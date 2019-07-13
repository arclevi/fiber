import threading
import json
import copy
from testTask import TestExector
from queue import Queue
from  Rs232 import RS232
import time
import os
import configGlobal
import random
class TaskController(object):
    _instance_lock = threading.Lock()
    def __init__(self,*args):
        if args and configGlobal.getDown():
            print ('inited')
            self.queue=Queue()    
            self.buf=dict()
            self.dataDir='data'
            self.taskJson=args[0]
            self.session=random.randint(100000,999999)
            self.isCurrentBusy=False
            self.testsStatus=list()
            self.temperatures={}
            self.testList=dict()
            self.bdysSpeeds=[]
            self.curTemperature=None
            self.sessionFile=''
            t=threading.Thread(target=self._recvTestData)
            t.setDaemon(True)
            t.start()
            self.dev=None
            self.wx=None

    def __new__(cls, *args, **kwargs):
        """
        实现单例模式
        """
        if not hasattr(TaskController, "_instance"):
            with TaskController._instance_lock:
                if not hasattr(TaskController, "_instance"):
                    TaskController._instance = object.__new__(cls)  
        return TaskController._instance
    def _recvTestData(self):
        while True:
            if not self.taskJson:
                break
            temp=self.queue.get()
            #print(temp['test'])
            if 'test' not in self.buf or not self.buf['test']:
                self.buf['test']=temp['test']
            if 'object' not in self.buf or not self.buf['object']:
                    self.buf['object']=self.taskJson['objects-list']
                    if temp['test']=='lp' or temp['test']=='lp_cfx':
                        self.buf['object']=['time']+self.buf['object']
                    elif temp['test']=='bdys' or temp['test']=='bdys_cfx':
                        self.buf['object']=['speed']+self.buf['object']
            if temp['test']=='lp' or temp['test']=='lp_cfx':
                if 'buf' not in self.buf or  len(temp['buf'][0])==1:
                        self.buf['buf']=[]
                else:
                    if len(self.buf['buf'])>=900:
                        self.buf['buf'].pop(0)

                testData={'time':time.strftime("%H:%M:%S")}
                for i in range(len(temp['buf'])):
                    testData[self.taskJson['objects-list'][i]]=temp['buf'][i][-1]
                self.buf['buf'].append(testData)
                #print(self.buf)
            if temp['test']=='bdys' or temp['test']=='bdys_cfx':
                if self.bdysSpeeds:
                    if 'buf' not in self.buf or  len(temp['buf'][0])==1:
                        self.buf['buf']=[]
                    testData={'speed':str(self.bdysSpeeds[len(temp['buf'][0])-1])}
                    for i in range(len(temp['buf'])):
                        testData[self.taskJson['objects-list'][i]]=temp['buf'][i][-1]
                    self.buf['buf'].append(testData)
    def testTaskInit(self):
            self.buf=dict()
            self.taskJson={}
            self.isCurrentBusy=False
            self.testsStatus=list()
            self.temperatures={}
            self.curTemperature=None
            self.testList=dict()
            self.bdysSpeeds=[]
            self.sessionFile=''
            configGlobal.setDown(True)
    def runTests(self):
        if self.taskJson is None or self.testList is None:
            self.testTaskInit()
            return False,'config is None'
        if self.temperatures is None:
            #self.isCurrentBusy=False
            self.testTaskInit()
            return False, 'Test temperature is None'
        today=time.strftime("%Y-%m-%d")
        temp=list(self.taskJson['test-tasks'].keys())
        sortedtemp=list()
        if 'basic' in temp:
            sortedtemp.append('basic')
        if 'normal' in temp:
            sortedtemp.append('normal')
        if 'low' in temp:
            sortedtemp.append('low')
        if 'high' in temp:
            sortedtemp.append('high')
        te=TestExector(self.queue,today,self.taskJson['ni-dev'],self.wx,self.taskJson['test-objects'],self.sessionFile)
        for i in range(len(sortedtemp)):
            t=sortedtemp[i]
            self.testsStatus[i]['status']=2
            self.curTemperature=self.temperatures[t]
            if t=='low' or t=='high':
                self.testsStatus[i]['tests'][0]['status']=2
                te.warmUp(5,self.curTemperature)
                self.testsStatus[i]['tests'][0]['status']=1
            #for test in self.testList[t]:
            for j in range(len(self.testList[t])):
                test=self.testList[t][j]
                print ('Here comes:')
                print (t, test)
                self.buf={}
                if t=='high' or t=='low':
                    self.testsStatus[i]['tests'][j+1]['status']=2
                else:
                    self.testsStatus[i]['tests'][j]['status']=2
                if test=='lp':
                    te.lp(self.curTemperature)
                elif test=='lp_cfx':
                    te.lpRepeat(self.curTemperature)
                elif test=='bdys':
                    te.bdys(self.curTemperature)
                elif test=='bdys_cfx':
                    te.bdysRepeat(self.curTemperature)
                else:
                    time.sleep(5) 
                #fileName=test+'.txt'
                #print (self.buf)
                time.sleep(2)
                if t=='high' or t=='low':
                    self.testsStatus[i]['tests'][j+1]['status']=1
                else:
                    self.testsStatus[i]['tests'][j]['status']=1
                self.buf={}
            self.testsStatus[i]['status']=1
        print ("all Down")
        time.sleep(5)
        self.testTaskInit()
    def combinConfig(self):
        product=self.taskJson['product']
        configFile="config/"+product+".json"
        template=''
        if not os.path.exists(configFile):
            return False,product + " 测试，配置文件不存在"
        userConfig=self.taskJson['test-settings']
        with open(configFile,"r") as f:
            template=json.load(f)
        for temperature in template:
            if temperature not in userConfig:
                continue
            for test in template[temperature]:
                if test not in userConfig[temperature]:
                    continue
                for item in template[temperature][test]:
                    if item in userConfig[temperature][test]:
                        #print (temperature,test,item)
                        template[temperature][test][item]=userConfig[temperature][test][item]
                    if test=='bdys' and item=='speeds':
                        self.bdysSpeeds=[int(x) for x in template[temperature][test][item].split(',')]
        self.sessionFile=os.path.join('config',product+'_'+str(self.session)+'.json')
        with open(self.sessionFile, 'w') as result_file:
            json.dump(template, result_file)
                
    def parseTask(self):
        if self.isCurrentBusy:
            #self.testTaskInit()
            return False,'busy'
        if self.taskJson is None:
            self.testTaskInit()
            return False,'config is None'
        print (self.taskJson)
        configGlobal.setDown(False)
        self.combinConfig()
        self.isCurrentBusy=True
        if self.taskJson['wx']=="rs232":
            self.wx=RS232()
        temp=list(self.taskJson['test-tasks'].keys())
        #print (temp)
        sortedtemp=list()
        if 'basic' in temp:
            sortedtemp.append('basic')
        if 'normal' in temp:
            sortedtemp.append('normal')
        if 'low' in temp:
            sortedtemp.append('low')
        if 'high' in temp:
            sortedtemp.append('high')
        for t in sortedtemp:
            task={'item':t,'tests':[],'status':0}
            if 'temperature' in self.taskJson['test-tasks'][t]:
                self.temperatures[t]=int(self.taskJson['test-tasks'][t]['temperature'])
            else:
                self.temperatures[t]=25
            self.testList[t]=copy.deepcopy(self.taskJson['test-tasks'][t]['testItems'])
            if 'lp' in self.testList[t] and 'lp_wdx' in self.testList[t]:
                self.testList[t].remove('lp_wdx')
            if 'bdys' in self.testList[t] and 'xxd' in self.testList[t]:
                self.testList[t].remove('xxd') 
            if t=='low' or t=='high':
                task['tests'].append({'name':'warmUP','status':0})
            for item in self.testList[t]:
                task['tests'].append({'name':item,'status':0})

            self.testsStatus.append(task)
        #print (self.testsStatus)
        #print (self.temperatures)
        #print (self.testList)
        return True, 'success'
        #task=json.loads(self.taskJson)
    def __del__(self):
        if self.sessionFile and os.path.exists(self.sessionFile):
            os.remove(self.sessionFile)
  
#config={'test-settings': {'normal': {'lp': {'stableFactor': 2, 'samples': 3600, 'wait': 45, 'duration': 60, 'frequency': 1}, 'bdys': {'samples': 3600, 'samplesPerSpeed': 10, 'frequency': 1}, 'lp_cfx': {'repetition': 6, 'powerDown': 60, 'wait': 60, 'duration': 60}, 'bdys_cfx': {'repetition': 6, 'powerDown': 60}}, 'high': {'lp': {'stableFactor': 2, 'samples': 3600, 'wait': 45, 'duration': 60}, 'bdys': {'samples': 3600, 'samplesPerSpeed': 10, 'frequency': 1}}, 'low': {'lp': {'stableFactor': 2, 'samples': 3600, 'wait': 45, 'duration': 60}, 'bdys': {'samples': 3600, 'samplesPerSpeed': 10, 'frequency': 1}}}, 'ni-dev': 'dev1', 'test-objects': {'1': 'abc', '0': '121', '5': 'ed'}, 'test-tasks': {'high': {'temperature': 55, 'testItems': ['lp', 'lp_wdx', 'bdys', 'xxd']}, 'normal': {'temperature': 25, 'testItems': ['lp', 'lp_wdx', 'lp_cfx', 'bdys', 'xxd', 'bdys_cfx']}, 'basic':{'testItems': ['jx', 'lz', 'fbl']}, 'low': {'temperature': -55, 'testItems': ['lp', 'lp_wdx', 'bdys', 'xxd']}}, 'wx': 'rs232', 'product': '10FA'}
#tc=TaskController(config)
#tc.taskJson=config
#tc.parseTask()
#tc.runTests()
#del tc

