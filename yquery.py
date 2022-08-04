import sys
import json
import random
import os
from hashlib import md5
from urllib import parse, request

# Get env variables.
appKey = os.getenv('appid')
key = os.getenv('appkey')
rowLen = int(os.getenv('rowlen'))

# Split query args.
query = " ".join(sys.argv[3:])
target_lang = sys.argv[1]
source_lang = sys.argv[2]

# Construct query request.
salt = str(random.randint(1, 65536))
sign = appKey + query + salt + key
sign = md5(sign.encode()).hexdigest()

ydapi = 'https://openapi.youdao.com/api'
params = dict(appKey=appKey, q=query, salt=salt, sign=sign, to=target_lang)
params['from'] = source_lang
url = ydapi + '?' + parse.urlencode(params)
res = json.loads(request.urlopen(url).read())

output = {
    'items': []
}

# Analyze query result.
if 'translation' in res:
    ent = res['translation']
    basic_def = u",".join(ent)

    # Split long text if necessary.
    while(len(basic_def) > rowLen):
        output['items'].append({
            'title': basic_def[:rowLen],
            'subtitle': 'Basic definition(s)',
            'valid': True,
            'arg': basic_def
        })
        basic_def = basic_def[rowLen:]

    if(len(basic_def) > 0):
        output['items'].append({
            'title': basic_def, 'subtitle': 'Basic definition(s)', 'valid': True, 'arg': basic_def
        })

    if 'web' in res:
        posts = res['web']
        for post in posts:
            web_def = u", ".join(post['value'])
            output['items'].append({
                'title': web_def, 'subtitle': post['key'], 'valid': True, 'arg': web_def})

else:
    output['items'].append({
        'title': 'Query failed',
        'subtitle': 'error code: ' + res['errorCode']
    })

# Output json to stdout.
print(json.dumps(output))
