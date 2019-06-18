#!/usr/bin/env python3
import os
import json as js
INDEX = 500006

def processDir(path):
    files = os.listdir(path)
    files.sort()
    files = [x for x in files if x[0]!='.' and x[-1]!='~']
    dirs = [x for x in files if not os.path.isfile(path+'/'+x)]
    files = [x for x in files if os.path.isfile(path+'/'+x)]
    [processDir(path+'/'+x) for x in dirs]
    [processFile(path+'/'+x) for x in files]

def processFile(path):
    global INDEX
    js_str = ""
    with open(path) as f:
        js_str = f.read()
    data = js.loads(js_str)
    data['processId'] = INDEX
    INDEX = INDEX+1
    js_data = js.loads(js.dumps(data))
    with open(path, 'w') as f:
        js.dump(js_data, f)

processDir('Processes')
