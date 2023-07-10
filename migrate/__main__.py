import click
from fileinput import filename
import sys, json, requests
import urllib.parse

import time
import hmac, xmltodict
from apig_sdk import signer
from util import * 
from ftplib import FTP
from obs import *
from dotenv import load_dotenv
import os
load_dotenv()

AK = os.getenv('DNT_AK')
SK = os.getenv('DNT_SK')
# OMS_GROUPS_ENDPOINT = "https://oms.{SG_REGION}.myhuaweicloud.com/v2/{}/taskgroups"


# SGOBSClient = ObsClient(access_key_id=AK, secret_access_key=SK, server=OBS_ENDPOINT)

Basepath = "/116476"
BasepathLen = len(Basepath)

FolderSet = set()
src_bucket = "src"

def addFolder(path):
    FolderSet.add(path[BasepathLen:])

@click.group()
def cli():
    pass

@cli.command(name='generate_url_list')
def generate_url_list_from_akamai():
    domain = os.getenv('DOMAIN')
    domain_url = os.getenv('DOMAIN_URL')
    basepath = os.getenv('basepath')
    path =  os.getenv('path')
    number_of_task = int(os.getenv('number_of_task'))
    url = f"{domain_url}/{basepath}/{path}"
    auth_key = os.getenv('DOMAIN_AUTH_KEY')
    
    auth_data = f"5, 0.0.0.0, 0.0.0.0, {int(time.time())}, 20220915, houyong_secure"
    sign_string = f"/{basepath}/{path}\nx-akamai-acs-action:version=1&action=list\n"

    headers = {"Accept": "application/xml",
        "X-Akamai-ACS-Action": "version=1&action=list",
        "X-Akamai-ACS-Auth-Data": auth_data,
        "X-Akamai-ACS-Auth-Sign": hmac_sha256(auth_key, auth_data + sign_string),
        "Host": "garena-nsu.akamaihd.net"}

   
    response = requests.get(url, headers=headers)
    xpars = xmltodict.parse(response.text)
    
    mkdir("key_list")
    for i in xpars["list"]["file"]:
        n = 0
        if not i["@name"].startswith(f"{basepath}/{path}/"):
            continue
            
        if i["@type"] == "dir":
            continue
        if i["@type"] == "file" and ("116476/test/" in i["@name"]):
            # print(i["@name"])
            filename = i["@name"] 
            subfile= filename.removeprefix("116476/test/")
            w_str = urllib.parse.quote(urllib.parse.quote(subfile))
            while n < number_of_task:
                file_object = open(f'key_list/url_list_{n}.txt', 'a', encoding='utf-8')
                file_object.write(f"http://{domain}/{w_str}\ttest/{subfile}\n")
                n = n + 1


@cli.command(name='oms_tasks')
@click.argument("region")
def createOMSTask(region):
    if(region == "ap-southeast-3"):
        project_id = os.getenv('SG_PROJECT_ID')
        dnt_bucket = os.getenv('DNT_SG_BUCKET')
    if(region == "cn-east-3"):
        project_id = os.getenv('SH_PROJECT_ID')
        dnt_bucket = os.getenv('DNT_SH_BUCKET')
    
    #request = signer.HttpRequest('POST', OMS_ENDPOINT.format(project_id))
    OMS_GROUPS_ENDPOINT = "https://oms.{}.myhuaweicloud.com/v2/{}/taskgroups"
    request = signer.HttpRequest('POST', OMS_GROUPS_ENDPOINT.format(region, project_id))
    request.headers = {
        'X-Project-Id': project_id,
        'Content-Type': 'application/json;charset=utf8'
    }
    from obs import PutObjectHeader, CreateBucketHeader
    createBucketHeader = CreateBucketHeader()
    
    createBucketHeader.aclControl ="PUBLIC_READ_DELIVERED"
    OBS_ENDPOINT = f"https://obs.{region}.myhuaweicloud.com"
    OBSClient = ObsClient(access_key_id=AK, secret_access_key=SK, server=OBS_ENDPOINT)
    OBSClient.createBucket(dnt_bucket, location=region, header=createBucketHeader)

    request.body = json.dumps({
        "src_node": {
            "cloud_type": "URLSource",
            "list_file": {
                "obs_bucket": "src-url-lists",
                "list_file_key": "key_list/"
            }
        },
        "description": "TEST_migration",
        "dst_node": {
            "region": region,
            "ak": AK,
            "sk": SK,
            "bucket": dnt_bucket,
            "cloud_type": "HEC",
        },
        "enable_failed_object_recording": True,
        "enable_restore": False,
        "enable_metadata_migration" : False,
        "enable_kms": False,
        "task_type": "URL_LIST"
    })
    print(request.body)
    sig.Sign(request)

    response = requests.request(
		request.method,
		request.scheme + "://" + request.host + request.uri,
		headers=request.headers,
		data=request.body)
    print(response.json())
    return response


@cli.command(name='upload_urls_obj')
def uploadUrlsObj():
    url_lists_obj= os.getenv('URL_LISTS_OBJ')
    src_bucket = os.getenv('URL_LISTS_SRC_BUCKET')
    region = "ap-southeast-3"
    try:
        from obs import PutObjectHeader, CreateBucketHeader
        createBucketHeader = CreateBucketHeader()
        createBucketHeader.aclControl ="PUBLIC_READ_DELIVERED"
        OBS_ENDPOINT = f"https://obs.{region}.myhuaweicloud.com"
        OBSClient = ObsClient(access_key_id=AK, secret_access_key=SK, server=OBS_ENDPOINT)
        OBSClient.createBucket(src_bucket, location=region, header=createBucketHeader)
        
        headers = PutObjectHeader()
        headers.contentType = 'text/plain'
        for file in os.listdir(url_lists_obj):
            fileitem = f"{url_lists_obj}/{file}"
            resp_putFile = OBSClient.putFile(src_bucket, fileitem, fileitem, headers=headers)
    except:
        import traceback
        print(traceback.format_exc())


sig = signer.Signer()
sig.Key = AK
sig.Secret = SK

cli(prog_name='migrate')
