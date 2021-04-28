import gatt

class AnyDevice(gatt.Device):
        
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def characteristic_value_updated(self, characteristic, value):
        print("Firmware version:", value.decode("utf-8"))
        
    def services_resolved(self):
        super().services_resolved()
        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            if service == "00001623-1212-efde-1623-785feabcd123":
                print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
                for characteristic in service.characteristics:
                    if str(characteristic.uuid) == '00001623-1212-efde-1623-785feabcd123':
                        print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))
                



manager = gatt.DeviceManager(adapter_name='hci0')

device = AnyDevice(mac_address='90:84:2B:50:36:43', manager=manager)
device.connect()
manager.run()

print("disconnected ?")
