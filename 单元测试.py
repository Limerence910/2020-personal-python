import json
import os
import argparse
import multiprocessing
import threading
import unittest
import test_code

class Test(unittest.TestCase):
    def setUp(self):
        print("\n测试开始！！\n")

    def tearDown(self):
        print("\n测试结束！！")

    def test_init(self):
        print("初始化测试！！")
        data = test_code.Data('D:\Personal\Desktop\学习资料\课程\软件工程实践\第一次个人作业\\test1', 1)
        self.assertTrue(data)
    
    def test_output(self):
        print("测试Data类：")
        t = test_code.output(0,user = 'petroav',event = 'CreateEvent')
        self.assertGreater(t,0)


if __name__ == '__main__':
    unittest.main()
    