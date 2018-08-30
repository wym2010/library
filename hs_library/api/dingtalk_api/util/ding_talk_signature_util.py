import hashlib
import hmac
import base64
import urllib

DEFAULT_ENCODING = 'UTF-8'
ALGORITHM = "HmacSHA256"
NEW_LINE = "\n"

class DingTalkSignatureUtil:


    def __init__(self):
        pass

    @staticmethod
    def get_canonical_string_for_isv(timestamp, suite_ticket=None):
        canonical_string = str(timestamp)
        if suite_ticket is not None:
            canonical_string += NEW_LINE + str(suite_ticket)
        return canonical_string

    @staticmethod
    def computer_signature(secret, canonical_string):

        secret = bytes(secret, encoding='utf-8')
        canonical_string = bytes(canonical_string, encoding='utf-8')
        print(secret, canonical_string)
        print(base64.b64encode(hmac.new(secret, canonical_string, digestmod='sha256').digest()))
        return str(base64.b64encode(hmac.new(secret, canonical_string, digestmod='sha256').digest()), encoding='utf-8')

    def param_to_query_string(self, *, param=None, charset='utf-8'):
        if not param:
            return None
        param_string = ''
        first = True
        for key, value in param.items():
            if not first:
                param_string += '&'
            param_string += self.url_encode(key, charset)
            if value is not None:

                param_string = param_string + '=' + self.url_encode(value, charset)

            first = False
        return param_string

    @staticmethod
    def url_encode(value=None, encoding='utf-8'):
        if value is None:
            return ''
        else:
            return urllib.parse.quote(value.encode(encoding), 'replace')
