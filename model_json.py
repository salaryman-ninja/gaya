import datetime
import time

from google.appengine.ext import db
from django.utils import simplejson as json


SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return time.mktime(o.timetuple()) # sec. from epoch
        if not isinstance(o, db.Model):
            return json.JSONEncoder.default(self, o)
        dictionary = {}
        dictionary['key'] = str(o.key())
        dictionary['key_name'] = str(o.key().name())
        for k, v in o.properties().iteritems():
            value = v.get_value_for_datastore(o)
            if value is None:
                pass
            elif v.data_type is datetime.datetime:
                value = self.default(value)
            elif not v.data_type in SIMPLE_TYPES:
                # unknown types
                #value = unicode(str(v))
                continue
            dictionary[k] = value
        return dictionary
