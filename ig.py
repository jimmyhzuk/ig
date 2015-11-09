# encoding: utf-8
"""
    Wrapper for IG's REST Trading API
"""
__author__ = "Raul Catalina"
__version__ = '0.1.0'


import requests
from pprint import pprint as pp


class IG(object):
    """ """

    class InvalidOperationException(Exception): pass


    ALLOWED_OPERATIONS = ['get', 'put', 'post', 'delete']

    DEFAULT_CONTENT_TYPE = 'application/json'
    DEFAULT_ENCODING = 'utf-8'


    def _print(self, data):
        """ """
        for k, v in data.iteritems():
            print k, '=> ',
            pp(v)


    def __init__(self, base_url, identifier, password, api_key):
        """ 
        Constructor
        """
        self.__base_url = base_url
        self.__identifier = identifier
        self.__password = password
        self.__api_key = api_key
        self.__xst = None
        self.__cst = None
        self.__is_logged = False

        self.login()


    def __del__(self):
        """ 
        Destructor
        """
        self.logout()


    def getRequestHeaders(self, version=1, content_type=None, encoding=None):
        """ 
        Returns a dictionary of headers needed for the request

        Args:
            version: Optional. Number of the method version API the script will use
            content_type: Optional. Content-type header, by default "application/json"
            encoding: Optional. Encoding char-set, be default "utf-8"

        Returns:
            Dictionary of headers
        """
        if content_type is None:
            content_type = IG.DEFAULT_CONTENT_TYPE

        if encoding is None:
            encoding = IG.DEFAULT_ENCODING

        headers = {
            "Content-Type": "{0}; charset={1}".format(content_type, encoding),
            "Accept": "{0}; charset={1}".format(content_type, encoding),
            "X-IG-API-KEY": self.__api_key,
            "Version": version
        }

        if self.__xst is not None:
            headers['X-SECURITY-TOKEN'] = self.__xst

        if self.__cst is not None:
            headers['CST'] = self.__cst

        return headers


    def request(self, operation, method, params=None, version=1, content_type=None, encoding=None):
        """ 
        """
        if operation not in IG.ALLOWED_OPERATIONS:
            raise IG.InvalidOperationException(
                'Operation "{0}" is not allowed, please use one of "{1}"'.format(operation,
                                                                                 ', '.join(IG.ALLOWED_OPERATIONS))
            )

        url = '{0}/{1}'.format(self.__base_url, method)
        headers = self.getRequestHeaders(version=version, content_type=content_type, encoding=encoding)

        if operation == 'get':
            response = requests.get(url, params=params, headers=headers)

        elif operation == 'put':
            #response = requests.post(url, json=params, headers=headers)
            pass

        elif operation == 'post':
            response = requests.post(url, json=params, headers=headers)

        elif operation == 'delete':
            response = requests.delete(url, headers=headers)


        response.raise_for_status()

#        self._print(response.json())
#        self._print(response.headers)

        return response


    def login(self):
        """ 
        login the session
        """
        params = {
            'encryptedPassword': False,
            'identifier': self.__identifier,
            'password': self.__password,
        }

        response = self.request('post', 'session', params=params, version=2)

        self.__xst = response.headers['X-SECURITY-TOKEN']
        self.__cst = response.headers['CST']

        self.__is_logged = True


    def logout(self):
        """ 
        Logout the session
        """
        if self.__is_logged:
            self.request('delete', 'session')


    def getAccountsInfo(self):
        """ """
        reponse = self.request('get', 'accounts')
        return reponse.json()


    def getMarketCategories(self):
        """ """
        response = self.request('get', 'marketnavigation')

        #self._print(response.headers)

        return response.json()



