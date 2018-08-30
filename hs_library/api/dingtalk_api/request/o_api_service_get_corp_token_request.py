from ..constants import CALL_TYPE_OAPI
from ..base_ding_talk_request import BaseDingTalkRequest


class OApiServiceGetCorpTokenRequest(BaseDingTalkRequest):
    _auth_corp_id = None
    _permanent_code = None

    @property
    def auth_corp_id(self,):
        return self._auth_corp_id

    @auth_corp_id.setter
    def auth_corp_id(self, corp_id):
        self._auth_corp_id = corp_id

    @property
    def permanent_code(self):
        return self._permanent_code

    @permanent_code.setter
    def permanent_code(self, permanent_code):
        self._permanent_code = permanent_code

    def get_api_name(self):
        return 'dingtalk.oapi.service.get_corp_token'

    def get_api_call_type(self):
        return CALL_TYPE_OAPI

    def get_parameters(self):
        parameters = {'auth_corpid': self._auth_corp_id}
        if self.permanent_code:
            parameters['permanent_code'] = self.permanent_code
        if self.other_params is not None:
            parameters.update(self.other_params)
        return parameters

    def validate(self):
        pass


BaseDingTalkRequest.register(OApiServiceGetCorpTokenRequest)
