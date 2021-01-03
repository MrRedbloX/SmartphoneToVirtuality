from struct import pack
import socket as sct

PORT = 4269
TYPE_POSITION = 40

class ODUdp:

    def __init__(self, ip, port):
        self.sock = sct.socket(sct.AF_INET, sct.SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def sendto(self, data):
        self.sock.sendto(data, (self.ip, self.port))

    def get_byte_from(self, x, y, z, type_='f'):
        return bytes([TYPE_POSITION]) + bytes(pack(type_, x)) + bytes(pack(type_, y)) + bytes(pack(type_, z))