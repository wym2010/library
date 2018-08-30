from ..base_ding_talk_request import BaseDingTalkRequest
from ..constants import CALL_TYPE_OAPI

class OApiUserGetRequest(BaseDingTalkRequest):
    _user_id = None

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        if not isinstance(user_id, str):
            raise TypeError('User id is a string!')
        else:
            self._user_id = user_id

    @staticmethod
    def get_api_name(self):
        return 'dingtalk.oapi.user.get'

    @staticmethod
    def get_api_call_type():
        return CALL_TYPE_OAPI

    def get_parameters(self):
        parameters = {'userid': self.user_id}
        if self._other_params is not None:
            parameters = parameters.copy().update(self._other_params)
        return parameters

    def validate(self):
        if self.user_id is not None:
            raise ValueError('user_id is not provided!')


