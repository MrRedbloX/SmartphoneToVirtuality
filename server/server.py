from sys import argv
from asyncio import get_running_loop, sleep, run
from netifaces import ifaddresses, interfaces, AF_INET, gateways
from struct import pack
from time import time

port = 4269

TYPE_SCREEN_SIZE = 37
TYPE_SUB = 38
TYPE_UNSUB = 39

LOG_FILE = "./logs.txt"

def get_available_addr():
    gateway_interface = gateways()['default'][AF_INET][1]
    for interface in interfaces():
        try:
            if interface == gateway_interface:
                return ifaddresses(interface)[AF_INET][0]['addr']
        except :
            continue
    return False

class UdpServer:

    def __init__(self, log_data=False):
        self.addrs = []
        self.screen_size = None
        self.log_data = log_data
        
        if self.log_data:
            self.file = open(LOG_FILE, "a")

    def __del__(self):
        if self.log_data:
            self.file.close()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if data[0] == TYPE_SUB:
            print(f"{addr} just subscribed! :)")
            if self.screen_size is not None:
                if self.log_data:
                    self.log(data)
                self.transport.sendto(self.screen_size, addr)
            self.addrs.append(addr)
        elif data[0] == TYPE_UNSUB:
            print(f"{addr} just unsubscribed! :(")
            self.addrs.remove(addr)
        elif data[0] == TYPE_SCREEN_SIZE:
            print(f"{addr} is connnected!")
            self.screen_size = data
        else:
            if self.log_data:
                self.log(data)
            self.send_to_all(data)
    
    def send_to_all(self, data):
        for ad in self.addrs:
            self.transport.sendto(data, ad)

    def error_received(self, err):
        print(err)

    def log(self, data):
        self.file.write(str(time())+" "+data.hex()+"\n")

async def run_server():
    if len(argv) > 1:
        ip = argv[1]
    else:
        ip = input("Enter an address (press enter to let the server choose): ")
        ip = get_available_addr() if ip == "" else ip
        if not ip:
            raise Exception("No available network interface.")

    print(f"Starting UDP server on {ip}:{port}")
    loop = get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(lambda: UdpServer(log_data=False), local_addr=(ip, port))

    try:
        await sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()

if __name__ == '__main__':
    run(run_server())