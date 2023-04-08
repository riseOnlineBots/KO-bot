from time import sleep

import psutil

from colorful_text import text


class DeviceValidation:
    physical_address = None
    device_legal = False

    registered_devices = []

    def __init__(self, registered_devices):
        self.registered_devices = registered_devices
        self.physical_address = self.find_connected_network()
        self.device_legal = bool(self.physical_address)

        self.validate()

    def is_device_legal(self):
        return self.device_legal

    def validate(self):
        if not self.is_device_legal():
            for _ in range(5):
                text("BU PROGRAMI CALISTIRAMAZSIN.")

            sleep(5)

            raise SystemExit(0)

    def find_connected_network(self):
        interfaces = psutil.net_if_addrs()

        for interface in interfaces.keys():
            for addr in interfaces[interface]:
                if addr.address in self.registered_devices:
                    return addr.address

        return None
