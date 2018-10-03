from pymongo import MongoClient


class Connection:
    def __init__(self, ip='127.0.0.1', port=27017):
        self.ip = ip
        self.port = port
        self.connection = self.connection(self.ip, self.port)

    @staticmethod
    def connection(ip, port):
        return MongoClient(ip, port)

    @property
    def tinder_db(self):
        return self.connection.tinder

    def write_recommendations(self, recs):
        if recs:
            self.tinder_db.meetings.insert_many(recs)

    def write_matches(self, matches):
        if matches:
            self.tinder_db.matches.insert_many(matches)

    def __del__(self):
        self.connection.close()
