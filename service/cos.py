from imp import reload

from service import client
import sys
import hashlib
from qcloud_cos.cos_threadpool import SimpleThreadPool

def getmd5(file):
    md5 = hashlib.md5(str(file).encode(encoding='utf-8'))
    md5 = md5.hexdigest()
    return md5

def upload_to_cos(file):
    #### 字节流简单上传
    key = getmd5(file)
    response = client.put_object(
        Bucket='20230312-1312414016',
        Body=file,
        Key=key,
        EnableMD5=False,
        ContentType='image/png; charset=utf-8'
    )
    url = client.get_object_url(
        Bucket='20230312-1312414016',
        Key=key
    )
    print(url)
    return url


def batch_put_file(files):
    pool = SimpleThreadPool()
    for file in files:
        key = getmd5(file)
        pool.add_task(client.put_object,Bucket='20230312-1312414016',Body=file,Key=key,EnableMD5=False)
    pool.wait_completion()
    result = pool.get_result()
    print(result)