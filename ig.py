# encoding: utf-8
"""
    Wrapper for IG's REST Trading API
"""
__author__ = "Raul Catalina"
__version__ = "0.1.0"


import requests
from pprint import pprint as pp


class IG(object):
    """ """

    class InvalidOperationException(Exception): pass
    class InvalidArgumentException(Exception): pass


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
            response = requests.put(url, data=params, headers=headers)

        elif operation == 'post':
            response = requests.post(url, json=params, headers=headers)

        elif operation == 'delete':
            response = requests.delete(url, headers=headers)


        response.raise_for_status()

#        self._print(response.json())
#        self._print(response.headers)

        return response


    ########################################################################
    #                                 Login
    ########################################################################

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
        #account_info = response.json()

        self.__xst = response.headers['X-SECURITY-TOKEN']
        self.__cst = response.headers['CST']

        self.__is_logged = True


    def logout(self):
        """ 
        Logout the session
        """
        if self.__is_logged:
            self.request('delete', 'session')


    def getEncryptionKey(self):
        """ """
        reponse = self.request('get', '/session/encryptionKey')
        return reponse.json()


    ########################################################################
    #                                Account
    ########################################################################
    # TODO: Implement the rest of methods

    def getAccounts(self):
        """ """
        reponse = self.request('get', 'accounts')
        return reponse.json()


    def getHistoryActivity(self, start_date=None, end_date=None, max_span_seconds=600,
                           page_size=20, page_number=1):
        """ """
        params = {
            'maxSpanSeconds': max_span_seconds,
            'pageSize': page_size,
            'pageNumber': page_number
        }

        if start_date is not None:
            params['from'] = start_date

        if end_date is not None:
            params['to'] = end_date

        reponse = self.request('get', 'history/activity', params=params, version=2)
        return reponse.json()


    def getHistoryTransactions(self, transaction_type='ALL', start_date=None, end_date=None,
                               max_span_seconds=600, page_size=20, page_number=1):
        """ 
        Transaction type: ALL (default), ALL_DEAL, DEPOSIT, WITHDRAWAL
        """
        params = {
            'type': transaction_type,
            'maxSpanSeconds': max_span_seconds,
            'pageSize': page_size,
            'pageNumber': page_number
        }

        if start_date is not None:
            params['from'] = start_date

        if end_date is not None:
            params['to'] = end_date

        reponse = self.request('get', 'history/transactions', params=params, version=2)
        return reponse.json()


    ########################################################################
    #                                Markets
    ########################################################################

    def getMarketCategories(self, node_id=None):
        """ 
        Returns all top-level nodes (market categories) in the market navigation hierarchy.
        
        Args:
            node_id: Optional. Node's ID
        """
        if node_id is None:
            response = self.request('get', 'marketnavigation')

        else:
            response = self.request('get', 'marketnavigation/{0}'.format(node_id))

        #self._print(response.headers)

        return response.json()


    def getMarketDetails(self, epic):
        """ 
        Returns the details of the given market
        
        Args:
            epic: Mandatory. String or List of strings with the epic of the market to be retrieved
        """
        epic_type = type(epic)

        if epic_type == type(str()):
            response = self.request('get', '/markets/{0}'.format(epic), version=3)

        elif epic_type == type(list()):
            response = self.request('get', '/markets?epics={0}'.format(','.join(epic)), version=2)

        else:
            raise IG.InvalidArgumentException(
                'Invalid type of argument "epic", it must be a string '
                'or a list of strings, {0} given'.format(epic_type.__name__)
            )

        return response.json()


    def findMarket(self, search_term):
        """
        Returns all markets matching the search term
        """
        response = self.request('get', '/markets?searchTerm={0}'.format(search_term))
        return response.json()


    ########################################################################
    #                                Dealing
    ########################################################################

    def getPositions(self):
        """ 
        Returns all open positions for the active account
        """
        response = self.request('get', '/positions', version=2)
        return response.json()


    ########################################################################
    #                                General
    ########################################################################

    def getApps(self):
        """ """
        response = self.request('get', '/operations/application')
        return response.json()


    def switchApp(self):
        """ """
        pass


    def disableCurrentApp(self):
        """ 
        TODO: Avoid logout() method crashes when disable the current APP
        """
        response = self.request('put', '/operations/application/disable')
        return response.json()


