import gatt

LEGO_Hub_Service = "00001623-1212-EFDE-1623-785FEABCD123"
LEGO_Hub_Characteristic = "00001624-1212-EFDE-1623-785FEABCD123"

class AnyDevice(gatt.Device):
        
    def connect_succeeded(self):
        """Print the mac adress of the connected device
        """
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        """Print the mac adress of the device that failed to connect
        """
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        """Print the mac adress of the device disconnected
        """
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
      
    def services_resolved(self):
        """Print the services and its characteristics if they are similar to the Lego Hub UUID
        """
        super().services_resolved()
        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            if service == LEGO_Hub_Service:
                print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
                for characteristic in service.characteristics:
                    if str(characteristic.uuid) == LEGO_Hub_Characteristic:
                        print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))
                


# Initialize the manager with the hci0 adaptater
manager = gatt.DeviceManager(adapter_name='hci0')
# Create the device
device = AnyDevice(mac_address='90:84:2B:50:36:43', manager=manager)
# Connect self to device
device.connect()
# The main loop that is necessary to receive Bluetooth events from the Bluetooth adapter
manager.run()
# It can be stopped by executing the stop() method
