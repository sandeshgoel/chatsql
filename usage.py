import requests
import datetime
import time
from dotenv import load_dotenv
import os
import json

def epoch2str(epoch_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch_time))

def get_usage_data(date):
    # Parameters for API request
    params = {'date': date}
    # Send API request and get response
    response = requests.get(url, headers=headers, params=params)
    usage_data = response.json()['data']
    return usage_data

load_dotenv()

# API key
api_key =  os.getenv("OPENAI_API_KEY") 
headers = {'Authorization': f'Bearer {api_key}'}
url = 'https://api.openai.com/v1/usage'

price_in = {
            'gpt-3.5-turbo-0125':0.5, 
            'gpt-4o-2024-05-13':5,
            'gpt-4-0613':0.5
            }
price_out = {
            'gpt-3.5-turbo-0125':1.5, 
            'gpt-4o-2024-05-13':15,
            'gpt-4-0613':1.5
            }

# Date for which to get usage data
date = datetime.datetime.now() # datetime.date(2024, 6, 14)
total_price_m = {}
total_price = {}
verbose = False

for i in range(30):
    d = date - datetime.timedelta(days=i)
    ds = d.strftime('%Y-%m-%d')
    fname = 'openai_usage/'+ds
    if (i>0 and os.path.isfile(fname)):
        with open(fname) as f:   
            usage_data = json.loads(f.read())
    else:
        print('**** Date: %s, Downloading data ...' % ds)
        if i>0: time.sleep(1)
        usage_data = get_usage_data(ds)
        if i > 0:
            with open(fname, 'w') as f:
                f.write(json.dumps(usage_data))

    from collections import Counter
    tokens_in = Counter()
    tokens_out = Counter()
    models = set()

    for data in usage_data:
        model_name = data['snapshot_id']
        if (model_name not in price_in.keys()):
            print('\n**** [%s] Model not found: %s, substituting gpt-3.5-turbo-0125\n' % 
                  (epoch2str(data['aggregation_timestamp']), model_name))
            model_name = 'gpt-3.5-turbo-0125'

        models.add(model_name)

        tokens_in[model_name] +=  data['n_context_tokens_total']
        tokens_out[model_name] += data['n_generated_tokens_total']

        price = (data['n_context_tokens_total'] * price_in[model_name] +  
                 data['n_generated_tokens_total'] * price_out[model_name])/10000
        if i==0:
            print('%s: %4.2fc (%d req) %s' % 
                  (epoch2str(data['aggregation_timestamp']), 
                    price, data['n_requests'], model_name))

    total_price_in = Counter()
    total_price_out = Counter()
    total_price_m[ds] = Counter()
    total_price[ds] = 0

    for model in models:
        pin = tokens_in[model] * price_in[model] / 10000
        pout = tokens_out[model] * price_out[model] / 10000
        total_price_in[model]    += pin
        total_price_out[model]   += pout
        total_price_m[ds][model] += pin + pout
        total_price[ds]          += pin + pout

    if (verbose):
        print()
        print('Number of records', len(usage_data))
 #       print('IN : Tk %6d  Cost %6.2fc' % 
 #             (n_context_tokens_total, total_price_in))
 #       print('OUT: Tk %6d  Cost %6.2fc' % 
 #             (n_generated_tokens_total, total_price_out))
        print()
        print('Total price = %6.2fc' % (total_price[ds]))
        print()

import operator
tp = sorted(total_price.items(), key=operator.itemgetter(0), reverse=True)
print('\n**** Daily costs ****\n')
for t in tp:
    date = t[0]
    price = t[1]
    print('%s: %6.2fc %s' % (date, price, total_price_m[date]))


