import logging
from datetime import datetime

from tinder_api import TinderApi
from facebook_tools import FacebookTools
from db import Connection
from config import Config


logging.basicConfig(format=u'%(filename)s # %(levelname)s # [%(asctime)s]  %(message)s', level=logging.INFO)


class TinderService:
    def __init__(self, fb_token=None, fb_id=None, tinder_token=None):
        if tinder_token:
            self._api = TinderApi(tinder_token=tinder_token)
        else:
            self._facebook_data = FacebookTools(access_token=fb_token, fb_id=fb_id)
            self._api = TinderApi(self._facebook_data.access_token, self._facebook_data.facebook_id)

        self._db = Connection(Config.DB_IP, Config.DB_PORT)

    @property
    def api(self):
        return self._api

    @property
    def storage(self):
        return self._db

    def like(self, limit=None):
        person_keys = 'birth_date', 'name', 'photos', 'url', 'photos', 'instagram', 'connection_count', \
                      'birth_date_info', 'teaser', 'distance_mi', 's_number'
        match_keys = 'created_date', 'last_activity_date', 'participants'

        likes_remaining = True
        person_info, match_info = [], []

        while likes_remaining:
            recs = self.api.get_recommendations()
            data_collection_date = datetime.utcnow()

            if not limit:
                recs_part = recs['results']
            elif limit > 0:
                recs_part = recs['results'][:limit]
            else:
                likes_remaining = False
                recs_part = []

            for rec in recs_part:
                if limit:
                    limit -= 1

                person_id = rec.get('_id', None)
                if not person_id:
                    continue

                result = self.api.like(person_id)

                if 'match' in result and 'likes_remaining' in result:
                    match = result['match']
                    likes_remaining_code = result['likes_remaining']
                    if likes_remaining_code == 0:
                        logging.info('LIKES REMAINING: 0')
                else:
                    logging.info(f'invalid tinder response {result}')
                    continue

                if likes_remaining_code != 0:
                    current_person_info = dict(record_date=data_collection_date, owner_id=person_id)
                    current_person_info.update({key: rec[key] for key in person_keys if key in rec})
                    person_info.append(current_person_info)

                likes_remaining = True if likes_remaining_code != 0 and limit != 0 else False

                if not match and not likes_remaining:
                    break

                if not match:
                    continue

                match_id = match.get('_id', None)
                if not match_id:
                    continue
                logging.info(f'MEETS---------: {person_id}')
                logging.info(f'MATCH---------: {match_id}')
                owner_id = match['participants'][0]
                match_info.append(dict(match_id=match_id, record_date=data_collection_date, owner_id=owner_id))
                match_info[-1].update({key: match[key] for key in match_keys if key in match})

                if not likes_remaining:
                    break

        uniq_person_info = self.get_uniq_records(person_info)
        uniq_match_info = self.get_uniq_records(match_info)

        logging.info(f'MEETS: {len(uniq_person_info)}')
        logging.info(f'MATCHES: {len(uniq_match_info)}')
        self.storage.write_recommendations(uniq_person_info)
        self.storage.write_matches(uniq_match_info)

    @staticmethod
    def get_uniq_records(records):
        uniq_records = []
        records = iter(records)
        while records:
            try:
                record = next(records)
                if record not in uniq_records:
                    uniq_records.append(record)
            except StopIteration:
                records = None
        return uniq_records

    def get_person(self, person_id):
        self.api.get_person(person_id)


if __name__ == '__main__':
    service_instance = TinderService()
    service_instance.like()
