#!/usr/bin/env python

from smbus import SMBus
import time

def main():
    '''
    Main program function
    '''
    # Define registers values from datasheet
    IODIRA = 0x00  # IO direction A - 1= input 0 = output
    IODIRB = 0x01  # IO direction B - 1= input 0 = output    
    IPOLA = 0x02  # Input polarity A
    IPOLB = 0x03  # Input polarity B
    GPINTENA = 0x04  # Interrupt-onchange A
    GPINTENB = 0x05  # Interrupt-onchange B
    DEFVALA = 0x06  # Default value for port A
    DEFVALB = 0x07  # Default value for port B
    INTCONA = 0x08  # Interrupt control register for port A
    INTCONB = 0x09  # Interrupt control register for port B
    IOCON = 0x0A  # Configuration register
    GPPUA = 0x0C  # Pull-up resistors for port A
    GPPUB = 0x0D  # Pull-up resistors for port B
    INTFA = 0x0E  # Interrupt condition for port A
    INTFB = 0x0F  # Interrupt condition for port B
    INTCAPA = 0x10  # Interrupt capture for port A
    INTCAPB = 0x11  # Interrupt capture for port B
    GPIOA = 0x12  # Data port A
    GPIOB = 0x13  # Data port B
    OLATA = 0x14  # Output latches A
    OLATB = 0x15  # Output latches B

    i2cbus = SMBus(1)  # Create a new I2C bus
    i2caddress = 0x20  # Address of MCP23017 device

    i2cbus.write_byte_data(i2caddress, IOCON, 0x02)  # Update configuration register

    i2cbus.write_word_data(i2caddress, IODIRA, 0xFF00)  # Set Port A as outputs and Port B as inputs

    while (True):
        portb = i2cbus.read_byte_data(i2caddress, GPIOB)  # Read the value of Port B
        print(portb) # print the value of Port B

        i2cbus.write_byte_data(i2caddress, GPIOA, 0x01)  # Set pin 1 to on
        time.sleep(0.5)  # Wait 500ms

        i2cbus.write_byte_data(i2caddress, GPIOA, 0x00)  # Set pin 1 to off
        time.sleep(0.5)  # Wait 500ms


if __name__ == "__main__":
    main()