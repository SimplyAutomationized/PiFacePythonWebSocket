__author__ = 'nrees'
import pifacedigitalio


def switch_pressed(event):
    event.chip.output_pins[event.pin_num].turn_on()

def switch_unpressed(event):
    event.chip.output_pins[event.pin_num].turn_off()

if __name__ == "__main__":
    cmd = pifacedigitalio.PiFaceDigital()
    listener = pifacedigitalio.InputEventListener(chip=cmd)
    listener.register(8, pifacedigitalio.IODIR_FALLING_EDGE, switch_pressed)
    listener.activate()