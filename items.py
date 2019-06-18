import numpy as np
import os
import os.path
import sys
import json as js
import time
import requests
import processes
import xml.etree.ElementTree as ET

BATCH_SIZE = 200
NEXT_UPDATE_TIME = -1
UPDATES_LEFT = 600
CACHE_EXPIRE_TIME = 60*60*24
XML_CACHE_EXPIRE_TIME = 7*60*60*24
BATCH = []
XML_BATCH = []

class Category:
    subcategories = []
    items = []
    parent = None
    name = ""
    cachingTime = -1
    cachingTimeXML = -1
    categories = []
    
    maxItemId = -1
    minItemId = sys.maxsize
    
    def __getitem__(self, key):
        for it in self.items:
            if it.name == key:
                return it
        for cat in self.subcategories:
            if cat.name == key:
                return cat
        return None
    
    def addSubcategories(self, subcs):
        for x in subcs:
            x.parent = self
            if x.maxItemId>self.maxItemId:
                self.maxItemId = x.maxItemId
            if x.minItemId<self.minItemId:
                self.minItemId = x.minItemId
        self.subcategories = subcs

    def addItems(self, items):
        for x in items:
            x.parent = self
            self.items = items
            if x.itemId>self.maxItemId:
                self.maxItemId = x.itemId
            if x.itemId<self.minItemId:
                self.minItemId = x.itemId

    @staticmethod
    def load(path, categories=[]):
        files = os.listdir(path)
        files = [x for x in files if x[0]!='.' and x[-1]!='~']
        dirs = [x for x in files if not os.path.isfile(path+'/'+x)]
        files = [x for x in files if os.path.isfile(path+'/'+x)]
        cat = Category()
        cat.categories = categories
        cat.name = path[path.rfind('/')+1:]
        subcs = [Category.load(path+'/'+x, categories+[x]) for x in dirs]
        cat.addSubcategories(subcs)
        items = [Item.load(path+'/'+x, categories) for x in files]
        cat.addItems(items)
        return cat

    def update(self, recursionTop = True):
        global BATCH
        current = time.time()
        if current<NEXT_UPDATE_TIME and UPDATES_LEFT<1:
            return self.cachingTime
        if current-self.cachingTime<CACHE_EXPIRE_TIME and not recursionTop:
            return self.cachingTime
        
        min = current
        if current-self.cachingTime>=CACHE_EXPIRE_TIME:
            for cat in self.subcategories:
                tm = cat.update(False)
                if tm<min:
                    min = tm
            for it in self.items:
                tm = it.update()
                if tm<min:
                    min = tm
            self.cachingTime = min

        if recursionTop:
            while len(BATCH)>0 and UPDATES_LEFT>1:
                currentBatch = BATCH[:BATCH_SIZE]
                state = batchUpdate(currentBatch)
                if state == 'OK':
                    BATCH = BATCH[BATCH_SIZE:]
                else: break
        return min
    
    def updateXML(self, recursionTop = True):
        global XML_BATCH
        current = time.time()
        if current-self.cachingTimeXML<XML_CACHE_EXPIRE_TIME and not recursionTop:
            return self.cachingTimeXML
        
        min = current
        if current-self.cachingTimeXML>=XML_CACHE_EXPIRE_TIME:
            for cat in self.subcategories:
                tm = cat.updateXML(False)
                if tm<min:
                    min = tm
            for it in self.items:
                tm = it.updateXML()
                if tm<min:
                    min = tm
            self.cachingTimeXML = min
        
        if recursionTop:
            while len(BATCH)>0:
                currentBatch = XML_BATCH[:BATCH_SIZE]
                state = batchUpdateXML(currentBatch)
                if state == 'OK':
                    XML_BATCH = XML_BATCH[BATCH_SIZE:]
                else: break
        return min

    def find(self, itemId):
        if itemId > self.maxItemId or itemId < self.minItemId:
            return None
        for it in self.items:
            if it.itemId == itemId:
                return it
        for cat in self.subcategories:
            it = cat.find(itemId)
            if it is not None:
                return it
        return None

    def save(self):
        for cat in self.subcategories:
            cat.save()
        for it in self.items:
            it.save()

    def clearCache(self, recursionTop = True):
        global BATCH
        for cat in self.subcategories:
            cat.clearCache()
        for it in self.items:
            it.clearCache()
        if recursionTop:
            BATCH = []
            XML_BATCH = []
            self.save()


class Item:
    parent = None
    nodeType = "item"
    name = ""
    cachingTime = -1
    cachingTimeXML = -1
    itemId = -1
    buyPrice = -1
    sellPrice = sys.float_info.max
    basePrice = -1
    volume = -1
    isRaw = False
    isFinal = False
    inProcess = []
    outProcess = []
    filename = ""
    bpo = -1
    categories = []

    @staticmethod
    def load(path, categories):
        f = open(path)
        js_str = f.read()
        data = js.loads(js_str)
        it = Item()
        it.filename = path
        it.name = data['name']
        if 'buy' in data:
            it.buyPrice = float(data['buy'])
        if 'sell' in data:
            it.sellPrice = float(data['sell'])
        if 'base' in data:
            it.basePrice = float(data['base'])
        if it.sellPrice==-1:
            it.sellPrice = sys.float_info.max
        it.itemId = int(data['itemId'])
        it.volume = float(data['volume'])
        if 'cachingTime' in data:
            it.cachingTime = float(data['cachingTime'])
        if 'cachingTimeXML' in data:
            it.cachingTimeXML = float(data['cachingTimeXML'])
        if 'isRaw' in data:
            it.isRaw = True
        if 'isFinal' in data:
            it.isFinal = True
        if 'bpc' in data:
            it.nodeType = "bpc"
        if 'bpo' in data:
            it.bpo = data['bpo']
        if 'inProcess' in data:
            it.inProcess = data['inProcess']
        if 'outProcess' in data:
            it.outProcess = data['outProcess']
        it.categories = categories
        return it
    
    def update(self):
        global BATCH
        current = time.time()
        if self.nodeType == "bpc":
            return current
        if current-self.cachingTime<CACHE_EXPIRE_TIME:
            return self.cachingTime
        BATCH.append(self)
        self.cachingTime = current
        return current

    def updateXML(self):
        global XML_BATCH
        current = time.time()
        if self.nodeType == "bpc":
            return current
        if current-self.cachingTimeXML<XML_CACHE_EXPIRE_TIME:
            return self.cachingTimeXML
        XML_BATCH.append(self)
        self.cachingTimeXML = current
        return current

    def printf(self):
        if self.parent is not None:
            print('Parent: ' + self.parent.name)
        print('Name: ' + self.name)
        print('CachingTime: ' + str(self.cachingTime))
        print('CachingTimeXML: ' + str(self.cachingTime))
        print('ItemID: ' + str(self.itemId))
        print('Buy: ' + str(self.buyPrice))
        print('Sell: ' + str(self.sellPrice))
        print('Volume: ' + str(self.volume))
        print('inProcesses:')
        print('[')
        for pr in self.inProcess:
            print(str(pr)+'  ')
        print(']')
        print('outProcesses:')
        print('[')
        for pr in self.outProcess:
            print(str(pr)+'  ')
        print(']')

    def save(self):
        d = { 'name':self.name, 'buy':self.buyPrice, 'sell':self.sellPrice, 'base':self.basePrice, 'itemId':self.itemId, 'volume':self.volume, 'cachingTime':self.cachingTime, 'cachingTimeXML':self.cachingTimeXML, 'inProcess':self.inProcess, 'outProcess':self.outProcess}
        if self.isRaw:
            d['isRaw'] = 1
        if self.isFinal:
            d['isFinal'] = 1
        if self.bpo != -1:
            d['bpo'] = self.bpo
        if self.nodeType == "bpc":
            d['bpc'] = 1
        js_data = js.loads(js.dumps(d))
        with open(self.filename, 'w') as f:
            js.dump(js_data, f)

    def clearCache(self):
        self.cachingTime = -1
        self.sellPrice = -1
        self.buyPrice = -1


def init(path):
    root = Category.load(path)
    loadCache(root)
    root.update()
    root.updateXML()
    save(root)
    return root

def loadCache(root):
    global BATCH, XML_BATCH, UPDATES_LEFT, NEXT_UPDATE_TIME
    if os.path.isfile('cache.json'):
        f = open('cache.json')
        js_str = f.read()
        data = js.loads(js_str)
        if 'batch' in data:
            BATCH = [root.find(x) for x in data['batch']]
        if 'xml_batch' in data:
            XML_BATCH = [root.find(x) for x in data['xml_batch']]
        if 'uleft' in data:
            UPDATES_LEFT = data['uleft']
        if 'utime' in data:
            NEXT_UPDATE_TIME = data['utime']

def save(root):
    global NEXT_UPDATE_TIME, UPDATES_LEFT, BATCH, XML_BATCH
    root.save()
    js_data = js.loads(js.dumps({ 'utime':NEXT_UPDATE_TIME, 'uleft':UPDATES_LEFT, 'batch':[x.itemId for x in BATCH], 'xml_batch':[x.itemId for x in XML_BATCH]}))
    with open('cache.json', 'w') as f:
        js.dump(js_data, f)


def batchUpdate(batch):
    oldPrices = [(x.sellPrice, x.buyPrice) for x in batch]
    newPrices = priceRequest(batch)
    if len(newPrices)>1 or newPrices[0][0]!=-1:
        oldPrices = newPrices
    else: return 'ERROR'
    for x,p in zip(batch, oldPrices):
        x.sellPrice = p[0]
        x.buyPrice = p[1]
    return 'OK'

def batchUpdateXML(batch):
    url = "https://api.eve-industry.org/job-base-cost.xml?names="
    for it in batch:
        url = url + it.name.replace(" ", "%20") + ","
    url = url[:-1]
    try:
        response = requests.get(url)
    except:
        return 'ERROR'
    statusCode = response.status_code
    res = []
    if statusCode == 200:
        root = ET.fromstring(response.content)
        res = [root.find('job-base-cost['+str(j+1)+']') for j in range(len(batch))]
        res = [setBasePriceIfNotNone(x, batch) for x in res]
        return 'OK'
    return 'ERROR'


def priceRequest(batch):
    global UPDATES_LEFT, NEXT_UPDATE_TIME
    baseUrl = "https://api.evemarketer.com/ec/marketstat/json";
    url = baseUrl+"?typeid="
    for it in batch:
        url = url + str(it.itemId)+","
    url = url[:-1]
    try:
        response = requests.get(url)
    except:
        return [(-1,-1)]
    statusCode = response.status_code
    res = []
    if statusCode == 200:
        jsres = js.loads(response.content)
        res = [(float(x['sell']['fivePercent']), float(x['buy']['fivePercent'])) for x in jsres]
    else: return [(-1,-1)]
    header = response.headers
    UPDATES_LEFT = int(header['X-Ratelimit-Remaining'])
    NEXT_UPDATE_TIME = int(header['X-Ratelimit-Reset'])
    return res


def clearCache():
    root.clearCache()

def show(elem):
    for child in elem.findall('*'):
        show(child)

def setBasePriceIfNotNone(elem, batch):
    if elem is None:
        return -1
    name = elem.get('name')[:-10]
    for it in batch:
        if it.name==name:
            it.basePrice = float(elem.text)
            return 1
