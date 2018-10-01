from tinder_api import TinderApi
from facebook_tools import FacebookTools


class TinderLiker:
    def __init__(self, fb_token=None, fb_id=None, tinder_token=None):
        if tinder_token:
            self._api = TinderApi(tinder_token=tinder_token)
        else:
            self._facebook_data = FacebookTools(access_token=fb_token, fb_id=fb_id)
            self._api = TinderApi(self._facebook_data.access_token, self._facebook_data.facebook_id)

    @property
    def api(self):
        return self._api

    def start(self):
        recs = self.api.get_recommendations()
        person_info = []
        interest_keys = '_id', 'birth_date', 'name', 'photos', 'url', 'photos', 'instagram', 'connection_count', \
                        'birth_date_info', 'teaser', 'distance_mi', 's_number'
        # match_keys = '_id', 'created_date', 'last_activity_date'
        for rec in recs['results']:
            person_id = rec['_id']
            person_info.append({key: rec[key] for key in interest_keys if key in rec})
            result = self.api.like(person_id)
            print(result)
            # match_id = my_id + her_id
            person_info[-1].update({'match_id': result.get('_id', None),
                                    'match_created_date': result.get('created_date', None),
                                    'match_last_activity_date': result.get('last_activity_date', None),
                                    'participants': result.get('participants', None)
                                    })
            raise Exception(result['likes_remaining'])


