from os import lstat
import sqlite3
import json
import codecs

conn = sqlite3.connect('hospitals.sqlite')
cur = conn.cursor()

cur.execute('SELECT * FROM Locations')
fhand = codecs.open('location.js', 'w', "utf-8")
fhand.write("const myData = [\n")
count = 0
for row in cur :
    data = str(row[1])
    loc=data.split(",")
    lat=float(loc[0])
    lng = float(loc[1])
    if lat == 0 or lng == 0 : continue
    Name = row[0]
    try:
        print(Name,lat,lng)

        count += 1
        if count > 1 : fhand.write(",\n")
        output = "{'Name': '"+Name+"',\n"+"'Latitude': "+str(lat)+",\n"+"'Longitude': "+str(lng)+"}"
        fhand.write(output)
    except:
        continue
    
fhand.write("\n];\n")
cur.close()
fhand.close()
print(count, "records written to location.js")
