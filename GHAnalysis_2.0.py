import json
import os
import argparse
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor

class Data:
    def __init__(self, dict_address: int = None, reload: int = 0):
        if reload == 1:
            self.__init(dict_address)
        if dict_address is None and not os.path.exists('1.json') and not os.path.exists('2.json') and not os.path.exists('3.json'):
            raise RuntimeError('error: init failed')
        x = open('1.json', 'r', encoding='utf-8').read()
        self.__4Events4PerP = json.loads(x)
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)
    def __init(self, dict_address: str):
        self.__4Events4PerP = {}
        self.__4Events4PerR = {}
        self.__4Events4PerPPerR = {}
        json_list = []
        #建立进程池，共4个进程
        pool = multiprocessing.Pool(4)
        for root, dic, files in os.walk(dict_address):
            #利用多进程进行文件的读入和提取，提高文件读入效率
            for f in files:
                result = pool.apply_async(self.get_content, args=(f,dict_address, json_list))
            pool.close()
            pool.join()
            
            
            #读入存储在数据目录下的records.json文件用于遍历统计
            with open(dict_address + '\\' + 'records.json','r', encoding='utf-8') as r:
                records = json.load(r)

            for i in records:
                if not self.__4Events4PerP.get(i['actor__login'], 0):
                    self.__4Events4PerP.update({i['actor__login']: {}})
                    self.__4Events4PerPPerR.update({i['actor__login']: {}})
                self.__4Events4PerP[i['actor__login']][i['type']
                                            ] = self.__4Events4PerP[i['actor__login']].get(i['type'], 0) + 1
                if not self.__4Events4PerR.get(i['repo__name'], 0):
                    self.__4Events4PerR.update({i['repo__name']: {}})
                self.__4Events4PerR[i['repo__name']][i['type']
                                        ] = self.__4Events4PerR[i['repo__name']].get(i['type'], 0) + 1
                if not self.__4Events4PerPPerR[i['actor__login']].get(i['repo__name'], 0):
                    self.__4Events4PerPPerR[i['actor__login']].update({i['repo__name']: {}})
                self.__4Events4PerPPerR[i['actor__login']][i['repo__name']][i['type']
                                                                    ] = self.__4Events4PerPPerR[i['actor__login']][i['repo__name']].get(i['type'], 0) + 1
        with open('1.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerP,f)
        with open('2.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR,f)
        with open('3.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR,f)

    #基于进程池中异步处理的特征，需要新构建一个函数提取文件内容
    def get_content(self, f, dict_address, json_list):
        append = json_list.append
        if f[-5:] == '.json':
            json_path = f
            x = open(dict_address+'\\'+json_path,
                    'r', encoding='utf-8').read()
            str_list = [_x for _x in x.split('\n') if len(_x) > 0]
            for  i,_str in enumerate(str_list):
                try:
                    append(json.loads(_str))
                except:
                    pass
            
        records = self.__listOfNestedDict2ListOfDict(json_list)
        #由于records列表无法直接传回主进程，将其保存为一个文件在主进程中调用
        with open(dict_address + '\\' + 'records.json' ,'w') as p:
            json.dump(records, p)

    def __parseDict(self, d: dict, prefix: str):
        _d = {}
        for k in d.keys():
            if k == 'login' or k == 'actor' or k == 'repo' or k == 'type' or k == 'name':
                if str(type(d[k]))[-6:-2] == 'dict':
                    _d.update(self.__parseDict(d[k], k))
                else:
                    _k = f'{prefix}__{k}' if prefix != '' else k
                    _d[_k] = d[k]
        return _d

    def __listOfNestedDict2ListOfDict(self, a: list):
        records = []
        append = records.append
        for d in a:
            _d = self.__parseDict(d, '')
            append(_d)
        return records

    def getEventsUsers(self, username: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        else:
            return self.__4Events4PerP[username].get(event,0)

    def getEventsRepos(self, reponame: str, event: str) -> int:
        if not self.__4Events4PerR.get(reponame,0):
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event,0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame,0):
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def analyse(self):
        
            
        if self.parser.parse_args().init:
            with ThreadPoolExecutor(max_workers=2) as workers:
                self.data = workers.submit(Data,self.parser.parse_args().init, 1)
            return 0

        else:
            if self.data is None:
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        res = self.data.getEventsUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo, self.parser.parse_args().event)
                    else:
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -l or -c are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    a = Run()
    