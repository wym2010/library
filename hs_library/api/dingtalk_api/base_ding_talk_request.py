from .i_ding_talk_request import IDingTalkRequest
import six
import abc


@six.add_metaclass(abc.ABCMeta)
class BaseDingTalkRequest(IDingTalkRequest):
    _other_params = {}
    _header_params = {}
    _http_method = 'POST'

    def add_other_parameter(self, key, value):
        self._other_params[key] = value

    def add_header_parameter(self, key, value):
        self._header_params[key] = value

    def get_header_parameters(self):
        return self._header_params

    def set_http_method(self, http_method):
        self._http_method = http_method

    def get_http_method(self):
        return self._http_method

    @abc.abstractmethod
    def get_api_name(self):
        pass

    @abc.abstractmethod
    def get_api_call_type(self):
        pass

    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def get_parameters(self):
        pass

