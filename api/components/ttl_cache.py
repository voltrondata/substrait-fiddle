from cachetools import TTLCache


############################################################
# Class to manage a custom TTLCache
############################################################
class TTL_Cache(TTLCache):
    '''
    Custom TTL_Cache is used to track the last used 
    time of a table in DuckDB. On its expiration
    the table is dropped from the DuckDB. TTL is 
    updated when the table is used.
    '''
    def __init__(self, maxsize, ttl, on_expire):
        super(TTL_Cache, self).__init__(maxsize=maxsize, ttl=ttl)
        self.on_expire = on_expire

    def __delitem__(self, key):
        self.on_expire(key)
        super(TTL_Cache, self).__delitem__(key)

    def update_ttl(self, key):
        self.touch(key)
