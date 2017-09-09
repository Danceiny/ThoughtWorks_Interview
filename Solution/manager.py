# -*- coding: utf-8 -*-
from constants import *
from datetime import datetime
import sys


class Gym_Manager:
    '''
    周⼀到周五：
    9:00 ~ 12:00 30元/时
    12:00 ~ 18:00 50元/时
    18:00 ~ 20:00 80元/时
    20:00 ~ 22:00 60元/时
    周六及周⽇
    9:00 ~ 12:00 40元/时
    12:00 ~ 18:00 50元/时
    18:00 ~ 22:00 60元/时
    取消
    - 周⼀到周五的预订取消收取全部费⽤的50%作为违约⾦
    - 周六周⽇的预订取消收取全部费⽤的25%作为违约⾦
    '''
    ORDER_MAX_MASK = 0xfffffffffff
    ORDER_BOOK_MASK= 0x80000000000
    def __init__(self, debug=False):
        self.debug = debug
        self.reserve = {}.fromkeys(range(1, 5),[])
        # data-structure: reserve = {1:[{0000_2016_0602_0910:'U123'}, {2016_0603_1012_0001:'U123'}]}
        # 0000_2016_06_02_09_10 <=>  0000 2016-06-02 09:00~10:00 (第1bit，0表示取消，1表示预定；后面三位表示场馆),
        # 数据存储：以_分割分别以16进制存储, 其中年用12bit，月4bit，日8bit，小时8bit，场馆3bit，预定位1bit，如上存储为
        #0x_3_7e0_6_02_09_0a = 3839801559306 = 0b110111111000000110000000100000100100001010
        # self.income = {3839801559306: 15}
        self.income = {}
        # 3839801559306 同上
        # 15 <=> income
        self.line = ''

    def charge_at_time(self, wd, t):
        wd = wd+1   # datetime().weekday() 0 <=> 星期一
        # if self.debug: print '星期',wd
        if 1 <= wd <= 5:
            if 9 <= t < 12:
                p = 30
            elif 12 <= t < 18:
                p = 50
            elif 18 <= t < 20:
                p = 80
            elif 20 <= t <= 22:
                p = 60
            else:
                return GYM_CLOSED
        elif 6 <= wd <= 7:
            if 9 <= t < 12:
                p = 40
            elif 12 <= t < 18:
                p = 50
            elif 18 <= t < 20:
                p = 80
            else:
                return GYM_CLOSED
        else:
            return TIME_ILLEGAL
        return p

    def count_charge(self, g, y, m, d, t_s,t_e,cancel=False):
        '''
        c=1 <=> book; c=0 <=> cancel
        :param g:
        :param d:
        :param t_s:
        :param t_e:
        :param c:
        :return:
        '''
        wd = datetime(y,m,d).weekday()
        s = 0
        if not cancel:
            for i in range(t_s, t_e):
                tmp = self.charge_at_time(wd, i)
                if self.debug: print i,':00 计费+1小时', tmp
                if tmp not in (GYM_CLOSED, TIME_ILLEGAL):
                    s += tmp
        else:
            p = self.violation_charge_percent(wd)
            s = self.income[self.make_v(g,y,m,d,t_s,t_e,book=1)] / p
        return s


    def violation_charge_percent(self, wd):
        '''

        :param wd: int[1-7], weekday
        :return:
        '''
        wd += 1
        if 1 <= wd <= 5:
            percent = 2
        elif 6 <= wd <= 7:
            percent = 4
        else:
            return TIME_ILLEGAL
        return percent


    def do_book(self, uid, g, y, m, d, t_s, t_e, cancel=False):
        '''

        :param g: int(1,2,3,4), gym
        :param y: int, year
        :param m: int, month
        :param d: int, day
        :param t_s: int, start time
        :param t_e: int, end time
        :param cancel: bool, is cancel. False <=> book operation default.
        :return:
        '''
        if g not in range(1,5):
            return GYM_NO_EXIST
        if y not in range(0, 10000) \
                or m not in range(0,13) \
                or d not in range(1,32) \
                or t_s not in range(0,24) \
                or t_e not in range(0,24):
            return TIME_ILLEGAL
        if cancel:
            old_key = self.make_v(g,y,m,d,t_s,t_e,book=1)
            if not {old_key:uid} in self.reserve[g]:
                # 取消预订的请求，必须与之前的预订请求严格匹配，需要匹配的项有⽤户ID
                print('Error: the booking being cancelled does not exist!')
                return
            if old_key not in self.income:
                print('Error: the booking being cancelled does not exist!')
                #print '只能完整取消之前的预订，不能取消部分时间段'
                return False
            # define setbit(x,y) x|=(1<<y) //将X的第Y位置1
            # define clrbit(x,y) x&=~(1<<y) //将X的第Y位清0
            new_key = old_key & ~self.ORDER_BOOK_MASK
            self.income[new_key] = self.count_charge(g,y,m,d,t_s,t_e,cancel=True)
            self.reserve[g].append({new_key:uid})
            del self.income[old_key]
            self.reserve[g].remove({old_key:uid})
            if self.debug: print 'Cancel fee: ', self.income[new_key]

            print('Success: the booking is accepted!')
        else:
            if not self.is_reserved(g, y, m, d, t_s, t_e):
                k = self.make_v(g,y,m,d,t_s,t_e,book=1)
                self.reserve[g].append({k:uid})
                self.income[k] = self.count_charge(g,y,m,d,t_s,t_e)
                print('Success: the booking is accepted!')
                if self.debug: print 'Accepted!!!!', g, y, m, d, t_s, t_e,self.get_info(self.make_v(g,y,m,d,t_s,t_e,book=1))
            else:
                print('Error: the booking conflicts with existing bookings!')

    def is_reserved(self, g, y, m, d, t_s, t_e):
        if not self.reserve[g]:
            return False
        for v,k in self.income.items():
            if not self.is_reserved_v(v):
                continue
            if self.get_year(v) == y and self.get_month(v) == m and self.get_day(v) == d:
                # the same day
                if t_s < self.get_start_hour(v) < t_e or t_s < self.get_end_hour(v) < t_e:
                    if self.debug: print 'is reserved!!!!',g,y,m,d,t_s,t_e,self.get_info(v)
                    return True
        return False
    def get_year(self,v):
        return (v>>28)&0xfff
    def get_month(self,v):
        return (v>>24)&0xf
    def get_day(self,v):
        return (v>>16)&0xff
    def get_start_hour(self, v):
        return (v>>8)&0xff
    def get_end_hour(self, v):
        return v&0xff
    def get_gym(self,v):
        return (v>>40)&0x7
    def is_reserved_v(self, v):
        return v>>43
    def is_canceld_v(self,v):
        return not self.is_reserved_v(v)
    def make_v(self, g, y, m, d, t_s, t_e, book):
        return (( (book<<3) + g) << 40) + (y << 28) + (m << 24) + (d << 16) + (t_s << 8) + t_e
    def get_info(self,v):
        return self.get_gym(v), self.get_year(v),self.get_month(v),self.get_day(v),self.get_start_hour(v),self.get_end_hour(v),self.is_reserved_v(v)
    def stdin_input_handler(self):
        line = raw_input('请输入命令：')
        self.input_handler(line.strip())

    def input_handler(self, line=None):
        '''

        :param line:
        :return:
        '''
        # U123 2016-06-02 20:00~22:00 A
        # U123 2016-06-02 20:00~22:00 A C
        if self.debug:
            print('processing...',line)
        if line is None or line == '':
            self.print_total_income()
            return
        items = line.strip().split(' ')
        if len(items) < 4 or len(items) > 5:
            print('Error: the booking is invalid!')
            return

        uid = items[0]
        year, month, day = items[1].split('-')
        start_hour, end_hour = items[2].split('~')
        month, day = month.lstrip('0'), day.lstrip('0')
        year, month, day = map(int, [year, month, day])

        try:
            i_date = datetime(year, month, day)
            if self.debug: print '星期: ' + str(i_date.weekday()+1)
        except Exception:
            # print('输入日期不正确')
            print('Error: the booking is invalid!')
            print sys.exc_info()[2]
            return

        s_tmp, e_tmp =  start_hour.split(':'), end_hour.split(':')
        start_hour, end_hour = int(s_tmp[0]), int(e_tmp[0])
        if start_hour == end_hour:
            print('Error: the booking is invalid!')
            return

        if s_tmp[1] != '00' or e_tmp[1] != '00':
            # print '时间段的起⽌时间必然为整⼩时'
            print('Error: the booking is invalid!')
            return

        gym = FILEDS_DICT.get(items[3])
        if gym not in range(1,5):
            print('Error: the booking is invalid!')
            # print '预定的场地不存在'
            return

        cancel = False
        if len(items) > 4 and items[4] == 'C':
            cancel = True

        self.do_book(uid,gym, year,month,day,start_hour,end_hour,cancel)


        #
        # 'Error: the booking conflicts with existing bookings!'
        # 'Success: the booking is accepted!'
        # 'Error: the booking being cancelled does not exist!'

    def print_total_income(self):

        # 收⼊汇总
        # ---
        # 场地:A
        # 2016-06-02 09:00~10:00 违约⾦ 15元
        # 2016-06-02 10:00~12:00 60元
        # 2016-06-03 20:00~22:00 120元
        # ⼩计：195元
        #
        # 场地:B
        # 2016-06-04 09:00~10:00 40元
        # ⼩计：40元
        #
        # 场地:C
        # ⼩计：0元
        #
        # 场地:D
        # ⼩计：0元
        # ---
        # 总计: 235元
        msg = {}.fromkeys(range(1,5))
        total = {}.fromkeys(range(1,5),0)
        if self.debug: print self.income
        for k,v in self.income.items():
            if self.debug:
                print 'loop self.income', bin(k),v
            gym = self.get_gym(k)
            year = self.get_year(k)
            month = self.get_month(k)
            day = self.get_day(k)
            start_hour = self.get_start_hour(k)
            end_hour = self.get_end_hour(k)
            cancel = self.is_canceld_v(k)

            if self.debug: print gym, year,month,day, start_hour, end_hour,cancel
            msg_date = datetime(year,month,day,start_hour)
            msg_date_s = msg_date.strftime("%Y-%m-%d %H:%M")
            msg_date_e = datetime(year,month,day,end_hour).strftime("%H:%M")
            if not msg[gym]:
                msg[gym] = {}

            msg[gym] = {time.mktime(msg_date.timetuple()):(' '.join(
                ('~'.join((msg_date_s,msg_date_e)),
                '违约金' if cancel else '',
                 str(v) + '元')))}
            if self.debug: print "收入新纪录：",msg[gym],msg[2]
            total[gym] += v
        if self.debug:print 'total',total
        print '收入汇总'
        print '---'
        # if self.debug: print msg
        i = 0
        for k,v in msg.items():
            if i!=0: print
            print('场地:' + FILEDS_DICT.keys()[FILEDS_DICT.values().index(k)])
            if not v:
                print('小计：0元')
                i += 1
                continue
            items = v.items()
            items.sort()
            for t, l in items:
                # '收⼊记录以时间顺序升序排列'
                print l
                print('小计：' + str(total[k]) + '元')
            i += 1
        print('---')
        print('总计：' + str(sum(total.values())) + '元')


import time
def datetime_to_timestamp(datetime_obj):
    """将本地(local) datetime 格式的时间 (含毫秒) 转为毫秒时间戳
    :param datetime_obj: {datetime}2016-02-25 20:21:04.242000
    :return: 13 位的毫秒时间戳  1456402864242
    """
    local_timestamp = long(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
    return local_timestamp
