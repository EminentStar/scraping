import redis
from redis import ConnectionError
import logging
from kazoo.client import KazooClient
from kazoo.client import KazooState
import time


logging.basicConfig()
logger = logging.getLogger('redis')

conn = {}
redis_list = ['127.0.0.1:6379', '127.0.0.1:6380','127.0.0.1:6381']


zk = KazooClient(hosts='127.0.0.1:2181')

zk.start()

cnt = 0
root = '/workers/redis'

while True:
    print("cnt(%s)************************************************" % (cnt))
    for child in redis_list:
        child_path = root + '/' + child

        if child in conn: 
            rs = conn[host]
        else:
            host, port = child.split(':')
            rs = redis.Redis(host=host, port=port)
            conn[host] = rs
        
        transaction = zk.transaction()
        
        try:
            rs.ping()
        except ConnectionError:
            if zk.exists(child_path) != None:
                zk.delete(child_path)
            print("%s: error" % (child_path))
        else:
            if zk.exists(child_path) == None:
                zk.create(child_path)
            print("%s: ok" % (child_path))
        transaction.commit()

    time.sleep(10)
    cnt += 1

zk.stop()
