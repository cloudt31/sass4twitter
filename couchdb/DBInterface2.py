#!/usr/bin/python3
import couchdb
import time
from datetime import datetime
from pytz import timezone
import operator
from collections import Counter

def main():
  d = datetime.now(timezone("utc"))
  temp=d.strftime('%a %b %d %H:%M:%S %z %Y')
  user = "admin"
  password = "cloudt3118"
  couchserver1 = couchdb.Server("http://%s:%s@localhost:9000/" % (user, password))

  fname = 'canberr.txt'
  # creating database
  dbname = "canberra"
  db = couchserver1[dbname]
  bb_query = {
    "selector": {
      "$and": [
        {"SA3_Name": {"$ne": None}},
        {"user.followers_count": {"$exists": True}},
        {"created_at": {"$regex": "May " + '0[3-9]'}},
        {"coordinates": {"$eq": None}},
        {"place.bounding_box": {"$exists": True}},
      ]
    },
    "sort": [{"SA3_Name": "desc"},{"user.followers_count":"desc"}],
    "limit": 80000,
    "use_index": 'bounding_box_index',
    "fields": [
      "SA3_Name",
      "user.followers_count",
      "created_at",
      "entities.hashtags",
      "user.name",
      "text",
      "SA3_Code",
      "sentiment",
      "place.bounding_box"
    ]
  }

  coords_query = {
    "selector": {
      "$and": [
        {"SA3_Name": {"$ne": None}},
        {"user.followers_count": {"$exists": True}},
        {"created_at": {"$regex": "May "+'0[3-9]'}},
        {"coordinates": {"$ne": None}}]
    },
    "sort": [{"SA3_Name": "desc"}, {"user.followers_count": "desc"}],
    "limit": 80000,
    "use_index": 'coord_index',
    "fields": [
      "SA3_Name",
      "user.followers_count",
      "created_at",
      "entities.hashtags",
      "user.name",
      "text",
      "SA3_Code",
      "sentiment",
      "coordinates.coordinates"
    ]
  }


  k=1
  start_time = time.time()
  _,_,bb_data = db.resource.post_json('_find',body = bb_query, headers={'Content-Type': 'application/json'})
  _,_,coords_data = db.resource.post_json('_find',body = coords_query, headers={'Content-Type': 'application/json'})
  bb_docs=bb_data['docs']
  coords_docs=coords_data['docs']
  x=(time.time() - start_time)
  long_list = []
  lat_list = []
  senti_list=[]
  sa3_list=[]
  followers_list=[]
  username_list=[]
  tweet_list=[]
  hashtags_list=[]
  date_list=[]
  k=0
  for i in bb_docs:
    loc_bounding_box = i['place']['bounding_box']['coordinates']  # for bounding box
    mid_longitude = (loc_bounding_box[0][0][0] + loc_bounding_box[0][2][0]) / 2
    mid_latitude = (loc_bounding_box[0][0][1] + loc_bounding_box[0][1][1]) / 2
    long_list.append(mid_longitude)
    lat_list.append(mid_latitude)
    senti_list.append(i['sentiment'])
    sa3_temp=[]
    sa3_temp.append(i['SA3_Name'])
    sa3_temp.append(i['SA3_Code'])
    sa3_list.append(sa3_temp)
    followers_list.append(i['user']['followers_count'])
    username_list.append(i['user']['name'])
    tweet_list.append(i['text'])
    hashtags_list.append(i['entities']['hashtags'])
    date_list.append(i['created_at'])
    k+=1
  for j in coords_docs:
    long_list.append(j['coordinates']['coordinates'][0])
    lat_list.append(j['coordinates']['coordinates'][1])
    senti_list.append(j['sentiment'])
    sa3_temp = []
    sa3_temp.append(j['SA3_Name'])
    sa3_temp.append(j['SA3_Code'])
    sa3_list.append(sa3_temp)
    followers_list.append(j['user']['followers_count'])
    username_list.append(j['user']['name'])
    tweet_list.append(j['text'])
    hashtags_list.append(j['entities']['hashtags'])
    date_list.append(j['created_at'])
    # print(j)
    k+=1
  print(k)

  sa3_followers=[]

  for n in range(len(sa3_list)):
    sa3_followers_temp = []

    sa3_followers_temp.append(sa3_list[n][0])
    sa3_followers_temp.append(followers_list[n])
    sa3_followers_temp.append(date_list[n])
    sa3_followers_temp.append(username_list[n])
    sa3_followers_temp.append(tweet_list[n])
    sa3_followers_temp.append(hashtags_list[n])
    sa3_followers_temp.append(senti_list[n])

    sa3_followers.append(sa3_followers_temp)


  with open(fname, 'w') as f:
    for i in sa3_followers:
      print(i,file=f)
  print("\n", " total Execution time= %s seconds" % (time.time() - start_time))
  print("query reading time = ", x ,"seconds")
  #Kartik's code
  list_couchdb = sa3_followers
  hashtag_dictionary = {}
  sentiment_dictionary = {}
  suburb_followers_dictionary = {}
  suburb_hashtag_dictionary = {}
  for item in list_couchdb:
    suburb = item[0]
    suburb_hashtag_dictionary[suburb] = 1
  for item in list_couchdb:
    for sub in suburb_hashtag_dictionary.keys():
      if sub == item[0]:
        suburb_hashtag_dictionary[sub] = []
  for sub in suburb_hashtag_dictionary.keys():
    list_of_hastag = []
    newhashtaglist=[]
    list_of_sentiment = []
    for tweet in list_couchdb:
      if tweet[0] == sub:
        list_of_hash_for_each_tweet = tweet[5]
        list_of_sentiment.append(tweet[6])
        for individual_hashtag in list_of_hash_for_each_tweet:
          list_of_hastag.append(individual_hashtag['text'])
          templist = [x.lower() for x in list_of_hastag]
          list_of_hastag = templist
    hashtag_dictionary[sub] = list_of_hastag
    sentiment_dictionary[sub] = list_of_sentiment


  for sub in hashtag_dictionary.keys():
    list_sub = hashtag_dictionary[sub]
    hashtag_dictionary_for_suburb = dict([i, list_sub.count(i)] for i in list_sub)
    hashtag_dictionary_for_suburb = sorted(hashtag_dictionary_for_suburb.items(), key=operator.itemgetter(1),
      reverse=True)
    suburb_hashtag_dictionary[sub] = hashtag_dictionary_for_suburb[0:3]#number of hastags to pick
  # print(type(suburb_hashtag_dictionary))
  temp_sentiment_dictionary = sentiment_dictionary
  for keys in temp_sentiment_dictionary.keys():
    temp_dict = Counter(temp_sentiment_dictionary[keys])
    temp_dict_sentiment = {}
    temp_dict_sentiment['neutral'] = round((temp_dict['neutral'] / (
            temp_dict['neutral'] + temp_dict['positive'] + temp_dict['negative'])) * 100, 1)
    temp_dict_sentiment['positive'] = round((temp_dict['positive'] / (
            temp_dict['neutral'] + temp_dict['positive'] + temp_dict['negative'])) * 100, 1)
    temp_dict_sentiment['negative'] = round((temp_dict['negative'] / (
            temp_dict['neutral'] + temp_dict['positive'] + temp_dict['negative'])) * 100, 1)
    sentiment_dictionary[keys] = temp_dict_sentiment
  # print(sentiment_dictionary)
  suburb_sentiment_dictionary = sentiment_dictionary
  for sub in suburb_hashtag_dictionary.keys():
    suburb_followers_dictionary_suburb = {}
    for tweet in list_couchdb:
      if tweet[0] == sub:
        suburb_followers_dictionary_suburb[tweet[3]] = str(tweet[1]) + ' <|> ' + tweet[4]#symbol btwn tweet and followers
    top3 = {k: suburb_followers_dictionary_suburb[k] for k in list(suburb_followers_dictionary_suburb)[:3]}#number of followers
    suburb_followers_dictionary[sub] = top3
  # print(suburb_followers_dictionary)
  # print("length of dollowerdict"+str(len(suburb_followers_dictionary)))
  # print("hastag ki length"+str(len(suburb_hashtag_dictionary)))
  for x in suburb_followers_dictionary.keys():
      print("suburb name : "+x)
      print("followers")
      print(suburb_followers_dictionary[x])
      topfollowersineachsub_dict=suburb_followers_dictionary[x]
      keys=list(topfollowersineachsub_dict.keys())
      values=list(topfollowersineachsub_dict.values())
      folcount,tweet = values[0]
      print(folcount)
      print(tweet)
      print(values[1])
      print(values[2])
      print(keys[0])
      print(keys[1])
      print(keys[2])
      print(type(keys))


      key0=""
      key1=""
      key2=""
      values0=""
      values1 = ""
      values2 = ""
      folcount0=""
      text0=""
      folcount1 = ""
      text1 = ""
      folcount2 = ""
      text2 = ""
      if len(keys)==0 and len(values)==0:
        print("no followers")
        key0 = "no followers"
        key1 = ""
        key2 = ""
        values0 = ""
        values1 = ""
        values2 = ""
      elif len(keys)==1 and len(values)==1:
        key0=keys[0]
        key1=""
        key2=""
        values0 = values[0]
        folcount0,text0 = values0.split("<|>")
        values1 = ""
        values2 = ""
        print(key0)
        print(folcount0, text0)
      elif len(keys)==2 and len(values)==2:
        key0 = keys[0]
        key1 = keys[1]
        key2 = ""
        values0 = values[0]
        folcount0,text0 = values0.split("<|>")
        values1 = values[1]
        folcount1,text1 = values1.split("<|>")
        values2 = ""
        print(key0)
        print(folcount0, text0)
        print(key1)
        print(folcount1, text1)
      elif len(keys)==3 and len(values)==3:
        key0 = keys[0]
        key1 = keys[1]
        key2 = keys[2]
        values0 = values[0]
        print(values0)
        folcount0,text0 = values0.split("<|>")
        values1 = values[1]
        folcount1,text1 = values1.split("<|>")
        values2 = values[2]
        folcount2,text2 = values2.split("<|>")
        print(key0)
        print(folcount0,text0)
        print(key1)
        print(folcount1,text1)
        print(key2)
        print(folcount2,text2)

  for x in suburb_hashtag_dictionary.keys():
    p = suburb_hashtag_dictionary[x]
    if len(p) == 0:
      print("no hashtags")
    elif len(p) == 1:
      print(p[0][0])
    elif len(p) == 2:
      print(p[0][0])
      print(p[1][0])
    elif len(p) == 3:
      print(p[0][0])
      print(p[1][0])
      print(p[2][0])
    print()
    print("hashtag")
    print(suburb_hashtag_dictionary[x])
    print("***************************************************************************")

  #kartiks code ends here

  return 0




if __name__ == "__main__":
  main()
