import json
import logging
import time
from collections import defaultdict

import tweepy
from shapely.geometry import Point, Polygon, LineString
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import GeoProcessor
import SentimentAnalysis
import TwitterCredentialsPA as twit
from CouchdbCredentials import couchserver


class TwitterStreamer():
    def __init__(self):
        pass

    def stream_tweets(self, dictionaries, area_box):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = StdOutListener(dictionaries)
        auth = OAuthHandler(twit.consumer_api_key, twit.consumer_api_secret)
        auth.set_access_token(twit.access_token, twit.access_secret)
        api = tweepy.API(auth)
        api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=3, retry_delay=5,
                         retry_errors=set([401, 404, 500, 503]))
        stream = Stream(auth, listener)
        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(locations=area_box)


class StdOutListener(StreamListener):

    def __init__(self, dictionaries):
        self.dictionaries = dictionaries

    def on_data(self, data):
        try:
            x = json.loads(data)

            # Setting up DB Connection
            if dbname in couchserver:
                db = couchserver[dbname]
            else:
                db = couchserver.create(dbname)

            # Setting Unique key
            x['_id'] = str(x['id_str'])

            # Sentiment Analysis Module
            sentiment = SentimentAnalysis.sentiment_score(str(x['text']))
            # print(x['text'])
            if str(data).__contains__('extended_tweet": {'):
                sentiment = (SentimentAnalysis.sentiment_score(str(x['extended_tweet']['full_text'])))
            # print(sentiment)
            x['sentiment'] = sentiment

            # Geo-analysis module
            area_details = [None, None]

            if x['coordinates'] is None and x['place']['bounding_box'] is not None:
                box_coordinate_list = x['place']['bounding_box']['coordinates']
                area_details = GeoProcessor.find_bounding_box_area(dictionaries[0], dictionaries[1], box_coordinate_list)

            if x['coordinates'] is not None:
                coordinates = Point(x['coordinates']['coordinates'])
                area_details = GeoProcessor.find_point_area(dictionaries[0], dictionaries[1], coordinates)

            if area_details[0] is not None and area_details[1] is not None:
                x['SA3_Code'] = area_details[0]
                x['SA3_Name'] = area_details[1]

            # Saving changes to couchdb
            db.save(x)
            return True
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
            logging.debug('Rate Limit Exceeded at ', time.time())
        except BaseException as e:
            logging.debug('Error on_data', e, 'at', time.time())
        return True

    def on_error(self, status):
        print(status)


def load_grid(location_area_file):
    polygon_dictionary = {}
    line_dictionary = {}
    with open(location_area_file, 'r') as f:
        location_json = json.load(f)
        for item in range(len(location_json['features'])):
            SA3_CODE = location_json['features'][item]['properties']['feature_code']
            SA3_NAME = location_json['features'][item]['properties']['feature_name']
            # print(SA3_CODE, SA3_NAME)
            multi_polygon = location_json['features'][item]['geometry']['coordinates']
            counter = 0
            l2_lin_dictionary = defaultdict(int)
            l2_pol_dictionary = defaultdict(int)
            for pol_doc in multi_polygon:
                # Inside Features - Geometry - Coordinates - Item - Polygon Item
                if len(pol_doc) == 1:
                    for sub_polygon in pol_doc:
                        # Inside Point coordinate layer of every multipolygon
                        # Points comprising the polygon, Right time to make polygon
                        l2_pol_dictionary[counter] = Polygon(sub_polygon)
                        sub_polygon2 = []
                        sub_polygon2 = sub_polygon
                        sub_polygon2.append(sub_polygon[0])
                        l2_lin_dictionary[counter] = LineString(sub_polygon2)
                        counter += 1
            polygon_dictionary[SA3_CODE + ',' + SA3_NAME] = l2_pol_dictionary
            line_dictionary[SA3_CODE + ',' + SA3_NAME] = l2_lin_dictionary
    return [polygon_dictionary, line_dictionary]


if __name__ == '__main__':
    # Setting up logging
    LOG_FILENAME = '/home/ubuntu/harvester/log/adelaide_logger.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(message)s')

    CITY_GRID_FILENAME = '/home/ubuntu/harvester/Aurin_JSON/adelaide.json'
    dictionaries = load_grid(CITY_GRID_FILENAME)

    adelaide_area_box = [138.4421299,-35.3489699,138.9634089955,-34.652564]
    dbname = 'adelaide'

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(dictionaries, adelaide_area_box)
