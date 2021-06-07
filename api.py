import datetime as dt
from sqlite3.dbapi2 import InterfaceError
import requests
import requests.auth as auth
from time import sleep
import settings as env


class RedditAPIManager:
    def __init__(self):
        self.__basic_header = {"User-Agent": env.USER_AGENT_STR}
        self.__remaining_requests = None
        self.__next_reset = None # Epoch time when number of remaining requests is reset
        self.__token = None
        self.__expiry = None     # Epoch time when token expires

    #@classmethod
    def get_token(self):
        if not self.__token:
            client_auth = auth.HTTPBasicAuth(env.REDDIT_ID, env.REDDIT_SECRET)
            data = {
                "grant_type": "password", 
                "username": env.USERNAME, 
                "password": env.PASSWD
            }
            response = requests.post(
                env.TOKEN_URL, 
                auth=client_auth, 
                data=data,
                headers=self.__basic_header
            )
            self.__token = response.json()["access_token"]
            age_limit = int(response.json()["expires_in"]) - 1
            self.__expiry = int(dt.datetime.now().timestamp()) + age_limit
        return (self.__token, self.__expiry)
    
    #@classmethod
    def set_token(self, token, expiry):
        if not isinstance(token, str) or not isinstance(expiry, int):
            raise InterfaceError("Improper argument type(s) given")
        self.__token = token
        self.__expiry = expiry
    
    #S@classmethod
    def get_posts(self):
        now = int(dt.datetime.now().timestamp())
        if now >= self.__expiry:
            self.get_token()
        if self.__remaining_requests == 0:
            sleep(self.__next_reset - now)

        headers = self.__basic_header
        headers["Authorization"] = "bearer %s" % self.__token
        response = requests.get(env.POSTS_URL, headers=headers)
        self.__remaining_requests = response.headers["x-ratelimit-remaining"]
        seconds_until_next_reset = int(response.headers["x-ratelimit-reset"])
        self.__next_reset = now + seconds_until_next_reset

        # See README.txt for response JSON structure
        return response.json()["data"]["children"]
