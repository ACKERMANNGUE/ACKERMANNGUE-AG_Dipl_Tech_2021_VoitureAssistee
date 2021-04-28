import bluetooth
import sys
import time


def receiveMessages():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    port = 1
    server_sock.bind(("", port))
    server_sock.listen(1)

    client_sock, address = server_sock.accept()
    print("Accepted connection from " + str(address))

    data = client_sock.recv(1024)
    print("received [%s]" % data)


def sendMessageTo(targetBluetoothMacAddress, message):
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((targetBluetoothMacAddress, port))
    sock.send(message)


def lookUpNearbyBluetoothDevices(hostname):
    nearby_devices = bluetooth.discover_devices()
    mac_add = ""
    for bdaddr in nearby_devices:
        if str(bluetooth.lookup_name(bdaddr)) == hostname:
            mac_add = str(bdaddr)
            print(str(bluetooth.lookup_name(bdaddr)) +
                  " [" + str(bdaddr) + "]")
    return mac_add


if len(str(sys.argv[0])) > 0:
    hostname_rsp = sys.argv[1]
else:
    hostname_rsp = ""

mac_address = lookUpNearbyBluetoothDevices(hostname_rsp)

mode = 1  # 0 = receive, 1 = send

while True:
    if mode == 0:
        receiveMessages()
        mode = 1
        time.sleep(1)
    elif mode == 1:
        message = input("msg: ")
        if message == "\quit":
            exit()
        sendMessageTo(mac_address, message)
        mode = 0
        time.sleep(1)
