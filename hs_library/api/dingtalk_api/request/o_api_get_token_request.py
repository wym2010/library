from ..base_ding_talk_request import BaseDingTalkRequest
from ..constants import CALL_TYPE_OAPI


class OApiGetTokenRequest(BaseDingTalkRequest):
    _corp_id = ''
    _corp_secret = ''

    @property
    def corp_id(self, ):
        return self._corp_id

    @corp_id.setter
    def corp_id(self, corp_id):
        self._corp_id = corp_id

    @property
    def corp_secret(self):
        return self._corp_secret

    @corp_secret.setter
    def corp_secret(self, corp_secret):
        self._corp_secret = corp_secret

    def get_api_name(self):
        return 'dingtalk.oapi.gettoken'

    def get_api_call_type(self):
        return CALL_TYPE_OAPI

    def get_parameters(self):
        parameters = {'corpid': self.corp_id, 'corpsecret': self._corp_secret}
        if self._other_params is not None:
            parameters.update(self._other_params)
        return parameters

    def validate(self):
        pass


