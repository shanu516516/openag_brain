#!/usr/bin/env python3
import gevent
from openag.modules import *


class Arduino(Module):
    @endpoint
    def cban_get(self, sensor_id):
        return 'get {}'.format(sensor_id)


class Sensor(Module):
    output = Output(DataType.TEST)
    def init(self, device_mod_id: ModuleParameter("ID of the device module"),
            pin: IntegerParameter("The pin to read from")):
        self.device = self.ask(device_mod_id)
        self.pin = pin

    @endpoint
    def _get_pin(self):
        """ Get the pin """
        return self.pin

    @endpoint
    def _set_pin(self, pin: IntegerParameter("The pin to start using")):
        """ Set the pin """
        self.pin = pin
        return self.pin

    get_set_pin = Procedure([_get_pin, _set_pin], 'get set pin')

    def run(self):
        while True:
            response = self.device.cban_get(self.pin)
            self.output.emit(response)
            gevent.sleep(1)

class Persist(Module):
    input = Input(data_type=DataType.TEST)
    def on_input(self, item):
        print(item.value)


sensor = Sensor(2)
arduino = Arduino(1)
persist = Persist(3)
sensor.init(1, 3)
arduino.init()
persist.init()
sensor.output.output_to(persist.input)
threads = []
threads.append(gevent.spawn(arduino.run))
threads.append(gevent.spawn(sensor.run))
threads.append(gevent.spawn(persist.run))
gevent.joinall(threads)