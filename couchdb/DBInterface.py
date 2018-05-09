#!/usr/bin/python3
import couchdb
import time
def main():

  # create an authenticated connection
  user = "admin"
  password = "cloudt3118"
  couchserver1 = couchdb.Server("http://%s:%s@localhost:9000/" % (user, password))

  print(couchserver1)
  fname = 'canberra.txt'
  # creating database
  dbname = "canberra"
  if dbname in couchserver1:
    db = couchserver1[dbname]
  else:
    db = couchserver1.create(dbname)

  bb_query = {
    "selector": {
      "$and": [
        {"SA3_Name": {"$ne": None}},
        {"user.followers_count": {"$exists": True}},
        {"created_at": {"$exists": True}},
        {"coordinates": {"$eq": None}},
        {"place.bounding_box": {"$exists": True}},
      ]
    },
    "sort": [{"SA3_Name": "desc"},{"user.followers_count":"desc"},{"created_at": "desc"}],
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
        {"created_at": {"$exists":True}},
        {"coordinates": {"$ne": None}}]
    },
    "sort": [{"SA3_Name": "desc"}, {"user.followers_count": "desc"}, {"created_at": "desc"}],
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
    ],
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
    # print(i)
    k+=1
  for j in coords_docs:
    long_list.append(j['coordinates']['coordinates'][0])
    lat_list.append(j['coordinates']['coordinates'][1])
    senti_list.append(i['sentiment'])
    sa3_temp = []
    sa3_temp.append(i['SA3_Name'])
    sa3_temp.append(i['SA3_Code'])
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
  with open(fname, 'w') as f:
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
    for i in sa3_followers:
      print(i,file=f)
  print("\n", " total Execution time= %s seconds" % (time.time() - start_time))
  print("query reading time = ", x ,"seconds")
  return 0




if __name__ == "__main__":
  main()
