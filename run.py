# -*- coding: utf-8 -*-
import time
from Solution.manager import Gym_Manager
lines1 = ['abcdefghijklmnopqrst1234567890',
         'U001 2016-06-02 22:00~22:00 A',
         'U002 2017-08-01 19:00~22:00 A',
         'U003 2017-08-02 13:00~17:00 B',
         'U004 2017-08-03 15:00~16:00 C',
         'U005 2017-08-05 09:00~11:00 D'
         ]
lines2 = ['U002 2017-08-01 19:00~22:00 A',
          'U003 2017-08-01 18:00~20:00 A',
          'U002 2017-08-01 19:00~22:00 A C',
          'U002 2017-08-01 19:00~22:00 A C',
          'U003 2017-08-01 18:00~20:00 A',
          'U003 2017-08-02 13:00~17:00 B'
          ]
# 取消预订的请求，必须与之前的预订请求严格匹配，需要匹配的项有⽤户ID
lines3 = ['U002 2017-08-01 19:00~22:00 A',
          'U003 2017-08-01 18:00~20:00 A',
          'U005 2017-08-01 19:00~22:00 A C',
          'U002 2017-08-01 19:00~22:00 A C',
          'U003 2017-08-01 18:00~20:00 A',
          'U003 2017-08-02 13:00~17:00 B'
          ]
debug = True
debug = False

print('-----------测试用例1----------')
gm = Gym_Manager(debug=debug)
for line in lines1:
    # print line,
    gm.input_handler(line)

gm.input_handler()

print('\n\n')
print('-----------测试用例2-----------')
#
gm = Gym_Manager()
for i in range(len(lines2)):
    # print line
    gm.input_handler(lines2[i])

gm.input_handler(None)

print('\n\n')
print('-----------测试用例3-----------')
#
gm = Gym_Manager()
for i in range(len(lines3)):
    # print line
    gm.input_handler(lines3[i])

gm.input_handler(None)


print('\n\n')
print('-----------标准输入测试-----------')
print('-----------请按回车键打印收入表单----------')
gm = Gym_Manager()
while True:
    gm.stdin_input_handler()