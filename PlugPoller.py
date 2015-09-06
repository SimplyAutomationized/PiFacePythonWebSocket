__author__ = 'nrees'
import threading
import socket

class PlugPoller(threading.Thread):

    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.connect(ip, port)
        self.status = '0000'
        self.command = '!getstat\r'
        self.loop = True
        self.statusChangeCallback = None
    def connect(self, ip, port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(1)
            self.s.connect((ip, port))
        except:
            pass

    def run(self):
        while self.loop:
            try:
                sleep(.1)
                self.s.send(self.command)
                self.status = str(self.s.recv(4))
                # print "data:{"+self.command,self.status+"}"
            except:
                # print 'plug connection error'
                sleep(5.0)
                self.connect(self.ip, self.port)
                pass
            if (self.command is not '!getstat\r'):
                # print self.command
                self.command = '!getstat\r'

    def getstatus(self):
        return self.status

    def toggleAll(self):
        self.sendcmd('!toggle1\r')
        self.sendcmd('!toggle2\r')
        if self.statusChangeCallback:
            self.statusChangeCallback('{"Lamps":"'+self.getstatus()+'"}')
    def sendcmd(self, c):
        try:
            self.s.send(c)
        except:
            pass
        return self.s.recv(4)
