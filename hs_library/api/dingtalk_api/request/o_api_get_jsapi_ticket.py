from ..base_ding_talk_request import BaseDingTalkRequest
from ..constants import CALL_TYPE_OAPI


class OApiGetJsapiTicketRequest(BaseDingTalkRequest):

    @staticmethod
    def get_api_name(self):
        return 'dingtalk.oapi.get_jsapi_ticket'

    @staticmethod
    def get_api_call_type(self):
        return CALL_TYPE_OAPI

    def get_parameters(self):
        parameters = {'userid': self.user_id}
        if self._other_params is not None:
            parameters = parameters.copy().update(self._other_params)
        return parameters

    def validate(self):
        pass

