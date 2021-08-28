from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import random
import ssl
import json
import sqlite3

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://pmjay.gov.in/pagination.php'
html = urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")

# Database

conn = sqlite3.connect('hospitals.sqlite')
cur = conn.cursor()

cur.executescript('''DROP TABLE IF EXISTS Hospitals;
            DROP TABLE IF EXISTS District_Hospitals;
            DROP TABLE IF EXISTS Locations;

            CREATE TABLE IF NOT EXISTS Hospitals (Hospital_Name TEXT, Address TEXT, District TEXT, State TEXT);
            CREATE TABLE IF NOT EXISTS District_Hospitals (District TEXT, Hospital_Name TEXT, Address TEXT, State TEXT);
            CREATE TABLE IF NOT EXISTS Locations(Hospital_Name TEXT, gdata TEXT); 
'''
                  )

# API Credentials
serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyAS19_Zro5RV71XsOYG0m-7UVHKNiYqRG8"

# Retrieve all of the states

states = []
tags = soup('object')
for tag in tags:
    states = tag.get('value')
states = states[1:-1]

rand_idx = 'Assam'
state = 'Haryana'

# Using this state
url = 'https://pmjay.gov.in/pagination.php?search%5Bstate%5D=' + state + '&search%5Bdistrict%5D=&Search='
data = []
html = urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")
tags = soup('th')
for item in tags:
    data.append(item.text)
tags = soup('td')
for item in tags:
    data.append(item.text)

# Storing hospital data of a state
hospital_data = [[None for _ in range(4)] for _ in range(len(data) // 4)]
for i in range(0, len(data) // 4):
    for j in range(4):
        hospital_data[i][j] = data[4 * i + j]

# Storing data in database


for i in range(1, len(hospital_data)):
    name = hospital_data[i][0]
    address = hospital_data[i][1]
    state = hospital_data[i][2]
    district = hospital_data[i][3]
    cur.execute('''INSERT INTO Hospitals (Hospital_Name, Address,State,District)
                VALUES (?,?,?,?)''', (name, address, state, district))

sqlstr = 'SELECT District FROM Hospitals'

districtlist = []
for i in range(len(hospital_data)):
    districtlist.append(hospital_data[i][3])

#rand_idx = random.randrange(len(districtlist))
dis = random.choice

cur.execute(''' 
INSERT INTO District_Hospitals (District, Hospital_Name, Address,State)
SELECT District, Hospital_Name, Address, State FROM Hospitals
WHERE District = ?
''', (dis,))



# taking address
location = []

for i in range(1, len(hospital_data)):
    if hospital_data[i][3] == dis:
        location.append(
            hospital_data[i][0] + ", " + hospital_data[i][1] + ", " + hospital_data[i][3] + ", " + hospital_data[i][2])

# using forward geocoding

geodata = dict()
base_url = "http://api.positionstack.com/v1/forward?access_key=e87e0b95fe3f68e4de19530c3ea94cdf&query="

for i in location:
    add = i
    url = base_url + add.replace(" ", "+")
    uh = urlopen(url, context=ctx)
    data = uh.read().decode()
    g = i.split(',')
    try:
        js = json.loads(data)
        latitude = str(js["data"][0]["latitude"])
        longitude = str(js["data"][0]["longitude"])
        coor = latitude + ", " + longitude
        geodata[g[0]] = coor

    except:
        print("Failed to retrieve coordinates for " + g[0])
        pass

for i in geodata.keys():
    print(i, geodata[i])
    cur.execute('''
            INSERT INTO Locations (Hospital_Name, gdata)
            VALUES (?, ?)''', (i, geodata[i]))

conn.commit()
cur.close()
