import os
import io
from stability_sdk import client

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'      # api host

os.environ['STABILITY_KEY'] = '*******'    ## your stabliliti api  key
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine='stable-diffusion-v1-5'
)

# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

# 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region 等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
tmp_secret_id = '****'     # 临时密钥的 SecretId，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
tmp_secret_key = '****'   # 临时密钥的 SecretKey，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
token = None                # 临时密钥的 Token，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
region = '****'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见https://cloud.tencent.com/document/product/436/6224
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=tmp_secret_id, SecretKey=tmp_secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
