'''
Created on 19 Nov 2017

@author: Dominik Marszk
'''

import SocketServer
import globalvars
from threading import Thread

def broadcastToSockets(buf):
    for client in globalvars.tcp_sockets:
        try:
            client.send(buf)
        except:
            # Ignore socket error - socket should be purged by its RX handler
            continue

class TcpHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        print "TCP client connected from {}".format(self.client_address[0])
        self.rxbuf = bytearray()
        globalvars.tcp_sockets.append(self.request)
        while True:
            rxbyte = self.request.recv(1)
            if not rxbyte:
                break
            self.rxbuf.append(rxbyte)
            if rxbyte == '\n':
                if globalvars.verbose > 0:
                    print "{} wrote: {}".format(self.client_address[0], self.rxbuf)
                globalvars.bridge.arduino_port.write(self.rxbuf)
                self.rxbuf = bytearray()
        globalvars.tcp_sockets.remove(self.request)
class serialTcpBridge():
    '''
    Handles TCP/IP - PC Serial port comm
    '''
    arduino_port = None
    def __init__(self, arduino_port):
        self.arduino_port = arduino_port
    
    def uplinkThread(self):
        # read from TCPIP
        # write to Serial
        self.arduino_port.write()
        
    def downlinkThread(self):
        # read from Serial
        serial_buffer = bytearray()
        while True:
#            size_buf = arduino_port.read(2)
#            size = struct.unpack('h', size_buf)
            rxbyte = self.arduino_port.read(1)
            if not rxbyte:
                break
            serial_buffer.append(rxbyte)
            if rxbyte == '\n':
                #write to TCPIP
                if globalvars.verbose > 0:
                    print "OBSW wrote: {}".format(serial_buffer)
                broadcastToSockets(serial_buffer)
                serial_buffer = bytearray()
    
    def runBridge(self):
        self.arduino_port.baudrate = 115200
        self.arduino_port.bytesize = 8
        self.arduino_port.parity = 'N'
        self.arduino_port.stopbits = 1
        if globalvars.verbose > 0:
            print(self.arduino_port)
        serialRxThread = Thread(target = self.downlinkThread)
        print "Starting downlink receiver at port {}".format(self.arduino_port.port)
        serialRxThread.start()
        print "Starting TCP server on {}:{}".format(globalvars.SERVER_HOST, globalvars.SERVER_PORT)
        server = SocketServer.ThreadingTCPServer((globalvars.SERVER_HOST, globalvars.SERVER_PORT), TcpHandler)
        server.serve_forever()
        serialRxThread.join()