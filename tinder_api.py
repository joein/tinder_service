import json
import requests
from uuid import UUID

from config import Config


class TinderApi:
    AUTH_URL = '/auth'
    LIKE_URL = '/like/'
    DISLIKE_URL = '/pass/'
    RECOMMENDATIONS_URL = '/user/recs'
    RECOMMENDATIONS_V2_URL = '/v2/recs/core?locale=en-US'

    ALL_MATCHES_URL = '/v2/matches'
    CHANGE_PREFERENCES_URL = '/profile'
    FAST_MATCH_INFO_URL = '/v2/fast-match/preview'
    META_URL = '/meta'
    PERSON_URL = '/user/'
    SELF_URL = '/profile'
    UPDATES_URL = '/updates'
    GIF_QUERY_URL = '/giphy/search'
    MATCH_INFO_URL = '/matches/'
    REPORT_URL = '/report/'
    RESET_REAL_LOCATION_URL = '/passport/user/reset'
    RESET_WEB_PROFILE_USERNAME_URL = '/profile/'
    SEND_MSG_URL = '/user/matches/'
    SET_WEB_PROFILE_USERNAME_URL = '/profile/'
    SUPERLIKE_URL = LIKE_URL, '/super'
    TRENDING_GIFS_URL = '/giphy/trending'
    UPDATE_LOCATION_URL = '/passport/user/travel'

    def __init__(self, fb_access_token=None, fb_id=None, tinder_token=None):
        self.headers = {"content-type": "application/json"}
        if not tinder_token:
            self.get_auth_token(fb_access_token, fb_id)
        else:
            self.headers.update(self.valid_tinder_token(tinder_token))

    @staticmethod
    def valid_tinder_token(tinder_token):
        if isinstance(tinder_token, dict):
            if 'X-Auth-Token' in tinder_token:
                return tinder_token
        elif isinstance(tinder_token, str):
            try:
                UUID(tinder_token)
            except TypeError:
                raise Exception("Tinder token must be a valid UUID")

    def get_auth_token(self, fb_access_token, fb_id):
        url = Config.HOST + self.AUTH_URL
        req = requests.post(url,
                            headers=self.headers,
                            data=json.dumps({'facebook_token': fb_access_token, 'facebook_id': fb_id}))
        try:
            self.check_response(req)
            tinder_auth_token = req.json()["token"]
            self.headers.update({"X-Auth-Token": tinder_auth_token})

        except Exception as ex:
            print("Can't receive tinder auth token")
            raise ex

    def get_recommendations(self):
        '''
        Returns a list of users that you can swipe on
        '''
        try:
            r = requests.get(Config.HOST + self.RECOMMENDATIONS_URL, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong with getting recomendations:", e)

    def get_person(self, person_id):
        '''
        Gets a user's profile via their id
        '''
        try:
            url = Config.HOST + self.PERSON_URL + str(person_id)
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get that person:", e)

    def get_self(self):
        '''
        Returns your own profile data
        '''
        try:
            url = Config.HOST + self.SELF_URL
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your data:", e)

    def get_meta(self):
        '''
        Returns meta data on yourself. Including the following keys:
        ['globals', 'client_resources', 'versions', 'purchases',
        'status', 'groups', 'products', 'rating', 'tutorials',
        'travel', 'notifications', 'user']
        '''
        try:
            url = Config.HOST + self.META_URL
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your metadata:", e)

    def get_recs_v2(self):
        '''
        This works more consistently then the normal get_recommendations becuase it seeems to check new location
        '''
        try:
            url = Config.HOST + self.RECOMMENDATIONS_V2_URL
            r = requests.get(url, headers=self.headers)
            return r.json()
        except Exception as e:
            print('excepted')

    def superlike(self, person_id):
        try:
            like_url = self.SUPERLIKE_URL[0]
            super_url = self.SUPERLIKE_URL[1]
            url = Config.HOST + like_url + person_id + super_url
            r = requests.post(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not superlike:", e)

    def like(self, person_id):
        try:
            url = Config.HOST + self.LIKE_URL + person_id
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not like:", e)

    def dislike(self, person_id):
        try:
            url = Config.HOST + self.DISLIKE_URL + person_id
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not dislike:", e)

    def match_info(self, match_id):
        try:
            url = Config.HOST + self.MATCH_INFO_URL + match_id
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your match info:", e)

    def fast_match_info(self):
        try:
            url = Config.HOST + self.FAST_MATCH_INFO_URL
            r = requests.get(url, headers=self.headers)
            count = r.headers['fast-match-count']
            # image is in the response but its in hex..
            print(r.json())
            return count
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your fast-match count:", e)

    @staticmethod
    def check_response(response):
        if response.status_code != 200:
            raise Exception(f"Response code {response.status_code}."
                            f" Reason: {response.reason}."
                            f" Error: {response.text}")
