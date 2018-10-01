import re
import requests
import robobrowser


from config import Config


class FacebookTools:
    FB_AUTH_URL = """https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&
    display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220
    _auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C
    %223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail
    %2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request
    &default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios
    &logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"""

    def __init__(self, email=Config.EMAIL, password=Config.PASSWORD, access_token=None, fb_id=None):
        self._email = email
        self._password = password
        if not access_token:
            self.get_fb_access_token()
        if not fb_id:
            self.get_fb_id()

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @property
    def access_token(self):
        return self._access_token

    @property
    def facebook_id(self):
        return self._facebook_id

    def _set_access_token(self, access_token):
        self._access_token = access_token

    def _set_facebook_id(self, fb_id):
        self._facebook_id = fb_id

    def get_fb_access_token(self):
        browser = robobrowser.RoboBrowser(parser="lxml")
        browser.open(self.FB_AUTH_URL)
        auth_form = browser.get_form()
        auth_form["email"] = self.email
        auth_form["pass"] = self.password

        browser.submit_form(auth_form)
        tinder_form = browser.get_form()
        try:
            browser.submit_form(tinder_form, submit=tinder_form.submit_fields['__CONFIRM__'])
            access_token = re.search(
                r"access_token=([\w\d]+)", browser.response.content.decode()).groups()[0]
            self.check_access_token(access_token)
            self._set_access_token(access_token)
        except Exception as ex:
            print(f"Access token could not be retrieved. Check your username and password. {ex}")

    def get_fb_id(self):
        self.check_access_token(self.access_token)

        response = requests.get('https://graph.facebook.com/me?access_token=' + self.access_token)
        self.check_response(response)
        json_response = response.json()

        self._set_facebook_id(json_response["id"])

    @staticmethod
    def check_access_token(access_token):
        if not access_token:
            raise Exception(f"Access token is {access_token}")

        if "error" in access_token:
            raise Exception(f"Facebook raw error: {access_token['error']}")

    @staticmethod
    def check_response(response):
        if response.status_code != 200:
            raise Exception(f"Response code {response.status_code}. Reason: {response.reason}. Error: {response.text}")
        if "id" not in response.json():
            raise Exception("There is no ID field in response")

