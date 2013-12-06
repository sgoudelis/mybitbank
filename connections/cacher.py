import datetime
import copy
from django.utils.timezone import utc

class Cacher(object):
    '''
    Caching object for data
    '''
    _cache = {}
    _caching_time = 30
    _debug = False
    
    def __init__(self, initial_cache_dir):
        self._cache = initial_cache_dir
    
    def __getitem__(self, key):
        cache = getattr(self, '_cache')
        return cache[key]
     
    def __setitem__(self, key, value):
        cache = getattr(self, '_cache')
        cache[key] = value
        return setattr(self, '_cache', cache)
    
    def get(self, key, default=False):
        if self._cache.get(key, False):
            return self._cache.get(key, False)
        else:
            return default
        
    def store(self, section, hashkey, value):
        if not section or not hashkey or not value:
            return False
        
        if not self._cache.get(section, False):
            self._cache[section] = {}
            
        self._cache[section][hashkey] = {'data': copy.deepcopy(value), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)}
        return True
        
    def fetch(self, section, hashkey):
        try:
            cache_object = self._cache[section].get(hashkey, None)
        except:
            print "Cache MISS for %s %s (with error)" % (section, hashkey)
            return False
        
        if cache_object and ((datetime.datetime.utcnow().replace(tzinfo=utc) - cache_object['when']).seconds) < self._caching_time:
            cached_data = self._cache[section][hashkey]['data']
            if self._debug:
                print "Cache HIT for %s %s" % (section, hashkey)
            return copy.deepcopy(cached_data)
        else:
            if self._debug:
                print "Cache MISS for %s %s" % (section, hashkey)
            return False
        
    def setDebug(self, flag):
        self._debug = flag
        