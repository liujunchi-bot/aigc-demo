import re
import time
import inspect
import json
import flask
import sys
import os
import base64
from PIL import Image
from io import BytesIO

import torch
import diffusers
import multiprocessing as mp

from service import cos

##################################################
# Utils

def retrieve_param(key, data, cast, default):
    if key in data:
        value = flask.request.form[ key ]
        value = cast( value )
        return value
    return default

def pil_to_b64(input):
    buffer = BytesIO()
    input.save( buffer, 'PNG' )
    output = base64.b64encode( buffer.getvalue() ).decode( 'utf-8' ).replace( '\n', '' )
    buffer.close()
    return output

def b64_to_pil(input):
    output = Image.open( BytesIO( base64.b64decode( input ) ) ).convert("RGB")
    output = output.resize((512, 512)).convert("RGB")
    return output

def get_compute_platform(context):
    try:
        import torch
        if torch.cuda.is_available():
            print('cuda')
            return 'cuda'
        elif torch.backends.mps.is_available() and context == 'engine':
            print('mps')
            return 'mps'
        else:
            print('cpu')
            return 'cpu'
    except ImportError:
        print('error')
        return 'cpu'

##################################################
# Engines

class Engine(object):
    def __init__(self):
        pass

    def process(self, kwargs):
        return []

class EngineStableDiffusion(Engine):
    def __init__(self, pipe, sibling=None, custom_model_path=None, requires_safety_checker=True):
        super().__init__()
        if sibling == None:
            self.engine = pipe.from_pretrained( '../disk1/stable-diffusion-2' )
        elif custom_model_path:
            if requires_safety_checker:
                self.engine = diffusers.StableDiffusionPipeline.from_pretrained(custom_model_path,
                                                                                safety_checker=sibling.engine.safety_checker,
                                                                                feature_extractor=sibling.engine.feature_extractor)
            else:
                self.engine = diffusers.StableDiffusionPipeline.from_pretrained(custom_model_path,
                                                                                feature_extractor=sibling.engine.feature_extractor)
        else:
            self.engine = pipe(
                vae=sibling.engine.vae,
                text_encoder=sibling.engine.text_encoder,
                tokenizer=sibling.engine.tokenizer,
                unet=sibling.engine.unet,
                scheduler=sibling.engine.scheduler,
                safety_checker=sibling.engine.safety_checker,
                feature_extractor=sibling.engine.feature_extractor
            )
        self.engine.to( get_compute_platform('engine') )

    def process(self, kwargs):
        output = self.engine( **kwargs )
        print(output)
        return {'images': output.images}

class EngineManager(object):
    def __init__(self):
        self.engines = {}

    def has_engine(self, name):
        return ( name in self.engines )

    def add_engine(self, name, engine):
        if self.has_engine( name ):
            return False
        self.engines[ name ] = engine
        return True

    def get_engine(self, name):
        if not self.has_engine( name ):
            return None
        engine = self.engines[ name ]
        return engine

##################################################
# App

# Load and parse the config file:
try:
    config_file = open ('config.json', 'r')
except:
    sys.exit('config.json not found.')

config = json.loads(config_file.read())

hf_token = config['hf_token']

if (hf_token == None):
    sys.exit('No Hugging Face token found in config.json.')

custom_models = config['custom_models'] if 'custom_models' in config else []

# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

# Initialize app:
app = flask.Flask( __name__ )

# Initialize engine manager:
manager = EngineManager()

# Add supported engines to manager:
manager.add_engine( 'txt2img', EngineStableDiffusion( diffusers.StableDiffusionPipeline,        sibling=None ) )
manager.add_engine( 'img2img', EngineStableDiffusion( diffusers.StableDiffusionImg2ImgPipeline, sibling=manager.get_engine( 'txt2img' ) ) )
manager.add_engine( 'masking', EngineStableDiffusion( diffusers.StableDiffusionInpaintPipeline, sibling=manager.get_engine( 'txt2img' ) ) )
for custom_model in custom_models:
    manager.add_engine( custom_model['url_path'],
                        EngineStableDiffusion( diffusers.StableDiffusionPipeline, sibling=manager.get_engine( 'txt2img' ),
                        custom_model_path=custom_model['model_path'],
                        requires_safety_checker=custom_model['requires_safety_checker'] ) )

# Define routes:
@app.route('/ping', methods=['GET'])
def stable_ping():
    return flask.jsonify( {'status':'success'} )

@app.route('/custom_models', methods=['GET'])
def stable_custom_models():
    if custom_models == None:
        return flask.jsonify( [] )
    else:
        return custom_models

@app.route('/txt2img', methods=['POST'])
def stable_txt2img():
    return _generate('txt2img')

@app.route('/img2img', methods=['POST'])
def stable_img2img():
    return _generate('img2img')

@app.route('/masking', methods=['POST'])
def stable_masking():
    return _generate('masking')

@app.route('/custom/<path:model>', methods=['POST'])
def stable_custom(model):
    return _generate('txt2img', model)

def _generate(task, engine=None):
    # Retrieve engine:
    if engine == None:
        engine = task

    engine = manager.get_engine( engine )

    # Prepare output container:
    output_data = {}

    # Handle request:
    try:
        seed = retrieve_param( 'seed', flask.request.form, int, 0 )
        count = retrieve_param( 'num_outputs', flask.request.form, int,   1 )
        total_results = []
        for i in range( count ):
            if (seed == 0):
                generator = torch.Generator( device=get_compute_platform('generator') )
            else:
                generator = torch.Generator( device=get_compute_platform('generator') ).manual_seed( seed )
            new_seed = generator.seed()
            prompt = flask.request.form[ 'prompt' ]
            args_dict = {
                'prompt' : [ prompt ],
                'num_inference_steps' : retrieve_param( 'num_inference_steps', flask.request.form, int,   100 ),
                'guidance_scale' : retrieve_param( 'guidance_scale', flask.request.form, float, 7.5 ),
                'eta' : retrieve_param( 'eta', flask.request.form, float, 0.0 ),
                'generator' : generator
            }
            if (task == 'txt2img'):
                args_dict[ 'width' ] = retrieve_param( 'width', flask.request.form, int,   512 )
                args_dict[ 'height' ] = retrieve_param( 'height', flask.request.form, int,   512 )
            if (task == 'img2img' or task == 'masking'):
                init_img_b64 = flask.request.form[ 'init_image' ]
                init_img_b64 = re.sub( '^data:image/.*;base64,', '', init_img_b64 )
                init_img_pil = b64_to_pil( init_img_b64 )
                print(type(init_img_pil))
                print(init_img_pil.format)
                # print(init_img_b64)
                print(type(init_img_b64))
                #init_img_pil = Image.open(BytesIO(init_img_b64)).resize((512,512))
                args_dict[ 'image' ] = init_img_pil
                args_dict[ 'strength' ] = retrieve_param( 'strength', flask.request.form, float, 0.7 )
            if (task == 'masking'):
                mask_img_b64 = flask.request.form[ 'mask_image' ]
                mask_img_b64 = re.sub( '^data:image/png;base64,', '', mask_img_b64 )
                mask_img_pil = b64_to_pil( mask_img_b64 )
                args_dict[ 'mask_image' ] = mask_img_pil
            # Perform inference:
            pipeline_output = engine.process( args_dict )
            pipeline_output[ 'seed' ] = new_seed
            total_results.append( pipeline_output )
        # Prepare response
        output_data[ 'status' ] = 'success'
        images = []
        for result in total_results:
            imgBase64 = pil_to_b64( result['images'][0].convert( 'RGB' ) )
            imgByte = base64.b64decode(imgBase64)
            url = cos.upload_to_cos(imgByte)
            aigcRes = {
                'image_url':url,
                'seed' : result['seed'],
                'mime_type': 'image/png'
            }
            images.append(aigcRes)
        output_data[ 'images' ] = images        
    except RuntimeError as e:
        output_data[ 'status' ] = 'failure'
        output_data[ 'message' ] = 'A RuntimeError occurred. You probably ran out of GPU memory. Check the server logs for more details.'
        print(str(e))
    return flask.jsonify( output_data )

if __name__ == '__main__':
    mp.set_start_method('spawn')
    app.run( host='0.0.0.0', port=1337, debug=False )
