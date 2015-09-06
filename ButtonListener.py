__author__ = 'Nate Rees'
import threading
import os
import pifacedigitalio
from sys import exit
from time import sleep
import time
import PlugPoller


class Buttons(threading.Thread):
    cmd = None
    loop = True
    button1Callback = None
    button2Callback = None
    button2LongPressCallback = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.cmd = pifacedigitalio.PiFaceDigital()
        self.loop = True

    def run(self):
        time_pushed = 0
        pushed_1 = False
        pushed_2 = False
        inputs = None
        # toggle button turn relay 1 on
        while self.loop:
            sleep(0.05)
            inputs = self.input_status()
            outputs = self.output_status()
            # print inputs, ' ', outputs
            if inputs[0] == '1' and pushed_1 is not True:
                pushed_1 = True
                if self.button1Callback:  # json callback for button press
                    self.button1Callback('{"Inputs":"' + self.input_status() + '"}')
            if inputs[0] == '0' and pushed_1:
                pushed_1 = False
                self.cmd.relays[0].toggle()
                if self.button1Callback:  # json callback for button press
                    self.button1Callback('{"Outputs":"' + self.output_status() + '"}')
                    self.button1Callback('{"Inputs":"' + self.input_status() + '"}')
            if inputs[1] == '1' and pushed_2 is not True:
                pushed_2 = True
                time_pushed = time.time()
                if self.button2Callback:
                    self.button2Callback('{"Inputs":"' + self.input_status() + '"}')
            if inputs[1] == '0' and pushed_2:
                time_taken = time.time() - time_pushed
                pushed_2 = False
                if(self.button2Callback):
                    self.button2Callback('{"Inputs":"' + self.input_status() + '"}')
                if time_taken < .5:
                    self.cmd.relays[1].toggle()
                    if self.button2Callback:
                        self.button2Callback('{"Outputs":"' + self.output_status() + '"}')
                    time_pushed = 0
                if (time_taken > .5):
                    try:
                        if self.button2LongPressCallback:
                            self.button2LongPressCallback()
                    except:
                        pass
                time_pushed = 0
                # if(self.button2LongPressCallback):
                #    self.button2LongPressCallback()

    def stop(self):
        self.loop = False
        #self.lamps.loop = False


    def output_status(self):
        list1 = self.cmd.output_port.value
        status = '{0:08b}'.format(list1)[::-1]
        return status

    def output_cmd(self, pin, value, local=True):
        self.cmd.leds[pin].value=value
        if self.button2Callback and not local:
            self.button2Callback('{"Outputs":"' + self.output_status() + '"}')
        return self.output_status()


    def input_status(self):
        list1 = self.cmd.input_port.value
        status = '{0:08b}'.format(list1)[::-1]
        return status


def main():
    button = Buttons()
    button.start()
    t = time.time()
    while True:
        sleep(60)
    button.stop()


if __name__ == '__main__':
    main()
