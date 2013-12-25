import datetime
import copy
from django.utils.timezone import utc

class Cacher(object):
    '''
    Caching object for data
    '''
    _cache = {}
    _caching_time = 10 # seconds
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
        
    def store(self, section, hashkey, value, howlong=_caching_time):
        if not section or not hashkey or not value:
            return False
        
        if not self._cache.get(section, False):
            self._cache[section] = {}
            
        self._cache[section][hashkey] = {'data': value, 'when': (datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(seconds=howlong))}
        return True
        
    def fetch(self, section, hashkey):
        try:
            cache_object = self._cache[section].get(hashkey, None)
        except:
            if self._debug:
                print "Cache MISS for %s %s (with error)" % (section, hashkey)
            return False
        
        if cache_object and cache_object.get('when', False) >= datetime.datetime.utcnow().replace(tzinfo=utc):
            cached_data = self._cache[section][hashkey]['data']
            if self._debug:
                print "Cache HIT for %s %s" % (section, hashkey)
            return cached_data
        else:
            if self._debug:
                print "Cache MISS for %s %s" % (section, hashkey)
            return False
        
    def purge(self, section):
        '''
        Removed cached contents for section
        '''    
        if self._cache.get(section, False):
            self._cache[section] = {}
            return True
    
    def setDebug(self, flag):
        self._debug = flag
        