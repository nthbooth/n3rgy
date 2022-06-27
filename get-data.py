#!/usr/local/python-3.8.9/bin/bin/python3
import requests, json
import mysql.connector
import datetime
import configparser
#from datetime import datetime

config=configparser.ConfigParser()
config.read("config.txt")

dbtouse=config.get("dbconfig","db")
dbuser=config.get("dbconfig","dbuser")
dbpassword=config.get("dbconfig","dbpasswd")
n3rgysecret=config.get("n3rgy","secret")

headers= {'Authorization': n3rgysecret}

print(dbtouse)
print(dbuser)
print(dbpassword)
print(n3rgysecret)

cnx = mysql.connector.connect(user=dbuser, password=dbpassword,
                              host='127.0.0.1',
                              database=dbtouse)

query_cursor = cnx.cursor()
query_cursor.execute("select DATE_FORMAT(max(timestamp), '%Y%m%d') from smartmeter_consumption");
timestamp=query_cursor.fetchall()
first_timestamp=timestamp[0][0]

if first_timestamp is None:   
    first_timestamp="20210530"

end_date=datetime.datetime.strptime(first_timestamp, "%Y%m%d") + datetime.timedelta(days=90)
end_date=end_date.strftime('%Y%m%d')


url = "https://consumer-api.data.n3rgy.com/electricity/consumption/1?start="+first_timestamp+"&end="+end_date
r=requests.get(url,headers=headers)
json=r.json()
r.close()


cursor = cnx.cursor()

add_data=("""insert into smartmeter_consumption (timestamp, electricity) values (%s, %s) on duplicate key update electricity=%s""")

for value in json["values"]:
    current_timestamp= datetime.datetime.strptime(value["timestamp"], '%Y-%m-%d %H:%M')
    data=(current_timestamp,value["value"],value["value"])
    cursor.execute(add_data,data)
cnx.commit()
cursor.close()
cnx.close()

