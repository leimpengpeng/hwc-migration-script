
import hmac, base64
import os
from hashlib import sha256


def hmac_sha256(key, data):
    appsecret = key.encode("utf-8")
    data = data.encode("utf-8")
    signature = base64.b64encode(hmac.new(appsecret, data, digestmod=sha256).digest())
    return signature


def mkdir(dir_nm):
    
    isExist = os.path.exists(dir_nm)
    if not isExist:
        os.makedirs(dir_nm)
    
    return