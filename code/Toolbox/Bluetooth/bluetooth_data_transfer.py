# @file bluetooth_data_transfer.py
# @brief Connect to a device and exchange messages

# Author : Ackermann Gawen
# Last update : 10.06.2021
import bluetooth
import sys
import time

CHATROOM_PORT = 1

MODE_RECEIVE = 0
MODE_SEND = 1

def receiveMessages(port):
    """Listen on a specific port in Radio Frequency Communication mode
    
    port : The port to listen to
    """
    # Initialize the socket for the bluetooth
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(port)
    # Accept the connection and returns a tuple of a socket and the mac address of the device connected to 
    client_sock, address = server_sock.accept()
    
    print("Accepted connection from " + str(address))
    data = client_sock.recv(1024)
    print("received [%s]" % data)


def sendMessageTo(targetBluetoothMacAddress, message, port):
    """Sends a message to a specified device on a specified port
    
    targetBluetoothMacAddress : The device's mac adress
    message : The message to send
    port : The port to emit on
    """
     # Initialize the socket for the bluetooth
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # Connect to the device
    sock.connect((targetBluetoothMacAddress, port))
    # Send the message
    sock.send(message)


def lookUpNearbyBluetoothDevices(hostname):
    """Scan around to find devices
    
    hostname : The hostname of the device to connect to
    
    returns : The mac address of the device to connect to
    """
    nearby_devices = bluetooth.discover_devices()
    mac_add = ""
    for bdaddr in nearby_devices:
        if str(bluetooth.lookup_name(bdaddr)) == hostname:
            mac_add = str(bdaddr)
            print(str(bluetooth.lookup_name(bdaddr)) +
                  " [" + str(bdaddr) + "]")
    return mac_add


# Check if the parameter of the hostname is set 
if len(str(sys.argv[1])) > 0:
    param_hostname = sys.argv[1]
else:
    param_hostname = ""

# Get the mac address from the hostname of a device
mac_address = lookUpNearbyBluetoothDevices(param_hostname)

# mode allows to detect when the device need to listen and when he can send
mode = MODE_SEND
port = CHATROOM_PORT
while True:
    if mode == MODE_RECEIVE:
        receiveMessages(port)
        mode = 1
        time.sleep(1)
    elif mode == MODE_SEND:
        # Get the keyboard inputs
        message = input("msg: ")
        if message == "\quit":
            exit()
        sendMessageTo(mac_address, message, port)
        mode = 0
        time.sleep(1)
