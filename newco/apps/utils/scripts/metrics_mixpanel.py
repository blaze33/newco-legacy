#! /usr/bin/env python
#
# Mixpanel, Inc. -- http://mixpanel.com/
#
# Python API client library to consume mixpanel.com analytics data.

import csv
#import tablib
import hashlib
import urllib
import time
import pprint
try:
    import json
except ImportError:
    import simplejson as json
    
from django.conf import settings

#Newco Dev
#API_KEY = settings.MIXPANEL_API_KEY_DEV
#API_SECRET = MIXPANEL_API_SECRET_DEV

#Newco Production
API_KEY = settings.MIXPANEL_API_KEY
API_SECRET = settings.MIXPANEL_API_SECRET


TYPE = 'segmentation'
EVENT = 'Load_item_detail'
PROPERTY = 'properties["product"]'
FROM_DATE = '2012-11-9'
TO_DATE = '2012-11-23'
NUM_DAYS = 15

class Mixpanel(object):

    ENDPOINT = 'http://mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        
    def request(self, methods, params, format='json'):
        """
            methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
                      will give us http://mixpanel.com/api/2.0/events/properties/values/
            params - Extra parameters associated with method
        """
        params['api_key'] = self.api_key
        params['expire'] = int(time.time()) + 600   # Grant this request 10 minutes.
        params['format'] = format
        if 'sig' in params: del params['sig']
        params['sig'] = self.hash_args(params)

        request_url = '/'.join([self.ENDPOINT, str(self.VERSION)] + methods) + '/?' + self.unicode_urlencode(params)

        request = urllib.urlopen(request_url)
        data = request.read()

        return json.loads(data)

    def unicode_urlencode(self, params):
        """
            Convert lists to JSON encoded strings, and correctly handle any 
            unicode URL parameters.
        """
        if isinstance(params, dict):
            params = params.items()
        for i, param in enumerate(params):
            if isinstance(param[1], list): 
                params[i] = (param[0], json.dumps(param[1]),)

        return urllib.urlencode(
            [(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params]
        )

    def hash_args(self, args, secret=None):
        """
            Hashes arguments by joining key=value pairs, appending a secret, and 
            then taking the MD5 hex digest.
        """
        for a in args:
            if isinstance(args[a], list): args[a] = json.dumps(args[a])

        args_joined = ''
        for a in sorted(args.keys()):
            if isinstance(a, unicode):
                args_joined += a.encode('utf-8')
            else:
                args_joined += str(a)

            args_joined += '='

            if isinstance(args[a], unicode):
                args_joined += args[a].encode('utf-8')
            else:
                args_joined += str(args[a])

        hash = hashlib.md5(args_joined)

        if secret:
            hash.update(secret)
        elif self.api_secret:
            hash.update(self.api_secret)
        return hash.hexdigest() 

if __name__ == '__main__':
    api = Mixpanel(
        api_key = API_KEY, 
        api_secret = API_SECRET
    )
    
    
    
    
    
    #### Segmentation on Properties ####
    data = api.request([TYPE,],{
        'event' : EVENT,
        'from_date':FROM_DATE,
        'to_date':TO_DATE,
        #'on':PROPERTY,
        #'name':'Country',
        #'values':['Firefox'],
        #'unit' : 'day',
        #'interval' : 7,
        'type': 'unique'
    })
    #print LIST
    pprint.pprint(data)
    pprint.pprint(API_KEY)
    pprint.pprint(API_SECRET)
    filename = 'results.%s.%06d.csv' %(FROM_DATE+'_'+TO_DATE+EVENT+'_'+PROPERTY,2012)
    csv_file = open(filename, 'wb')
    wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    header=["Dates"]
    d = data['data'] ['values']
    for key, value in d.iteritems():
            header.append(key)
    wr.writerow(header)
    
    #### Segmentation/Properties ####
    
    for i in range(NUM_DAYS):
        
        date = data['data'] ['series'] [i]
        list = [date]
        for key, value in d.iteritems():
            value=data['data'] ['values'] [key][date]
            list.append(value)
        wr.writerow(list)
        
        
#        for j in LIST:
#            value=data['data'] ['values'] [j][date]
#            list.append(value)
        #value_1 = data['data'] ['values'] ['Amazon'][date]
        #value_2 = data['data'] ['values'] ['Decathlon'][date]    
    
    #### Segmentation Click to Product ####
#    for i in range(11):
#        date = data['data'] ['series'] [i]
#        value = data['data'] ['values'] ['Click to Product'][date]
#        wr.writerow([date,value])
    
    #pprint.pprint( data_csv)
#pprint.pprint (request)
