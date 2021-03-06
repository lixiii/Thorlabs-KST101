# Library to control the stretching jig
# The module needs to be initialised with an init function
import serial
import math
from bcolours import BC
ser = serial.Serial()

# the following variables are obtained from the communication protocol and applies to the KST101
des = 0x50  # generic USB
source = 0x01  # host

# conversion factor is valid only for the ZFS actuator used in the stretching jig
# conversion factor is obtained from the datasheet
ZFS_SCALE_FACTOR = 2184533.33

def init( port = '/dev/serial/by-id/usb-Thorlabs_Stepper_Controller_26001411-if00-port0'):
    """
        Initialisation
        ###############
        WARNING
        The serial port is opened by this function. If the port is successfully opened, ensure that the port is closed before termination. 
    """
    ser.baudrate = 115200
    ser.port = port
    ser.open()
    if ser.is_open:
        print(BC.WARNING + "Serial port is open. Please ensure that port is closed before terminating the program." + BC.ENDC)


def identify():
    """ Identify the controller by asking it to flash its screen. This is primarily used for testing if the connection is successfull"""
    cmdIdentify = bytearray([ 0x23, 0x02, 0, 0, des, source ])
    print(BC.OKGREEN + "Sending command 'MGMSG_MOD_IDENTIFY' to controller. " + BC.ENDC)
    ser.write(cmdIdentify)


def home():
    """Move to home"""
    cmdHome = bytearray([ 0x43, 0x04, 0, 0, des, source ])
    print(BC.HEADER + "Sending command 'MGMSG_MOT_MOVE_HOME' to controller. Waiting for completion response" + BC.ENDC)
    ser.write(cmdHome)
    resp = ser.read(6) # message consists of 6 bytes
    if resp[0] == 0x44 and resp[1] == 0x04:
        print(BC.OKGREEN + "Homing completed successfully." + BC.ENDC)
    else:
        print(BC.FAIL + "Command failed. Controller responds with error. Response received:" + resp.hex() + BC.ENDC)
        raise Exception("Controller Error")


def absMove(position):
    """
        Move to an absolute position
        position should be given in float unit in mm.
    """
    posCount = ZFS_SCALE_FACTOR * position 

    posByteArray = list( int(posCount).to_bytes(4, byteorder="little", signed=True) )
    cmd = bytearray([ 0x53, 0x04, 0x06, 0, des | 0x80, source, 0, 0] + posByteArray )
    print(BC.HEADER + "Sending command 'MGMSG_MOT_MOVE_ABSOLUTE' to controller. Waiting for completion response" + BC.ENDC)
    ser.write(cmd)

    # listen for move complete command
    resp = ser.read(20)
    if resp[0] == 0x64 and resp[1] == 0x04:
        print(BC.OKGREEN + "Positioning completed successfully." + BC.ENDC)
    else:
        print(BC.FAIL + "Command failed. Controller responds with error. Response received:" + resp.hex() + BC.ENDC)
        raise Exception("Controller Error")


def move(position): 
    """Make a relative movement of position in mm."""
    posCount =  ZFS_SCALE_FACTOR * position 

    posByteArray = list( int(posCount).to_bytes(4, byteorder="little", signed=True) )
    cmd = bytearray([ 0x48, 0x04, 0x06, 0, des | 0x80, source, 0, 0] + posByteArray )
    print(BC.HEADER + "Sending relative motion command to controller. Waiting for completion response" + BC.ENDC)
    ser.write(cmd)

    # listen for move complete command
    resp = ser.read(20)
    if resp[0] == 0x64 and resp[1] == 0x04:
        print(BC.OKGREEN + "Positioning completed successfully." + BC.ENDC)
    else:
        print(BC.FAIL + "Command failed. Controller responds with error. Response received:" + resp.hex() + BC.ENDC)
        raise Exception("Controller Error")


def step(posCount): 
    """Make a relative movement of position in encoder counts."""
    posByteArray = list( int(posCount).to_bytes(4, byteorder="little", signed=True) )
    cmd = bytearray([ 0x48, 0x04, 0x06, 0, des | 0x80, source, 0, 0] + posByteArray )
    print(BC.HEADER + "Sending encoder count and relative motion command to controller. Waiting for completion response" + BC.ENDC)
    ser.write(cmd)

    # listen for move complete command
    resp = ser.read(20)
    if resp[0] == 0x64 and resp[1] == 0x04:
        print(BC.OKGREEN + "Positioning completed successfully." + BC.ENDC)
    else:
        print(BC.FAIL + "Command failed. Controller responds with error. Response received:" + resp.hex() + BC.ENDC)
        raise Exception("Controller Error")


def setBacklash(position): 
    '''Change backlash settings'''
    
    posCount =  ZFS_SCALE_FACTOR * position 

    posByteArray = list( int(posCount).to_bytes(4, byteorder="little", signed=True) )
    cmd = bytearray([ 0x3a, 0x04, 0x06, 0, des | 0x80, source, 0, 0] + posByteArray )
    print(BC.HEADER + "Sending backlash settings command to controller. " + BC.ENDC)
    ser.write(cmd)



def closePort():
    ser.close()
