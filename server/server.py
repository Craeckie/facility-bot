import logging
import pickle
import json
import redis
import time
import os
from datetime import datetime, timedelta
from flask import Flask, request

from utils import load_list, store_list, load_xy

app = Flask(__name__)
r = redis.Redis(host=os.environ.get('REDIS_HOST', default='127.0.0.1'), port=6379, db=0)


# Nur logging
class RequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.url = request.url
            record.remote_addr = request.remote_addr
        except Exception:
            pass
        return super().format(record)


formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
logging.basicConfig(filename='/var/log/flask.log', level=logging.DEBUG)
from flask.logging import default_handler

default_handler.setFormatter(formatter)

# app.logger.addHandler(

r.set_response_callback('HGET', pickle.loads)


# if not r.get('temp:list')
@app.route("/")
def hello():
    if r.exists('temp'):
        (last_time, temp) = r.hget('temp', 'temp')
        l = load_list(r)
        # for j in reversed(r.lrange('temp:list', 0, -1)):
        text_list = reversed(["{0:%H:%M:%S}: {1}".format(time, value) for time, value in l])
        # for time, value in l:
            # pars = json.loads(j)
            # unix_time = pars[0]
            # t = float(pars[1])
            # l.append("{0:%H:%M:%S}: {1}".format(datetime.fromtimestamp(time), float(value)))
        # last_temp_formatted = "{0} ({1:%d.%m.%y %H:%M:%S})".format(temp, datetime.fromtimestamp(float(last_time)))
        last_temp_formatted = "{0} ({1:%d.%m.%y %H:%M:%S})".format(temp, last_time)
        text =  f"Last temperature: {last_temp_formatted }<br />\n"
        text += f"List ({len(l)}):<br />\n"
        text += '<br />\n'.join(text_list)
        return text
    else:
        return "Hello World!"

@app.route("/api/last")
def last():
    if r.exists('temp'):
        (last_time, temp) = r.hget('temp', 'temp')
        return f"{temp}"
    else:
        return "N/A"

@app.route("/temp/<float:temp>")
def tmp(temp):
    l = load_list(r)
    new_val = (datetime.now(), temp)
    data = pickle.dumps(new_val)
    r.hset('temp', 'temp', data)
    l.append(new_val)
    l = [(time, value) for (time, value) in l if time > datetime.now() - timedelta(days=7)]
    store_list(r, l)

    return f"Temp changed to {temp}"


@app.route("/reset")
def reset():
    r.delete('temp:list')
    r.hdel('temp', 'temp')
    return "Success!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
