#coding=utf-8

import sys
from django.core.mail import EmailMessage
from django.conf import settings
reload(sys)
sys.setdefaultencoding('utf8')


def request_get(url, timeout=5, headers=None):
    """
    发送get请求
    默认超时5秒
    默认http请求，如果https请求url中必须是https://开发
    headers = {'User-Agent': 'hhrtest'}
    ret, err = request_get('http://ip.taobao.com/service/getIpInfo.php?ip=122.88.60.28', headers=headers)
    if not err: print ret.text
    状态码：ret.status_code
    返回Unicode型的数据，如文本文件：ret.text
    返回bytes型也就是二进制的数据，如图片、文件等：ret.content
    返回json数据：ret.json()
    headers: ret.request.headers['User-Agent'] 
    直接获取返回json串内容 ret.json()['data']['country']
    """
    import re
    import requests
    ret = err = None
    requests.packages.urllib3.disable_warnings()
    if not re.match('https?://',url.strip()): url = 'http://' + url
    try:
        ret = requests.get(url, timeout=timeout, headers=headers)
    except Exception as e:
        return ret, e
    return ret, err

def request_post(url, post_data, timeout=5, headers=None):
    """
    发送post请求
    默认http请求，如果https请求url中必须是https://开发
    post_data = {'key1': 'value1', 'key2': 'value2'}
    ret, err = request_post('http://httpbin.org/post', post_data=post_data)
    if not err: print ret.text
    状态码：ret.status_code
    文本内容：ret.text
    headers: ret.request.headers['User-Agent'] 
    直接获取返回json串内容 ret.json()['data']['country']
    """
    import re
    import requests
    ret = err = None
    requests.packages.urllib3.disable_warnings()
    if not re.match('https?://',url.strip()): url = 'http://' + url
    try:
        ret = requests.post(url, post_data, timeout=timeout, headers=headers)
    except Exception as e:
        return ret, e
    return ret, err

def local_cmd(cmd):
    """
    返回退出状态码和执行输出结果（标准输出和错误输出）
    ret, err = local_cmd('date')

    """
    import commands
    err, ret = commands.getstatusoutput(cmd)
    return ret, err

def send_html_mail(tolist, subject, html_content, fromer=None, cclist=None, bcclist=None):
    '''
    发送html邮件
    '''
    if fromer: 
        _fromer = '%s<%s>' % (fromer, settings.EMAIL_HOST_USER)
    else:
        _fromer = settings.EMAIL_HOST_USER
    
    msg = EmailMessage(subject, html_content, _fromer, tolist)
    msg.content_subtype = "html"
    if cclist: msg.cc = cclist
    if bcclist: msg.bcc = bcclist
    ret = msg.send(fail_silently=True)
    if ret == 1:
        ret = True
    else:
        ret = False
    return ret

def make_password(length=8):
    '''
    生成随机密码
    '''
    from random import choice
    import string
    chars=string.ascii_letters+string.digits
    return ''.join([choice(chars) for i in range(length)])

def redis_set(key, value, ex=0, host='localhost', port=6379):
    '''
    写redis
    '''
    ret = err = None
    try:
        import redis
        r = redis.StrictRedis(host=host,port=port)
        ret = r.set(key, value, ex)
    except Exception as e:
        err = e
    return ret, err

def redis_get(key, host='localhost', port=6379):
    '''
    读redis
    '''
    ret = err = None
    try:
        import redis
    except Exception as e:
        return False, e
    try:
        r = redis.StrictRedis(host=host,port=port)
        ret = r.get(key)
    except Exception as e:
        err = e
    return ret, err
