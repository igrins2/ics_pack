import socket
from contextlib import closing
import time
import numpy as np

from .tcs_packets import pad_message

r1 = "  2  1 192 Sun Jul  5 2015(186) 02:32:14.9 +14:27:17.06 -00:05:13.26 2457208.6057 2015.50937  3.58 "
"+14:32:30.32 +30:18:30.5 +14:32:30.35 +30:18:30.4"
r2 = " 2000.00000 - 0: 4:32.73 +14:31:49.79 +30:22:17.1  1.0002   47.30   67.80 -00:05:42.37 +30:27:21.9 +00:00:00.00 +00:00:00.0 +00:00:00.00 +00:00:00.0 -00:00:00.02 +00:00:00.1 +00:00:00.00 +00:00:00.0 +00:00:00.00 +00:00:00.00 +00:00:00.00 +00:00:00.0  107.9709    1.1846   23.52  65.0 85.000000  60.8  1.0002  -71.4     0.0  11.0  181.0  -1.0  -1.0      56492 N    0.000  54751.000   90.0  6 0000000000 0000000000 0000000000 0000000010 0000000000 0200000000 0000000000 0000000000 0000000000 0000000000 00000000 01000110 00000010 11100000 01000111 00000000    -5123597     -762413 0.0148353 0.0034907 0.0001454 0.0000048      17263          0           0    15.041     0.000 0.00000 0.00000 1.00077 1.00000 0.000001454 0 0 0       1 1000000000000000 1 1 1 0 0 2     0.0     0.0     0 130807  107.2   89.0    15.0315     0.0012 0 0 0.0029089    0    0 0 0 0 0 5320.0   0    0.0    0.0    0.0    0.0    0.0 13 0  -2.000   2.000  0     -38121      16632     -51979    -256376         94    -359283   -74.0  -262.7"
  

def tcs_info(buffer_file, starting_line=0):
    import itertools
    c = itertools.count()
    while True:
        try:
            with open(buffer_file) as f:
                for l in f:
                    c1 = c.next()
                    if c1 > starting_line:
                        break

                for l in f:
                    print(c.next())
                    yield l
        except StopIteration:
            pass

# get_tcs_info = tcs_info().next
from astropy import units as u
from astropy.coordinates import SkyCoord

def get_str(ra, dec):
    return "{} {}".format(ra.to_string("h", sep=":",
                                       alwayssign=True, precision=2),
                          dec.to_string("degree", sep=":",
                                        alwayssign=True, precision=1))

from astropy.coordinates.angles import Longitude, Latitude

class TelescopePointing():
    def __init__(self, ra, dec):

        self._update(ra*u.hour, dec*u.degree)

    def _update(self, ra, dec):
        c = SkyCoord(ra=ra, dec=dec, frame='icrs')
        self.c = c
        self.ra = c.ra
        self.dec = c.dec
        
    def move(self, dra, ddec):
        mu = np.cos(self.dec.rad)
        ra = Longitude(self.ra + dra * u.arcsec / mu)
        dec = Latitude(self.dec + ddec * u.arcsec)

        self._update(ra, dec)
        
    def current(self):
        return get_str(self.ra, self.dec)


tel_pointing = TelescopePointing(10.5, 42.5)

def tcs_info_simul():
    while True:
        c1 = tel_pointing.current()
        yield r1+c1+" "+c1+r2

if 0:
    c1 = tel_pointing.c
    print(tel_pointing.current())
    tel_pointing.move(0, 10)
    c2 = tel_pointing.c
    print(tel_pointing.current())

    print(c1.separation(c2))

def radec_received(comm, args):
    if comm == "stepra":
        dra = float(args[0])
        ddec = 0
    elif comm == "stepdec":
        dra = 0.
        ddec = float(args[0])

    #print("processing", comm, dra, ddec)
    tel_pointing.move(dra, ddec)


class ProcessCommand(object):
    def __init__(self, buffer_file=None):
        if buffer_file is None:
            self.get_tcs_info = next(tcs_info_simul())
        else:
            self.buffer_file = buffer_file
            self.get_tcs_info = next(tcs_info(buffer_file))

    def __call__(self, data, response=False):
        #commands = data.decode("ascii").split()
        #indx = data.find("\x00")
        commands = data.split()

        mode = None

        print("commands", commands)

        if not commands:
            comm_msg = "tcs", "-"
        elif commands[:2] == ["gui", "off"]:
            comm_msg = "tcs", "-"
            mode = "GUIOFF"
        elif commands[0] == "gui":
            msg = self.get_tcs_info
            comm_msg = "gui", msg
            mode = "GUI"
            #response = True
        elif commands[0] in ["stepra", "stepdec"]:
            radec_received(commands[0], commands[1:])
            comm_msg = "tcs", "-"
        else:
            comm_msg = "tcs", "-"

        msg = pad_message(*comm_msg)

        print("processed", commands)

        if response:
            return mode, msg
        else:
            return mode, None


def tcsmon_recv(chan):
    #head=chan.recv(7, socket.MSG_WAITALL)
    #code=int(head[3:])
    #leng=get_packet_length(code)
    res = chan.recv(100, socket.MSG_WAITALL)
    data = res.decode()

    indx = data.find('\x00')
    print(data, indx)
    d = data[:indx]

    return d


def run_server(host, port, backlog, buffer_file, timeout_in_seconds=0.01):

    process_command = ProcessCommand(buffer_file)
    get_tcs_info = process_command.get_tcs_info

    socket_args = socket.AF_INET, socket.SOCK_STREAM

    with closing(socket.socket(*socket_args)) as s:

        s.bind((host, port))
        s.listen(backlog)

        print("1. TCS running on %s:%d" % (host, port))

        while 1:

            print("waiting a client to connect")
            # while False:
            #     try:
            #         conn, address = s.accept()
            #     except socket.timeout:
            #         print("timeout")
            #         pass
            #     else:
            #         break

            conn, address = s.accept()

            conn.setblocking(0)
            conn.settimeout(timeout_in_seconds)

            timeout_mode = None  # if mode is "GUI", keep send msg

            last_tcs_sent = time.time()

            while True:
                #print('Wating for data')
                #ready = select.select([conn], [], [], timeout_in_seconds)
                #if ready[0]:
                timeout = False
                try:
                    #data = conn.recv(size)
                    data = tcsmon_recv(conn)
                except socket.timeout:
                    timeout = True
                except:
                    data = ""

                if timeout_mode == "GUI":
                    cur_time = time.time()
                    if cur_time - last_tcs_sent > 0.2:
                        last_tcs_sent = cur_time
                        msg = pad_message("gui", get_tcs_info)
                        conn.sendall(msg.encode())
                        print("sent", msg[:40])

                if not timeout:
                    print('Received: ', data)

                    if not data:
                        print('connection closed')
                        break

                    mode, msg = process_command(data)
                    if mode == "GUIOFF":
                        timeout_mode = None
                    elif mode == "GUI":
                        timeout_mode = "GUI"

                    if msg is not None:
                        conn.sendall(msg.encode())
                        print("sent", msg)

                #time.sleep(0.2)  # delays for 0.2 seconds
                #data = client.recv(size)


