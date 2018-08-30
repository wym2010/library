from urllib import request, parse
import json
a = 'https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid=dingoaakxvbgbuaei0kfs5&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=https://192.168.141.1:8000/api/v1/book'


class Auth(object):
    "The base implementation of a auth function."
    def __init__(self, *args, **kwargs):
        self.code = None
        self.access_token = None
        self.openid = None
        self.persistent_code = None
        self.sns_token = None
        self.user_info = None

        self.access_token_url = None
        self.persistent_code_url = None
        self.sns_token_url = None
        self.user_info_url = None
        print(kwargs)

        self.code = kwargs['code']
        self.access_token_url = kwargs['access_token_url']
        self.persistent_code_url = kwargs['persistent_code_url']
        self.sns_token_url = kwargs['sns_token_url']
        self.user_info_url = kwargs['user_info_url']
        self.appid = kwargs['appid']
        self.appsecret = kwargs['appsecret']

    def _get_access_token(self):
        with request.urlopen(self.access_token_url % (self.appid, self.appsecret)) as f:
            try:
                response = f.read().decode('utf-8')
                self.access_token = json.loads(response)['access_token']
            except Exception as e:
                print(e, json.loads(response)['errmsg'])

    def _get_persistent_code(self):
        data = json.dumps({
            'tmp_auth_code': self.code
        })
        req = request.Request(self.persistent_code_url % self.access_token)
        req.add_header('Content-type', 'application/json')
        with request.urlopen(req, data=data.encode('utf-8')) as f:
            try:
                response = f.read().decode('utf-8')
                self.persistent_code = json.loads(response)['persistent_code']
                self.openid = json.loads(response)['openid']
            except Exception as e:
                print(e, json.loads(response)['errmsg'])

    def _get_sns_token(self):
        data = json.dumps({
            'openid': self.openid,
            'persistent_code': self.persistent_code
        })
        req = request.Request(self.sns_token_url % self.access_token)
        req.add_header('Content-type', 'application/json')
        with request.urlopen(req, data=data.encode('utf-8')) as f:
            try:
                response = f.read().decode('utf-8')
                self.sns_token = json.loads(response)['sns_token']
            except Exception as e:
                print(e, json.loads(response)['errmsg'])

    def _get_user_info(self):
        with request.urlopen(self.user_info_url % self.sns_token) as f:
            try:
                response = f.read().decode('utf-8')
                self.user_info = json.loads(response)
            except Exception as e:
                print(e, json.loads(response)['errmsg'])

    def get_user_info(self):
        if self.user_info is None:
            self._get_access_token()
            self._get_persistent_code()
            self._get_sns_token()
            self._get_user_info()
        print(self.user_info)
        return self.user_info
