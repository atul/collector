import time
import logging
import redis
from flask import Flask, request, jsonify
import requests
import math
import statistics
import ipdb
logging.basicConfig(filename='error.log',level=logging.DEBUG)
app = Flask(__name__)
app.config["DEBUG"]=True
map={}
cache = redis.Redis(host='redis', port=6379)

def check_server_load_distribution(url='http://188.188.188.1:4919/', times=1000):
    resetmap()
    cache.delete(0)
    for i in range(times):
        resp=requests.get('%s' % url)
        #time.sleep(0.1)
        map=recordserver(resp.json()['servername'])

def average(data):
    if not len(data):
        return None
    return sum(data) * 1.0 / len(data)

def validate_distribution(map):
    servers=0
    data=[]
    for k in map.keys():
        data.append(map[k])
    servers=len(data)
    total=math.sum(data)
    standard_deviation = statistics.stdev(data)
    return standard_deviation, total, servers

def resetmap():
    for k in map.keys():
        map[k]=0

def recordserver(server_):
    retries=10
    while True:
        try:
            if server_ in map.keys():
                hits=cache.incr(map['server_'])
            else:
                map[server_]=1
            return map
        except redis.exceptions.ConnectionError as exc:
            if retries==0:
                raise exc
            retries-=1
            time.sleep(0.5)



def get_map(remaddr):
    retries = 10
    while True:
        try:
            if remaddr in map.keys():
                hits=cache.incr('hits')
                map[remaddr]=hits
            else:
                map[remaddr]=1
            return map
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/check')
def check():
    check_server_load_distribution(url='http://188.188.188.1:4919', times=1000)
    std_dev, total, servers=validate_distribution(map)
    return 'Result: standard_deviation: %s, total requests: %s, Number of servers: %s\n' % (std_dev, total, servers), 200

@app.route('/')
def result():
    return 'Result map:\n {} \n'.format(map), 200

@app.route('/record')
def record():
    map = get_map(request.environ['REMOTE_ADDR'])
    #app.logger.info("%s" % map)
    return 'Result map {} \n'.format(map)

@app.route('/resultmap')
def resultmap():
    #app.logger.info("%s" % map)
    return 'Result map {} \n'.format(map)
