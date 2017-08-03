#coding:utf-8
#from django.test import TestCase

# Create your tests here.
import json
import requests
url = 'http://120.26.231.224:8000/addtask'
payload = {
    "action": "release",
    "data": [
        {
            "idc": "dev",
            "module_name": "bbtree-settingcenter-api",
            "war_version": "",
        },
        {
            "idc": "dev",
            "module_name": "bbtree-usercenter-web",
            "war_version": "",
        }
    ]
}
r = requests.post(url, data=json.dumps(payload))
print r.text
