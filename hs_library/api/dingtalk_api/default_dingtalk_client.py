from .i_dingtalk_client import IDingTalkClient
from .constants import FORMAT_XML, CALL_TYPE_OAPI, FORMAT_JSON, CALL_TYPE_TOP
from datetime import datetime
from urllib import parse
from .util.ding_talk_signature_util import DingTalkSignatureUtil
import json
import requests


class DefaultDingTalkClient(IDingTalkClient):

    _server_url = None
    _format = FORMAT_XML
    _dt1970 = datetime(1970, 1, 1, 0, 0, 0, 0)
   # _web_utils = None
   # _i_top_logger = None
    _disable_parser = False
    _use_simplify_json = False
    _use_gzip_encoding = True
    _system_parameters = {}

    def __init__(self, *, server_url):
        self._server_url = server_url

    def execute(self, *, request=None, session=None, access_key=None, access_secret=None, suite_ticket=None, corp_id=None, timestamp=datetime.now().timestamp()*1000):

        if access_key is not None:
            if request.get_api_call_type() is None or request.get_api_call_type() == CALL_TYPE_TOP:
                return self.do_execute_top(request=request, timestamp=timestamp)
            else:
                return self.do_execute_o_api(request=request, access_key=access_key, access_secret=access_secret, suite_ticket=suite_ticket, corp_id=corp_id, timestamp=timestamp)

        if access_key is None:
            return self.do_execute(request=request, session=session, timestamp=timestamp)



    def do_execute(self, *, request, session, timestamp):
        if request.get_api_call_type() == CALL_TYPE_TOP or request.get_api_call_type() is None:
            return self.do_execute_top(request=request, session=session, timestamp=timestamp)
        else:
            return self.do_execute_o_api(request=request, session=session, timestamp=timestamp)

    def do_execute_top(self, *, request=None, session=None, timestamp=None):
        start = datetime.now()
        try:
            request.validate()
        except ValueError as e:
            return self.create_error_response(e)
        except AttributeError as e:
            return self.create_error_response(e)

        txt_params = request.get_parameters()
        txt_params['method'] = request.get_api_name
        txt_params['v'] = '2.0'
        txt_params['format'] = self._format
        txt_params['partner_id'] = self._get_sdk_version()
        txt_params['timestamp'] = round(timestamp)
        txt_params['session'] = session
        txt_params.update(self._system_parameters)

        if self._use_simplify_json:
            txt_params['simplify'] = 'true'
        if self._use_gzip_encoding:
            request.add_header_parameter('Accept-Encoding', 'gzip')
        real_server_url = self.get_server_url(self._server_url, request.get_api_name(), session)
        try:
            r=requests.post(url=real_server_url, data=txt_params)
        except Exception as e:
            print(e)
        return r.text

    def do_execute_o_api(self, *, request=None, session=None, access_key=None, access_secret=None, suite_ticket=None, corp_id=None, timestamp=None):
        try:
            request.validate()
        except ValueError as e:
            return self.create_error_response(e)
        except AttributeError as e:
            return self.create_error_response(e)

        self._format = FORMAT_JSON
        txt_params = {'access_token': session}
        if self._use_gzip_encoding:
            request.add_header_parameter('Accept-Encoding', 'gzip')
        if access_key is not None:
            ding_time_stamp = str(round(datetime.now().timestamp()*1000))
            canonical_string = DingTalkSignatureUtil.get_canonical_string_for_isv(ding_time_stamp, suite_ticket)
            signature = DingTalkSignatureUtil.computer_signature(access_secret, canonical_string=canonical_string)
            ps = {'accessKey': access_key, 'signature': signature, 'timestamp': ding_time_stamp+''}
            print(ps)
            if suite_ticket is not None:
                ps['suiteTicket'] = suite_ticket
            if corp_id is not None:
                ps['corpId'] = corp_id
            query_str = parse.urlencode(ps)
            if self._server_url.find('?') > -1:
                real_server_url = self._server_url + '&' + query_str
            else:
                real_server_url = self._server_url + '?' + query_str
        else:
            if self._server_url.find('?') > -1:
                real_server_url = self._server_url + ('&access_token=' + session if session is not None and session !='' else '')
            else:
                real_server_url = self._server_url + ('?access_token=' + session if session is not None and session !='' else '')

        try:
            if request.get_http_method() == 'POST':
                json_params = {}
                for key, value in request.get_parameters().items():
                    if (value.startswith('[') and value.endswith(']')) or (value.startswith('{') and value.endswith('}')):
                        json_params[key] = json.loads(value)
                    else:
                        json_params[key] = value
                print(real_server_url, json_params)
                json_params = json.dumps(json_params)
                r = requests.post(url=real_server_url, data=json_params,)
            else:
                r = requests.get(url=real_server_url, params=request.get_parameters())

        except Exception as e:
            print(e)
        return r.text


    @staticmethod
    def _get_sdk_version():
        return 2.0

    def get_server_url(self, _server_url, api_name, session):
        return _server_url


IDingTalkClient.register(DefaultDingTalkClient)