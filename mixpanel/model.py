from itertools import islice, groupby
from datetime import datetime
import math
from bitdeli.model import model


NUM_DAYS = 30
MAX_BINS = 6

def events(profile):
    
    def hour2day(event):
        return datetime.utcfromtimestamp(event[0] * 3600).toordinal()
    
    def hour_lists():
        for event, hours in profile['events'].iteritems():
            hour_list = list(hours)
            yield hour2day(hour_list[-1]), event, hour_list
    
    event_list = list(hour_lists())
    first_day = min(event_list)[0]
    for _first, event, hour_list in event_list:
        for day, hours in groupby(reversed(hour_list), hour2day):
            relative = day - first_day
            if relative > NUM_DAYS:
                break
            else:
                daily_total = sum(count for hour, count in hours) 
                yield event, relative, daily_total
                
@model
def build(profiles):
    for profile in profiles:
        if profile.uid:
            for event, day, count in events(profile):
                bin = min(int(math.log(count, 2)), MAX_BINS)
                yield '%s:%s:%s' % (day, bin, event), profile.uid