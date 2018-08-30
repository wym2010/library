import six
import abc


@six.add_metaclass(abc.ABCMeta)
class IDingTalkRequest(object):

    @abc.abstractmethod
    def get_api_name(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_api_call_type(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_parameters(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_header_parameters(self):
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_http_method(self):
        raise NotImplementedError

