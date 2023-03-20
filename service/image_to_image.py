import io
import warnings

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image

from service import stability_api
# Set up our initial generation parameters.
def image_to_image(prompt,img_byte):
    img = Image.open(io.BytesIO(img_byte))
    img = img.resize((512,512))
    imgRes = []
    answers2 = stability_api.generate(
        prompt=prompt,
        init_image=img, # Assign our previously generated img as our Initial Image for transformation.
        start_schedule=0.6, # Set the strength of our prompt in relation to our initial image.
        seed=123467458, # If attempting to transform an image that was previously generated with our API,
                        # initial images benefit from having their own distinct seed rather than using the seed of the original image generation.
        steps=30, # Amount of inference steps performed on image generation. Defaults to 30.
        cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
                   # Setting this value higher increases the strength in which it tries to match your prompt.
                   # Defaults to 7.0 if not specified.
        width=512, # Generation width, defaults to 512 if not included.
        height=512, # Generation height, defaults to 512 if not included.
        samples=1,  # Number of images to generate, defaults to 1 if not included.
        sampler=generation.SAMPLER_K_DPMPP_2M # Choose which sampler we want to denoise our generation with.
                                                 # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                 # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
)

# Set up our warning to print to the console if the adult content classifier is tripped.
# If adult content classifier is not tripped, display generated image.
    for resp in answers2:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                "Your request activated the API's safety filters and could not be processed."
                "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                global img2
                img2 = Image.open(io.BytesIO(artifact.binary))
                imgRes.append(img2)
                # img2.save("res/test3/"+str(artifact.seed)+ "-img2img.png") # Save our generated image with its seed number as the filename and the img2img suffix so that we know this is our transformed image.
    return imgRes