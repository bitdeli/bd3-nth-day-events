from itertools import groupby
from collections import Counter
from bitdeli.insight import insight
from bitdeli.widgets import Table, Widget

NUM_DAYS = 30
DEFAULT_SHOW_DAYS = 4

class TokenInput(Widget):
    pass

BINS = ['1', '2-3', '4-7', '8-15', '16-31', '32-63', '64-']
COLUMNS = [{'name': 'event',
            'label': 'Event',
            'row_header': True,
            'width': '200px'}]
COLUMNS += [{'name': bin, 'label': bin, 'cell': 'integer'} for bin in BINS]
COLUMNS += [{'name': 'total',
             'label': 'Total #Users',
             'cell': 'integer'}]
          
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
            bins = [0] * len(BINS)
            for day, event, bin, num_users in items:
                bins[bin] = num_users
            total = float(sum(bins))
            row = dict((BINS[i], {'label': bin, 'background': bin / total})
                       for i, bin in enumerate(bins))
            row['total'] = {'label': int(total)}
            row['event'] = {'label': event}
            yield row
    return list(sorted(scored(),
                       key=lambda x: x['total'],
                       reverse=True))

def select_days(params):
    def label(n):
        return 'Day %d' % n
    if 'tables' in params:
        chosen = [int(d.split()[1]) for d in params['tables']['value']]
    else:
        chosen = range(DEFAULT_SHOW_DAYS)
    data = [label(i) for i in range(NUM_DAYS) if i not in chosen]
    return chosen, TokenInput(id='tables',
                              size=(10, 1),
                              label='Show Days',
                              value=map(label, chosen),
                              data=data)

@insight
def view(model, params):
    days, tokeninput = select_days(params)
    yield tokeninput
    for day, day_data in groupby(keys(model, days), lambda x: x[0]):
        yield Table(size=(12, 'auto'),
                    fixed_width=True,
                    columns_label='Number of Events',
                    data={'columns': COLUMNS,
                          'rows': make_day(day_data)},
                    label='day %s' % day)
    