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
import signal
import spidev
import sys
import time

"""
Settings
"""

DEBUG = True

# ADC channel and SPI CS pin
ADC_CHANNEL = 1
ADC_CS_PIN = 0

# Noise threshold
# The volume will update when the ADC input voltage changes beyond the
# noise threshold value.  Increase this value if the volume updates without
# touching the potentiometer.
NOISE = 20

# Volume minimum and maximum as percentages.
# Set VOL_MIN to the lowest level you can hear sound from your system.
# Set VOL_MAX to a level that does not distort the sound from your system.
# VOL_MIN should be 0 or greater.  VOL_MAX should not be greater than 100.
VOL_MIN = 0
VOL_MAX = 100

# Audio device name - typical 'default' or 'pulse'
DEV_NAME = 'default'

# Audio mixer name - typical 'PCM' 'HDMI' or 'Master'
# For a list of available mixers use the command "amixer scontrols"
MIX_NAME = 'HDMI'


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

        :param channel: 1 or 2
        :type channel: int
        :raises ValueError: read_adc_voltage: channel out of range
        :return: raw value from ADC, 0 to 4095
        :rtype: int
        """
        if (channel > 2) or (channel < 1):
            raise ValueError('read_adc_voltage: channel out of range')

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
            new_volume = (((adc_val / 4095) * 100) *
                          ((VOL_MAX - VOL_MIN) / 100)) + VOL_MIN
            vol_str = "{}%".format(int(new_volume))

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
        vol.dispose()
        sys.exit(0)

    vol = Volume()

    signal.signal(signal.SIGINT, daemon_exit)

    while True:
        vol.set_volume()

        # wait 200ms
        time.sleep(0.2)
