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

    def send_msg(self, match_id, msg):
        try:
            url = Config.HOST + self.SEND_MSG_URL + match_id
            r = requests.post(url, headers=self.headers,
                              data=json.dumps({"message": msg}))
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not send your message:", e)

    def get_updates(self, last_activity_date=""):
        '''
        Returns all updates since the given activity date.
        The last activity date is defaulted at the beginning of time.
        Format for last_activity_date: "2017-07-09T10:28:13.392Z"
        '''
        try:
            url = Config.HOST + self.UPDATES_URL
            r = requests.post(url,
                              headers=self.headers,
                              data=json.dumps({"last_activity_date": last_activity_date}))
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong with getting updates:", e)

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

    def change_preferences(self, **kwargs):
        '''
        ex: change_preferences(age_filter_min=30, gender=0)
        kwargs: a dictionary - whose keys become separate keyword arguments and the values become values of these arguments
        age_filter_min: 18..46
        age_filter_max: 22..55
        age_filter_min <= age_filter_max - 4
        gender: 0 == seeking males, 1 == seeking females
        distance_filter: 1..100
        discoverable: true | false
        {"photo_optimizer_enabled":false}
        '''
        try:
            url = Config.HOST + self.CHANGE_PREFERENCES_URL
            r = requests.post(url, headers=self.headers, data=json.dumps(kwargs))
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not change your preferences:", e)

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

    def update_location(self, lat, lon):
        '''
        Updates your location to the given float inputs
        Note: Requires a passport / Tinder Plus
        '''
        try:
            url = Config.HOST + self.UPDATE_LOCATION_URL
            r = requests.post(url, headers=self.headers, data=json.dumps({"lat": lat, "lon": lon}))
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not update your location:", e)

    def reset_real_location(self):
        try:
            url = Config.HOST + self.RESET_REAL_LOCATION_URL
            r = requests.post(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not update your location:", e)

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

    def set_web_profile_username(self, username):
        '''
        Sets the username for the webprofile: https://www.gotinder.com/@YOURUSERNAME
        '''
        try:
            url = Config.HOST + self.SET_WEB_PROFILE_USERNAME_URL + username
            r = requests.put(url, headers=self.headers,
                             data=json.dumps({"username": username}))
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not set webprofile username:", e)

    def reset_web_profile_username(self, username):
        '''
        Resets the username for the webprofile
        '''
        try:
            url = Config.HOST + self.RESET_WEB_PROFILE_USERNAME_URL + username
            r = requests.delete(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not delete webprofile username:", e)

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

    def report(self, person_id, cause, explanation=''):
        '''
        There are three options for cause:
            0 : Other and requires an explanation
            1 : Feels like spam and no explanation
            4 : Inappropriate Photos and no explanation
        '''
        try:
            url = Config.HOST + self.REPORT_URL + person_id
            r = requests.post(url, headers=self.headers, data={
                "cause": cause, "text": explanation})
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not report:", e)

    def match_info(self, match_id):
        try:
            url = Config.HOST + self.MATCH_INFO_URL + match_id
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your match info:", e)

    def all_matches(self):
        try:
            url = Config.HOST + self.ALL_MATCHES_URL
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
            return count
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your fast-match count:", e)

    def trending_gifs(self, limit=3):
        try:
            url = Config.HOST + self.TRENDING_GIFS_URL + f'?limit={limit}'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get the trending gifs:", e)

    def gif_query(self, query, limit=3):
        try:
            url = Config.HOST + self.GIF_QUERY_URL + f'?limit={limit}&query={query}'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your gifs:", e)

    @staticmethod
    def check_response(response):
        if response.status_code != 200:
            raise Exception(f"Response code {response.status_code}."
                            f" Reason: {response.reason}."
                            f" Error: {response.text}")
