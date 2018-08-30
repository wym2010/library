from library.hs_library.api.dingtalk_api.default_dingtalk_client import DefaultDingTalkClient
from library.hs_library.api.dingtalk_api.request.o_api_get_token_request import OApiGetTokenRequest
from library.hs_library.api.dingtalk_api.request.o_api_sns_getuserinfo_bycode_request import OApiSnsGetuserinfoBycodeRequest
from library.hs_library.settings import DingTalk_args as dd

def main():
    gettoken_client = DefaultDingTalkClient(server_url='https://oapi.dingtalk.com/gettoken')
    req = OApiGetTokenRequest()
    req.corp_id = 'ding5a354717bb1411a835c2f4657eb6378f'
    req.corp_secret = 'YgmnhFATTp4ZKRF0sDw5Oxic7YbBePGSdG7WWb7b7FiOL5-RbsP26G9RGOfKM7M8'
    req.set_http_method('GET')
    print(gettoken_client.execute(request=req))

    # userinfo_client = DefaultDingTalkClient(server_url=dd['getUserinfoUrl'])
    # req = OApiSnsGetuserinfoBycodeRequest()
    # req.tmp_auth_code = 'afsdf'
    # print(userinfo_client.execute(request=req, access_key=dd['appId'], access_secret=dd['appSecret']))


if __name__ == '__main__':
    main()



