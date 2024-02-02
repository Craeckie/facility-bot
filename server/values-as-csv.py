import redis
import pickle
from trash_utils import *

cache = redis.Redis(host='redis', port=6379, db=0)
cache.set_response_callback('HGET', pickle.loads)

l = load_list(cache)

with open('/output/values.csv', 'w') as f:
    for ts, temp in l:
        d = ts.date()
        time = ts.time()
        line = ','.join([str(v) for v in [d, time, temp]])
        print(line)
        f.write(line + '\n')
