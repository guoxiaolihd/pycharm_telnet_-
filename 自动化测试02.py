import os
import time
import telnetlib
import datetime
import re


class GjbTool:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None
        self.tn = None
        self.fp = None
        self.target = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S') + '.txt'
        self.pathlog = f'./logs/{self.target}'
        self.pathcontent = f'./content/{self.target}'

    def telnet_connect(self):
        tn = telnetlib.Telnet(self.host, port=23, timeout=10)
        # tn.set_debuglevel(2)
        # tn.read_until('login'.encode('ascii'))
        tn.expect([b'login:'], 5)
        tn.write((self.username + '\n').encode('ascii'))
        # tn.read_until('password'.encode('ascii'))
        tn.expect([b'Password:'], 5)
        tn.write((self.password + '\n').encode('ascii'))
        return tn

    def get_filename(self, path):
        if not os.path.exists('./logs'):
            os.mkdir('./logs')
        if not os.path.exists('./content'):
            os.mkdir('./content')
        if os.path.isdir(path):
            files_name = []
            for root, dirs, files in os.walk(path):
                if len(files) > 0:
                    for file in files:
                        res = os.path.join(root, file)
                        files_name.append(res)
            return files_name
        else:
            filepath, filename = os.path.split(path)
            return filename

    def send_cmd(self, command):
        s = command + '\n'
        self.tn.write(s.encode('ASCII'))

    def change_cmd(self, command):
        a, b, c = self.tn.expect([b'[root@aic-os:/]#'], 2)
        s = c
        self.send_cmd('cd /apps/gjb_testsuite/src/mutex')
        d, e, f = self.tn.expect([command], 1)
        s = s + f
        self.fp.write(s.decode('ASCII'))

    def main_cmd(self, name):
        ss = ''
        # 发送指令
        self.send_cmd('./' + name)
        # 保存数据
        g, h, i = self.tn.expect([b'[root@aic-os:/apps/gjb_testsuite/src/mutex]#'], 9)
        ss = ss + i.decode('GBK')
        last_line = i.decode('GBK').split('\n')[-1]
        if last_line == '[root@aic-os:/apps/gjb_testsuite/src/mutex]# ':
            self.fp.write(ss)
            time.sleep(1)
        else:
            self.fp.write(ss)
            self.fp.write('time out********' + '\n')
            time.sleep(1)

    def middle_ware(self, path):
        print('welecom to gjbTool test')
        filenames = self.get_filename(path)
        x = 0
        self.tn = self.telnet_connect()
        self.fp = open(self.pathlog, 'a', encoding='utf8')
        self.change_cmd(b'[root@aic-os:/apps/gjb_testsuite/src/mutex]#')
        for filename in filenames:
            x += 1
            if x % 5 == 0:
                self.tn.close()
                self.fp = open(self.pathlog, 'a', encoding='utf8')
            filepath, name = os.path.split(filename)
            print(f'this is {name},connect is {x}')
            self.main_cmd(name)
        self.tn.close()
        time.sleep(1)

        self.fp.close()
        print('this test  is end')

    def deal_with(self):
        print('开始解析处理数据。。。。。。')
        with open(self.pathlog, 'r', encoding='utf8') as fp:
            pass_list = []
            failed_lsit = []
            for line in fp:
                if re.search('\[root@aic-os:/apps/gjb_testsuite/src/mutex]# \./', line):
                    filename = re.search('^\./(.*)$', line.split()[1]).groups(0)[0]
                    filepath = re.search('^.*/apps/(.*)]#$', line.split()[0]).groups(0)[0]
                    pathname = filepath + '/' + filename
                if re.search('^<RSLT>(\.+)\[GJB_PASS]$', line):
                    pass_list.append(pathname)
                if re.search('^<RSLT>(\.+)\[GJB_FAILED]$', line):
                    failed_lsit.append(pathname)

        with open(self.pathcontent, 'w', encoding='utf8') as fp:
            fp.write('GJB_FAILED'.center(80, '*') + '\n')
            for failed in failed_lsit:
                fp.write(failed.center(80, ' ') + '\n')
            fp.write('\n')
            fp.write('GJB_PASS'.center(80, '*') + '\n')
            for pas in pass_list:
                fp.write(pas.center(80, ' ') + '\n')


if __name__ == '__main__':
    gjb_tool = GjbTool('10.4.120.11', 'root', 'root')
    path = r'C:\Users\ASUS\workspace\gjb_testsuite\Release\strip\gjb_testsuite\src\mutex'
    gjb_tool.middle_ware(path)
    gjb_tool.deal_with()
