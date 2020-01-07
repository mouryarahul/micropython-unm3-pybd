#! /usr/bin/env python
#
# MicroPython Driver for NM3
#
# This file is part of nm3-micropython-pybd derived from NM3 Python Driver. 
# https://github.com/bensherlock/nm3-micropython-pybd
# https://github.com/bensherlock/nm3-python-driver
#
#
# MIT License
#
# Copyright (c) 2020 Benjamin Sherlock <benjamin.sherlock@ncl.ac.uk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""MicroPython PYBD Example using the NM3 over UART."""

#import network
import json
import os
import pyb
import machine
from unm3_pybd.unm3driver import Nm3
from unm3_pybd.unm3driver import MessagePacket
from unm3_pybd.unm3networksimple import Nm3NetworkSimple



def rtc_callback(unknown):
    # RTC Callback function - Toggle LED
    pyb.LED(2).toggle()


def load_app_config(config_filename='config/app_cfg.json'):
    '''Load Application Configuration from JSON file.
       If file doesn't exist, create the file and save default settings.
    '''
    app_config = None
    try:
        with open(config_filename) as json_config_file:
            app_config = json.load(json_config_file)
    except Exception:
        pass

    return app_config
    
def save_app_config(app_config, config_filename='config/app_cfg.json'):
    '''Save Application Configuration to JSON file.
       If file doesn't exist, create the file.
    '''
    with open(config_filename, 'w') as json_config_file:
        json.dump(app_config, json_config_file)


def default_app_config():
    ''' Get default Application Configuration
    '''
    cfg = { 'network' : { 'gateway' : 7 },
            'sensing' : { 'period_s' : 60 } }
            
    return cfg
    
    
def main():
    # Startup Load Configuration
    app_cfg = load_app_config()
    if not app_cfg:
        app_cfg = default_app_config()
        save_app_config(app_cfg)
        

    # LEDs for indicator
    led_red = pyb.LED(1)
    led_green = pyb.LED(2)
    led_blue = pyb.LED(3)

    # https://forum.micropython.org/viewtopic.php?t=6222
    #usb_connected = pyb.USB_VCP().isconnected()

    #if usb_connected:
    #    led_green.on()
    #else:
    #    led_green.off()



    uart = machine.UART(1, 9600, bits=8, parity=None, stop=1, timeout=1000)
    nm3_modem = Nm3(uart)
    nm3_network = Nm3NetworkSimple(nm3_modem)

    temperature_adc = pyb.ADC(pyb.Pin.board.X1)
    light_adc = pyb.ADC(pyb.Pin.board.X2)

    # Set RTC to wakeup at a set interval
    rtc = pyb.RTC()
    rtc.init() # reinitialise - various bugs in firmware at present
    rtc.wakeup(app_cfg['sensing']['period_s'] * 1000) # milliseconds
    message_count = 0


    while True:
        # Main Loop
        # LED On
        led_red.on()
        # 1. Power up external 3V3 regulator
        pyb.Pin.board.EN_3V3.on()
        # 2. Take sensor readings on ADC
        temperature_val = temperature_adc.read()
        light_val = light_adc.read()
        # 3. Build nm3 message
        message_string = 'Count=' + '{:04d}'.format(message_count) + ' Temperature=' + '{:04d}'.format(temperature_val) + ' Light='+ '{:04d}'.format(light_val) 
        message_bytes = message_string.encode('utf-8')
        message_count = message_count + 1
        # 4. Reinitialise the UART
        uart.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=1000)
        # 5a. Send nm3 message - Unicast
        #nm3_modem.send_unicast_message(007, message_bytes)
        # 5b. Send nm3 message - Unicast with Ack plus retry
        #response_time = nm3_modem.send_unicast_message_with_ack(007, message_bytes)
        #retries = 3
        #while response_time < 0 and retries > 0:
        #    retries = retries - 1
        #    response_time = nm3_modem.send_unicast_message_with_ack(007, message_bytes)
        # 5c. Send nm3 message with network
        nm3_network.send_message(app_cfg['network']['gateway'], message_bytes)
        # 6. Power down external 3V3 regulator
        pyb.Pin.board.EN_3V3.off()
        # 7. # Power down UART    
        uart.deinit() # deinit the bus
        # LED On
        led_red.off()
        # 8a. Light Sleep
        pyb.stop()
        # 8b. Deep Sleep - followed by hard reset
        #pyb.standby()
        



    # Disable the external 3.3v regulator (used by SDcard)
    #pyb.Pin.board.EN_3V3.off()

    # Now sleep
    #if not usb_connected:
        #pyb.stop()
        #pyb.standby()
        #machine.lightsleep()
        #machine.deepsleep()


    #usb_connected = False
    #if pyb.usb_mode() is not None:                  # User has enabled CDC in boot.py
    #    usb_connected = pyb.Pin.board.USB_VBUS.value() == 1
    #    if not usb_connected:
    #        pyb.usb_mode(None)                      # Save power


    #wl_ap = network.WLAN(1)
    #wl_ap.active(0)             # shut down the AP

    #wl_ap.config(essid='PYBD')          # set AP SSID
    #wl_ap.config(password='pybd0123')   # set AP password
    #wl_ap.config(channel=6)             # set AP channel
    #wl_ap.active(1)                     # enable the AP

    #wl_ap.status('stations')    # get a list of connection stations
    #wl_ap.active(0)             # shut down the AP


