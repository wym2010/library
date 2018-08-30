from ..base_ding_talk_request import BaseDingTalkRequest
from ..constants import CALL_TYPE_OAPI


class OApiSnsGetuserinfoBycodeRequest(BaseDingTalkRequest):
    _tmp_auth_code = ''

    @property
    def tmp_auth_code(self, ):
        return self._tmp_auth_code

    @tmp_auth_code.setter
    def tmp_auth_code(self, tmp_auth_code):
        self._tmp_auth_code = tmp_auth_code

    def get_api_name(self):
        return 'dingtalk.oapi.sns.getuserinfo_bycode'

    def get_api_call_type(self):
        return CALL_TYPE_OAPI

    def get_parameters(self):
        parameters = {'tmp_auth_code': self.tmp_auth_code}
        if self._other_params is not None:
            parameters.update(self._other_params)
        return parameters

    def validate(self):
        pass


