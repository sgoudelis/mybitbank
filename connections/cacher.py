import logging

logging.basicConfig(level='INFO')


class Cacher(dict):
    '''
    This is WORK-IN-PROGRESS
    '''
    def __setitem__(self, key, value):
        #print 'Setting %r to %r' % (key, value)
        super(Cacher, self).__setitem__(key, value)