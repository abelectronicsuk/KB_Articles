# AB Electronics UK ADC-DAC Pi Volume Control Daemon

## Introduction

The ADC-DAC Pi Volume Control Daemon uses the ADC input voltage from a MCP3202 ADC to set the audio volume in Linux using the "amixer" command.  This gives you the ability to control the volume level with a potentiometer in the same way as many audio amplifiers.

The daemon samples the ADC input every 200ms and if the voltage has changed more than a predetermined amount the daemon calls the amixer linux command with the new volume level.

The Volume Control Daemon has been tested on the Raspberry Pi 3+ and Raspberry Pi 4 using the HDMI and headphone audio outputs.  It should be compatible with other Raspberry Pi models and audio DAC boards by changing the device and mixer in the configuration.

---
## Hardware Installation

The volume control daemon is designed for use with the ADC-DAC Pi from AB Electronics UK.  The ADC-DAC Pi uses the MCP3202 ADC from Microchip so this program should be compatible with any ADC board based on the MCP3202.

The ADC-DAC Pi requires a voltage between 0 and 3.3V.  You can create this using a 10K linear potentiometer with the outer pins connected to 3.3V and ground and the center tap connected to the ADC input.
```
                            _________
                            |         \
3.3V --------------------===|         |______
                            |         |      \
ADC IN1 -----------------===|         |      |  10K Linear Potentiometer
                            |         |______/
Ground ------------------===|         |
                            |_________/ 
```  
---
## Software Prerequisites

The volume control daemon uses the SPI bus on the Raspberry Pi and the "spidev" python library.

We have a tutorial available on the AB Electronics UK website that explains how to enable the SPI port and install the required python library.  

https://www.abelectronics.co.uk/kb/article/2/spi-and-raspbian-linux-on-a-raspberry-pi  

---
## Software Installation

Download the KBArticles directory from GitHub into your home directory.  
```
cd ~/
git clone https://github.com/abelectronicsuk/KB_Articles.git  
```

Create a bin directory in the current users home directory, copy the adc-volume-control.py into the bin directory and make it executable.  
```
mkdir ~/bin
cd ~/KB_Articles/ADC_Volume_Control
cp adc-volume-control.py ~/bin/adc-volume-control
chmod +x ~/bin/adc-volume-control
```
---
## Configuration


The volume control daemon will need to be configured for your audio setup before use.  

Open the adc-volume-control file in a text editor to change the configuration options.

```
nano ~/bin/adc-volume-control
```

The following configuration options are available.

**DEV_NAME**

Audio device name - typical values are 'default' or 'pulse'  

**MIX_NAME**  

Audio mixer name - typical values are 'Headphone', 'PCM', 'HDMI' or 'Master'  
For a list of available mixers use the command "amixer scontrols"

**VOL_MIN**  
Minimum volume level as a percentage between 0 and 100.  
Set VOL_MIN to the lowest level you can hear sound from your system.  
VOL_MIN should be less than VOL_MAX.  

**VOL_MAX**  
Maximum volume level as a percentage between 0 and 100.  
Set VOL_MAX to a level that does not distort the sound from your system.  
VOL_MAX should be greater than VOL_MIN. 

**ADC_CHANNEL**  
The ADC channel to which the potentiometer or voltage input is connected.  
Channel value can be 1 or 2.  

**ADC_CS_PIN**

SPI CS pin connected to the ADC.  On the ADC-DAC Pi this should be set as 0.
Possible values on the Raspberry Pi are 0 and 1.

**NOISE**

Noise threshold.  The volume will update when the ADC input voltage changes beyond the noise threshold value.  
Increase this value if the volume updates without touching the potentiometer.  

**DEBUG**  
Set debug to True to enable logging or False to disable logging.  
When debug is enabled any changes in volume will be logged.  

---
## Testing the program

Test the program by executing ~/bin/adc-volume-control

```
cd ~/bin
./adc-volume-control
```

If the program runs correctly it should print a response similar to the text below.  When the potentiometer is turned the program will print the new volume value to the console.

```
2020-11-01 18:28:54,760 - 64%
Simple mixer control 'HDMI',0
  Capabilities: pvolume pvolume-joined pswitch pswitch-joined
  Playback channels: Mono
  Limits: Playback -10239 - 400
  Mono: Playback -3430 [64%] [-34.30dB] [on]
```

If you get an error message check the DEV_NAME and MIX_NAME settings are targeting the correct device and mixer.  

---
## Running the program as a systemd service

The program can be run at startup as a daemon using systemd.  Systemd is available on all versions of Raspbian Linux from Jessie onwards.

A daemon service file is included in the ADC_Volume_Control directory.  To install the daemon and enable it run the following commands.

```
cd ~/KB_Articles/ADC_Volume_Control
chmod +x adc-volume.service
sudo cp adc-volume.service /etc/systemd/system
sudo systemctl enable adc-volume.service
sudo systemctl start adc-volume.service
```

**Note:**

If you are logged into Linux using a user other than "pi" you will need to edit the adc-volume.service file to point to the correct directory for the executable.  

You can check the status of the adc-volume service using the following command.

```
sudo systemctl status adc-volume.service
```

To stop the adc-volume service using the following command.

```
sudo systemctl stop adc-volume.service
```

To disable the adc-volume service and stop it from running on startup use the following command.

```
sudo systemctl disable adc-volume.service
```