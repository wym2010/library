import six
import abc


@six.add_metaclass(abc.ABCMeta)
class IDingTalkClient(object):

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError


