import time
import logging
import redis
from flask import Flask, request, jsonify
logging.basicConfig(filename='error.log',level=logging.DEBUG)
app = Flask(__name__)
app.config["DEBUG"]=True
map={}
cache = redis.Redis(host='redis', port=6379)



def get_map(remaddr):
    print("%s" % map)
    retries = 5
    while True:
        try:
            if remaddr in map.keys():
                app.logger.info("%s is in keys, incrementing value" % remaddr)
                hits=cache.incr('hits')
                map[remaddr]=hits
            else:
                app.logger.info("%s is not in keys, adding key" % remaddr)
                map[remaddr]=1
            return map
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/record')
def record():
    map = get_map(request.environ['REMOTE_ADDR'])
    app.logger.info("%s" % map)
    return 'Result map {} \n'.format(map)

@app.route('/resultmap')
def resultmap():
    app.logger.info("%s" % map)
    return 'Result map {} \n'.format(map)
