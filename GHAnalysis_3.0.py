import json
import os
import time
import argparse
import sqlite3

class Data:
    def __init__(self, dict_address: int = None, reload: int = 0):
        if reload == 1:
            self.__init(dict_address)

        
    def __init(self, dict_address: str):
        #建立一个数据库并建立一个名为HOMEWOEK的表
        connector = sqlite3.connect('Information.db')
        connector.execute('''CREATE TABLE IF NOT EXISTS HOMEWORK (
                actor_login     TEXT    NOT NULL,
                event           TEXT    NOT NULL,
                user_repo       TEXT    NOT NULL);''')      
        connector.commit()
        for f in os.listdir(dict_address):
            if f[-5:] == '.json':
                with open(dict_address + '\\' + f, 'r', encoding = 'utf-8') as f:
                    for _x in f:
                        #将键keys转为字符串类型
                        records = json.loads(_x)
                        data = (records['actor']['login'], records['type'], records['repo']['name'])
                        #往表中添加信息
                        connector.execute('INSERT INTO HOMEWORK(actor_login, event, user_repo) VALUES(?,?,?)',data)
        connector.commit()
        connector.close()
        print(0)

class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.argInit()
        self.data = None
        self.operation()

    def argInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def operation(self):
        if self.parser.parse_args().init:
            self.data = Data(self.parser.parse_args().init, 1)
            return 0
        else:
            if self.data is None:
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        output(type=2, user=self.parser.parse_args().user, event=self.parser.parse_args().event,repo=self.parser.parse_args().repo)
                    else:
                        output(type=0,user=self.parser.parse_args().user,event=self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    output(type=1,repo=self.parser.parse_args().repo,event=self.parser.parse_args().event)
                else:
                    raise RuntimeError('Error: Argument -l or -c is required.')
            else:
                raise RuntimeError('Error: Argument -e is required.')

def output(type, user="", event="", repo=""):
        connector = sqlite3.connect('Information.db')
        if type == 0:
            cursor = connector.execute('SELECT * FROM HOMEWORK WHERE event=? AND actor_login=?',(event,user))
        elif type == 1:
            cursor = connector.execute('SELECT * FROM HOMEWORK WHERE event=? AND user_repo=?',(event,repo))   
        else:
            cursor = connector.execute('SELECT * FROM HOMEWORK WHERE event=? AND user_repo=? AND actor_login=?', (event, repo, user))  
        print(len(list(cursor))) 
        connector.close()

if __name__ == '__main__':
    a = Run()
    