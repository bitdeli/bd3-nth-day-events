from itertools import groupby
from bitdeli.insight import insight
from bitdeli.widgets import Table

BINS = ['1', '2-3', '4-7', '8-15', '16-31', '32-63', '64-']
COLUMNS = [{'name': name, 'label': name.capitalize()}
           for name in ['event'] + BINS + ['total']]

def keys(model, days):
    def items():
        for key in model:
            day, bin, event = key.split(':', 2)
            day = int(day)
            if day in days:
                yield day, event, int(bin), len(model[key])
    return list(sorted(items()))
                
def make_day(day_data):
    def scored():
        for event, items in groupby(day_data, lambda x: x[1]):
            row = dict((bin, 0) for bin in BINS)
            row.update((BINS[bin], num_users)
                       for day, event, bin, num_users in items)
            row['total'] = sum(row.itervalues())
            row['event'] = event
            yield row
    return list(sorted(scored(),
                       key=lambda x: x['total'],
                       reverse=True))

@insight
def view(model, params):
    days = [0, 1, 2]
    for day, day_data in groupby(keys(model, days), lambda x: x[0]):
        yield Table(size=(12, 'auto'),
                    data={'columns': COLUMNS,
                          'rows': make_day(day_data)},
                    label='day %s' % day)
    