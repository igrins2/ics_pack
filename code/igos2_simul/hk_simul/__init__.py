import threading
import socketserver

import os
import time

HK = {}

RIN = 0
RB = 1

VELOCITY_200 = "VT=109226"
VELOCITY_1 = "VT=546"

class MTR(object):
    def __init__(self, motor):
        self.motor = motor
        self._velocity = 0
        self._bit = [0, 0]  #RIN(3), RBl / RIN(2), RBr
        self._p_goal = 0

        self._initializing = False
        self._go = True
        self._zs = False

    def mtr_func(self, data):
        res = None
        for d in data.split("\r"):
            if d:
                res = self.mtr_func1(d)
        res += "\r"
        return res

    def mtr_func1(self, data):
        
        #print("---", self._p_goal, self._p_current, "---")
        
        #-------------------------------------------------
        # set
        if data == "ECHO_OFF":
            self._velocity = 0
            self._p_goal = 0
            self._initializing = True
            
            if self.motor == "ut":
                self._p_current = 150000
            else:
                self._p_current = -150000
            
        elif data.find("VT") >= 0:
            _data = data.split("=")
            if data == VELOCITY_200:
                self._velocity = int(_data[1]) // 50
            else:
                self._velocity = int(_data[1]) // 10
            
            return str(self._velocity)
        
        elif data == "G":
            self._zs = False
            if self._p_goal > self._p_current:
                self._go = True
            else:
                self._go = False
                if self._velocity > 0:
                    self._velocity *= (-1)
            return str(self._go)
        
        elif data.find("PRT") >= 0:
            pos = data.split("=")
            if self._initializing:
                self._p_goal = 0
            else:
                self._p_goal = self._p_current + int(pos[1])
            return str(self._p_goal)
        
        elif data.find("PT") >= 0:                
            pos = data.split("=")
            self._p_goal = int(pos[1])
            return str(self._p_goal)
        
        elif data == "ZS":
            self._zs = True
            return str(self._zs)
        
        elif data == "O=0":
            self._velocity = 0
            self._p_current = 0
            self._initializing = False
            return str(self._p_current)           
        
        #-------------------------------------------------
        # check during moving...
        if data == "RPA":
            #_c_time = time.time() - self._p_time
            self._p_current = self._p_current + self._velocity
            return str(self._p_current)
        
        elif data.startswith("RBt"):
            if abs(abs(self._p_goal) - abs(self._p_current)) < 1000:
                return "0"
            else:
                return "1"
            
        elif data == "RIN(3)" or data == "RIN(2)":
            if self.motor == "ut":
                if self._p_current < 0:
                    self._bit[RIN] = 1
                else:
                    self._bit[RIN] = 0
                    self._p_goal = 0
            else:
                if self._p_current > 0:
                    self._bit[RIN] = 1
                else:
                    self._bit[RIN] = 0
                    self._p_goal = 0        
            
            return str(self._bit[RIN])
            
        elif data == "RBl" or data == "RBr":
            if self.motor == "ut":
                if self._zs == False and self._p_current < 0:
                    self._bit[RB] = 1
                else:
                    self._bit[RB] = 0
            else:
                if self._zs == False and self._p_current > 0:
                    self._bit[RB] = 1
                else:
                    self._bit[RB] = 0
            return str(self._bit[RB])    
        else:
            return ""
        
        


# MTR
com_resp = [('@@@@', 'IPC ONLINE!\r'),
            ('GOSUB1', None),
            ('GOSUB2', None)]

#HK["mtr"] = dict(com_resp=com_resp, default_resp='ok')
for l in ["lt", "ut"]:
    mtr_helper = MTR(l)
    k = "mtr_%s" % l
    HK[k] = dict(com_resp=com_resp,
                 default_resp=mtr_helper.mtr_func)


# PDU

class PDUSimul(object):

    msg0 = ('1 ON\r2 ON\r3 ON\r4 ON\r5 ON\r6 ON\r7 ON\r8 ON\r\r\r'
            'OUTLET 1 {0} ( UNIT#0 J1 )OUTLET-1\r'
            'OUTLET 2 {1} ( UNIT#0 J2 )OUTLET-2\r'
            'OUTLET 3 {2} ( UNIT#0 J3 )OUTLET-3\r'
            'OUTLET 4 {3} ( UNIT#0 J4 )OUTLET-4\r'
            'OUTLET 5 {4} ( UNIT#0 J5 )OUTLET-5\r'
            'OUTLET 6 {5} ( UNIT#0 J6 )OUTLET-6\r'
            'OUTLET 7 {6} ( UNIT#0 J7 )OUTLET-7\r'
            'OUTLET 8 {7} ( UNIT#0 J8 )OUTLET-8\r\r\r')

    def __init__(self):
        self.powers = [1, 1, 1, 1, 1, 1, 1, 1]

    def make_msg(self):
        powers= [["OFF","ON"][i] for i in self.powers]
        print(powers)
        msg = self.msg0.format(*powers)
        return msg

    def pdu_handle(self, data):
        import re
        p_P = re.compile(r"([FN])0(\d+)")

        m = p_P.match(data)
        if m:
            control, ind = m.groups()
            print("pdu recieved", control, ind)
            if control in ["N"]: # turn on
                self.powers[int(ind)-1] = 1
            elif control in ["F"]: # turn off
                self.powers[int(ind)-1] = 0
            else:
                print("Unknown pdu command: ", data)
        else:
            print("Unknown pdu command: ", data)

        return self.make_msg()

_power_msg = ('1 ON\r2 ON\r3 ON\r4 ON\r5 ON\r6 ON\r7 ON\r\r\r'
              'OUTLET 1 ON ( UNIT#0 J1 )OUTLET-1\r'
              'OUTLET 2 ON ( UNIT#0 J2 )OUTLET-2\r'
              'OUTLET 3 ON ( UNIT#0 J3 )OUTLET-3\r'
              'OUTLET 4 ON ( UNIT#0 J4 )OUTLET-4\r'
              'OUTLET 5 ON ( UNIT#0 J5 )OUTLET-5\r'
              'OUTLET 6 ON ( UNIT#0 J6 )OUTLET-6\r'
              'OUTLET 7 ON ( UNIT#0 J7 )OUTLET-7\r'
              'OUTLET 8 ON ( UNIT#0 J8 )OUTLET-8\r\r\r')

com_resp = [('@@@@', 'IPC ONLINE!\r'),
            # ('DN0', _power_msg),
            # ("F0", _power_msg),
            # ("N0", _power_msg),
            ("LO", None)]

pdu_simul = PDUSimul()

HK["pdu"] = dict(com_resp=com_resp,
                 default_resp=pdu_simul.pdu_handle)

# TMC1
com_resp = [('SETP? 1', '+125.000\r\n'),
            ('SETP? 2', '+66.4000\r\n'),
            ('KRDG? A', '+120.798\r\n'),
            ('KRDG? B', '+130.798\r\n'),
            ('HTR? 1', '+000.0\r\n'),
            ('HTR? 2', '+000.0\r\n')]
HK["tmc1"] = dict(com_resp=com_resp, default_resp=None)


# TMC2
com_resp = [('SETP? 1', '+124.000\r\n'),
            ('SETP? 2', '+65.4000\r\n'),
            ('KRDG? A', '+60.0\r\n'),
            ('KRDG? B', '+66.798\r\n'),
            ('HTR? 1', '+000.0\r\n'),
            ('HTR? 2', '+000.0\r\n')]
HK["tmc2"] = dict(com_resp=com_resp, default_resp=None)

# TMC3
com_resp = [('SETP? 1', '+65.4000\r\n'),
            ('SETP? 2', '+66.4000\r\n'),
            ('KRDG? A', '+65.198\r\n'),
            ('KRDG? B', '+75.798\r\n'),
            ('HTR? 1', '+000.0\r\n'),
            ('HTR? 2', '+000.0\r\n')]
HK["tmc3"] = dict(com_resp=com_resp, default_resp=None)

# TM
com_resp = [('KRDG? 1', '+120.81\r\n'),
            ('KRDG? 2', '+62.81\r\n'),
            ('KRDG? 3', '+16.81\r\n'),
            ('KRDG? 4', '+120.81\r\n'),
            ('KRDG? 5', '+35.81\r\n'),
            ('KRDG? 6', '+66.81\r\n'),
            ('KRDG? 7', '+280.81\r\n'),
            ('KRDG? 8', '+280.81\r\n'),
            ('KRDG? 0', '+120.81,+62.81,+16.81,+120.81,+35.81,+66.81,+280.81,+280.81\r\n')]
HK["tm"] = dict(com_resp=com_resp, default_resp=None)

# VGM
com_resp = [('@253PR1?;FF', '@253ACK9.00E+2;FF'),
            ('@253PR2?;FF', '@253ACK1.23E+2;FF'),
            ('@253PR3?;FF', '@253ACK9.42E-2;FF')]
HK["vm"] = dict(com_resp=com_resp, default_resp=None)


class HouseKeepingHandlerBase(socketserver.BaseRequestHandler):

    # class attributes "hks_data", "hks_name" must be defiend by a derivative.

    def _handle_data(self, data):

        com_resp = self.hks_data["com_resp"]
        default_resp = self.hks_data["default_resp"]

        for com, resp in com_resp:
            if data.find(com) == 0:
                return resp

        if callable(default_resp):
            return default_resp(data)

        if default_resp is not None:
            print("returning default response", default_resp)
            return default_resp
        else:
            raise RuntimeError("no response is found in %s: %s",
                               (self.hks_name, data))

    def handle(self):

        print("Starting a %s." % self.hks_name)
        res = self.request.recv(64)
        data = res.decode()
        print("data received %s: [%s] %d" % (self.hks_name, data, len(data)))
        while data.strip():

            try:
                res = self._handle_data(data)
            except RuntimeError:
                import traceback
                traceback.print_exc()
                print("skipping the error")

                res = None

            if res is not None:
                self.request.sendall(res.encode())
                print("response sent %s: [%s]" % (self.hks_name, res))

            res = self.request.recv(64)
            data = res.decode()
            # print("data received %s: [%s]" % (self.hks_name, data))
            print("data received %s: [%s] %d" % (self.hks_name, data, len(data)))

        print("empty data received. closing the loop")


#from .new import classobj
def new_hk_handler(hks_name, hks_data):
    #import types
    kls = type("", (HouseKeepingHandlerBase,),
                       dict(hks_data=hks_data,
                            hks_name=hks_name))
    return kls


# name of the hk and corresponding hks_data key.
hk_name_data = [("lt", "mtr_lt"),
                ("ut", "mtr_ut"),
                ("pdu", "pdu"),
                ("tmc1", "tmc1"),
                ("tmc2", "tmc2"),
                ("tmc3", "tmc3"),
                ("tm", "tm"),
                ("vm", "vm")]


def get_handlers(cfg):
    host_port_list = []
    for hk_name, _ in hk_name_data:
        #host = cfg.get("HK", hk_name+"-ip")
        host = "localhost"
        port = int(cfg.get("HK", hk_name+"-port"))
        host_port_list.append((host, port))

    handler_list = []
    for hk_name, k in hk_name_data:
        hk_type = HK[k]
        handler = new_hk_handler(hk_name, hk_type)
        handler_list.append(handler)

    return host_port_list, handler_list


class ThreadedTCPServer(socketserver.ThreadingMixIn,
                        socketserver.TCPServer):
    pass


def run_server(host_port_list, handler_list):

    servers = []
    for (host, port), handler in zip(host_port_list, handler_list):
        print("(%s) Listening to %s:%d" % (handler.hks_name, host, port))
        server = ThreadedTCPServer((host, port), handler)
        servers.append(server)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_threads = []
    for server in servers:

        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True

        server_threads.append(server_thread)

    for server_thread in server_threads:
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

    input("Press enter to quit the server.")

    for server in servers:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port

    import sys
    from SetConfig import LoadConfig, get_ini_files

    config_dir = sys.argv[1]
    
    fits_list = dict(H="h_fits.list",
                     K="k_fits.list",
                     S="s_fits.list")

    ini_file = config_dir + "/IGRINS/Config/IGRINS_test.ini"
    cfg = LoadConfig(ini_file)

    host_port_list, handler_list = get_handlers(cfg, fits_list)

    run_server(host_port_list, handler_list)
