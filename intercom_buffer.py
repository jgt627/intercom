import sounddevice as sd
import struct                                        # https://python-sounddevice.readthedocs.io
import numpy                                                                    # https://numpy.org/
import argparse                                                                 # https://docs.python.org/3/library/argparse.html
import socket                                                                   # https://docs.python.org/3/library/socket.html
import queue                                                                    # https://docs.python.org/3/library/queue.html
import sys
from intercom import Intercom

class Intercom_buffer(Intercom):

    def init(self, args):
        Intercom.init(self, args)
        self.cl = 0
        self.ce = 1
        self.l = [None]*64
    def run(self):
        sending_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiving_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listening_endpoint = ("0.0.0.0", self.listening_port)
        receiving_sock.bind(listening_endpoint)

        def receive_and_buffer():
            estructura, source_address = receiving_sock.recvfrom(Intercom.max_packet_size)

            tupla = struct.unpack('!%shh' % 2048, estructura)

            cont = tupla[len(tupla)-1]          #obtiene el contador
            a = []                              #transformar la tupla en un ndarray bidimensional
            for x in range(0, 2047, 2):
                tuplaux = (numpy.int16(tupla[x]), numpy.int16(tupla[x+1]))
                a.append(numpy.asarray(tuplaux))
            b = numpy.asarray(a)
            
            
            self.ce += 1
            self.ce %= 64
            self.l[cont] = b
        def record_send_and_play(indata, outdata, frames, time, status):
            
            
            estructura = struct.pack('!%shh' % (indata.size), *indata.flatten('C'), self.ce)

            sending_sock.sendto(estructura, (self.destination_IP_addr, self.destination_port))


            if numpy.all(self.l[self.cl] != None):
                message = self.l[self.cl]
                self.l[self.cl] = None
               
            elif self.l[self.cl] == None: 
                message = numpy.zeros((self.samples_per_chunk, self.number_of_channels), self.dtype)
            
            outdata[:] = numpy.frombuffer(message, numpy.int16).reshape(self.samples_per_chunk, self.number_of_channels)
            self.cl += 1
            self.cl %= 64

            if __debug__:
                sys.stderr.write(".")
                sys.stderr.flush()

        with sd.Stream(samplerate=self.samples_per_second, blocksize=self.samples_per_chunk, dtype=self.dtype, channels=self.number_of_channels, callback=record_send_and_play):
            print('-=- Press <CTRL> + <C> to quit -=-')
            while True:
                receive_and_buffer()


if __name__ == "__main__":
    intercom = Intercom_buffer()
    parser = intercom.add_args()
    args = parser.parse_args()
    intercom.init(args)
    intercom.run()
