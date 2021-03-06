#!/usr/bin/env python

"""
================================================
AB Electronics UK ADC-DAC Pi Volume Control Daemon
================================================

Change the volume on the Raspberry Pi to a value based on the input voltage
from an ADC-DAC Pi ADC channel.

This code should work with any ADC board based on the MCP3202 from Microchip.

The MCP3202 CS pin should be connected to CE0 (pin 24)
on the Raspberry Pi GPIO header.
"""

from __future__ import absolute_import, division, print_function, \
                                                    unicode_literals

import logging
import math
import signal
import spidev
import sys
import time


"""
=========================
Configuration
=========================
"""

# Audio device name - typical values are 'default' or 'pulse'
DEV_NAME = 'default'

# Audio mixer name - typical values are 'Headphone', 'PCM', 'HDMI' or 'Master'
# For a list of available mixers use the command "amixer scontrols"
MIX_NAME = 'Headphone'

# Volume minimum and maximum as percentages.
# Set VOL_MIN to the lowest level you can hear sound from your system.
# Set VOL_MAX to a level that does not distort the sound from your system.
# VOL_MIN should be 0 or greater.  VOL_MAX should not be greater than 100.
VOL_MIN = 0
VOL_MAX = 100

# Scale - values can be 'linear' or 'logarithmic'
# When scale is set to 'linear' the volume will follow a linear response to match the ADC input.
# When scale is set to 'logarithmic' the volume will follow a logarithmic response compared to the ADC input.

SCALE = "linear"

# ADC channel and SPI CS pin
ADC_CHANNEL = 1
ADC_CS_PIN = 0

# Noise threshold
# The volume will update when the ADC input voltage changes beyond the
# noise threshold value.  Increase this value if the volume updates without
# touching the potentiometer.
NOISE = 20

# Set debug to True to enable logging or False to disable logging.
DEBUG = True

"""
=========================
End of Configuration
=========================
"""

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s - %(message)s')


def debug(str):
    if not DEBUG:
        return
    logger.debug(str)


class ADC(object):
    """
    ADC Class
    Based on the Microchip MCP3202 ADC
    """

    # Define SPI bus
    spiADC = spidev.SpiDev()
    spiADC.open(0, ADC_CS_PIN)
    spiADC.max_speed_hz = (900000)

    def __init__(self):
        """
        Class Constructor
        """

    def read_adc_raw(self, channel):
        """
        Read the raw value from the selected channel on the ADC
        """
        if (channel > 2) or (channel < 1):
            debug('read_adc_voltage: channel out of range')

        raw = self.spiADC.xfer2([1, (1 + channel) << 6, 0])
        ret = ((raw[1] & 0x0F) << 8) + (raw[2])
        return ret

    def dispose(self):
        self.spiADC.close()


class Volume(object):
    """
    Methods for setting the Raspberry Pi audio volume
    """

    def __init__(self):
        if VOL_MIN < 0 or VOL_MIN > 100:
            debug("VOL_MIN out of range 0 to 100")
        if VOL_MAX < 0 or VOL_MAX > 100:
            debug("VOL_MAX out of range 0 to 100")
        if VOL_MIN > VOL_MAX:
            debug("VOL_MIN greater than VOL_MAX")
        self.last = 0
        self.adc = ADC()
        self.new_volume = 0
        self.vol_range = VOL_MAX - VOL_MIN

    def set_volume(self):
        """
        Set the audio volume based on the ADC input voltage
        """

        # get the current ADC voltage
        adc_val = self.adc.read_adc_raw(ADC_CHANNEL)

        # check if the voltage has changed outside of the threshold.
        # this reduces volume changes due to noise on the ADC input
        if (adc_val >= self.last + NOISE or adc_val <= self.last - NOISE):
            self.last = adc_val

            # check if the scale is linear or log
            if (SCALE == 'logarithmic'):
                # calculate a logarithmic value based on the ADC input
                response = 1.1
                a = self.vol_range / ((math.log(4095, response) + 1))
                if adc_val < 1: adc_val = 1
                self.new_volume = ((math.log(adc_val, response) + 1) * a) + VOL_MIN                
            else:
                # calculate a linear value based on the ADC input
                self.new_volume = ((adc_val / 4095) * (self.vol_range)) + VOL_MIN

            # check the new volume is within the range 0 to 100
            if self.new_volume < 1: self.new_volume = 0
            if self.new_volume > 100: self.new_volume = 100

            vol_str = "{}%".format(int(self.new_volume)) 
            debug(vol_str)
            # set the volume using the amixer command
            from subprocess import call
            call(['amixer', '-D', DEV_NAME, 'sset', MIX_NAME, vol_str])

    def dispose(self):
        self.adc.dispose()
        del self.adc


if __name__ == "__main__":
    def daemon_exit(args, b):
        debug("Exiting ADC Volume Control")
        vol_obj.dispose()
        sys.exit(0)

    vol_obj = Volume()

    signal.signal(signal.SIGINT, daemon_exit)

    while True:
        vol_obj.set_volume()

        # wait 200ms
        time.sleep(0.2)
