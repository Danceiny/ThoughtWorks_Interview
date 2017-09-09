class test:
    def __init__(self):
        pass
    def fun(self,line=None):
        print line,id(line)
        N = len(line)
        while N:
            print N,
            N -= 1
        print
t = test()

lines2 = ['U002 2017-08-01 19:00~22:00 A',
          'U003 2017-08-01 18:00~20:00 A',
          'U002 2017-08-01 19:00~22:00 A C',
          'U002 2017-08-01 19:00~22:00 A C',
          'U003 2017-08-01 18:00~20:00 A',
          'U003 2017-08-02 13:00~17:00 B'
          ]
for i in range(len(lines2)):
    t.fun(lines2[i])