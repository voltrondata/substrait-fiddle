from cachetools import TTLCache


class TTL_Cache(TTLCache):
    def __init__(self, maxsize, ttl, on_expire):
        super(TTL_Cache, self).__init__(maxsize=maxsize, ttl=ttl)
        self.on_expire = on_expire

    def __delitem__(self, key):
        self.on_expire(key)
        super(TTL_Cache, self).__delitem__(key)

    def update_ttl(self, key):
        self.touch(key)
