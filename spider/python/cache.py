#! /usr/bin/env python3
import redis


class Cache(object):
    """Redis客户端
    """
    __client = None

    def __init__(self):
        if not self.__client:
            pool = redis.ConnectionPool(host='localhost', port=6379, db=3)
            self.__client = redis.Redis(connection_pool=pool)

    def r_sadd(self, cache_key, values):
        if not values:
            return 0

        return self.__client.sadd(cache_key, *values)

    def r_smembers(self, cache_key):
        return self.__client.smembers(cache_key)

    def r_sismember(self, cache_key, value):
        return self.__client.sismember(cache_key, value)

    def r_spop(self, cache_key):
        return self.__client.spop(cache_key)

    def r_set(self, cache_key, value):
        return self.__client.set(cache_key, value)

    def r_get(self, cache_key):
        return self.__client.get(cache_key)

    def r_incr(self, cache_key, amount=1):
        return self.__client.incr(cache_key, amount)

    def r_get_number(self, cache_key):
        return int(self.r_get(cache_key))


if __name__ == "__main__":
    cache = Cache()
    # print(cache.r_sadd('group:index_url:hz', ['https://www.douban.com/group/145219/discussion?start=0', 'https://www.douban.com/group/145219/discussion?start=25']))
    # print(cache.r_smembers('group:index_url:hz'))
    # print(cache.r_spop('group:index_url:hz'))
    # print(cache.r_smembers('group:index_url:hz'))
    # print(cache.r_smembers("group:hz:topic_ids"))
    # print(cache.r_incr('group:incr:hz'))
    print(cache.r_get_number('group:incr:hz'))
