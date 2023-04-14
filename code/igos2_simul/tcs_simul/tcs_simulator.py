import socket
from contextlib import closing

from .tcs_packets import pad_message


def tcs_info(buffer_file, starting_line=0):
    import itertools
    c = itertools.count()
    with open(buffer_file) as f:
        for l in f:
            c1 = c.next()
            if c1 > starting_line:
                break

        for l in f:
            print(c.next())
            yield l


get_tcs_info = next(tcs_info())


def radec_received(comm, args):
    print("processing", comm, args)
    pass


class ProcessCommand(object):
    def __init__(self, buffer_file):
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
            msg = get_tcs_info()
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


def run_server(host, port, backlog, buffer_file, timeout_in_seconds=0.2):

    process_command = ProcessCommand(buffer_file)

    socket_args = socket.AF_INET, socket.SOCK_STREAM

    with closing(socket.socket(*socket_args)) as s:

        s.bind((host, port))
        s.listen(backlog)

        print("2. TCS running on %s:%d" % (host, port))

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

            while True:
                #print('Wating for data')
                #ready = select.select([conn], [], [], timeout_in_seconds)
                #if ready[0]:
                try:
                    #data = conn.recv(size)
                    data = tcsmon_recv(conn)
                except socket.timeout:
                    if timeout_mode == "GUI":
                        msg = pad_message("gui", get_tcs_info())
                        conn.sendall(msg.encode())
                        print("sent", msg[:40])
                    else:
                        #print("timeout")
                        pass
                else:
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


