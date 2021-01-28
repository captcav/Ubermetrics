# coding=utf-8
import os
import hashlib
import json
import urllib.parse
import urllib.request

class UbermetricsConn():
    def __init__(self, login:str, password:str):
        self.login = login
        self.password = password
        self.endPoint = os.getenv("UB_API_ENDPOINT")
        self.userId = None
        self.sessionId = None
        self.authTokens = []
    
    def __repr__(self):
        return '(' +  self.login + ' ; ' + self.password + ')'
    
    def search(self, params):
        authToken = self.getAuthToken()
        params["user_id"]=self.userId
        params["session_id"]=self.sessionId
        params["auth_token"]=authToken
        try:
            return self.get_query("/v2/mentions/", params)
        except urllib.error.URLError as e:
            raise Exception(e)
    
    def getAuthToken(self):
        if self.userId == None:
            self.connect()
        elif len(self.authTokens) == 1:
            self.renewTokens()
        return self.authTokens.pop()

    def connect(self):
        params = {
            "action" : "login_request",
            "user_name" : self.login,
        } 
        
        response = self.post_query(params)
        if response['success'] != 'true':
            raise Exception(response['error']['message'])

        data = response['data']
        user_id = data['user_id']
        user_seed = data['user_seed']
        auth_seed = data['auth_seed']
        md5Pass = hashlib.md5(self.password.encode())
        md5WithUser = hashlib.md5((md5Pass.hexdigest() + user_seed).encode())
        md5WithAuth = hashlib.md5((md5WithUser.hexdigest() + auth_seed).encode())
        
        self.userId = user_id
        self.newTokens(md5WithAuth.hexdigest())
    
    def newTokens(self, hash): 
        params = {
            "action" : "login",
            "user_id" : self.userId,
            "pass" : hash,
        }
        response = self.post_query(params)
        
        if response['success'] != 'true':
            raise Exception(response['error']['message'])

        data = response["data"]        
        self.sessionId= data['session_id']
        self.authTokens = data['auth_tokens']

    def renewTokens(self): 
        params = {
            "action" : "renew_session",
            "user_id" : self.userId,
            "session_id" : self.sessionId,
            "auth_token": self.authTokens.pop()
        }
        response = self.post_query(params)
        if response['success'] != 'true':
            raise Exception(response['error']['message'])

        data = response["data"]
        self.sessionId= data['session_id']
        self.authTokens = data['auth_tokens']

    def post_query(self, params):
        encoded_params = urllib.parse.urlencode(params)
        encoded_params = encoded_params.encode('ascii') # data should be bytes
        req = urllib.request.Request(self.endPoint, encoded_params)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())

    def get_query(self, relativeUrl, params):
        url = urllib.parse.urljoin(self.endPoint, relativeUrl)
        encoded_params = urllib.parse.urlencode(params)
        full_url = url + '?' + encoded_params
        response = urllib.request.urlopen(full_url)
        return json.loads(response.read())
