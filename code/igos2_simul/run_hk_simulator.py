import sys
import os

from SetConfig import LoadConfig, get_ini_files
from hk_simul import get_handlers, run_server

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port

    #config_dir = sys.argv[1]
    #print(config_dir)
    config_dir = "/home/ics/IGRINS/Config"

    '''
    os.environ["IGRINS_CONFIG"] = ",".join([os.path.join(config_dir,
                                                         "IGRINS.ini"),
                                            os.path.join(config_dir,
                                                         "IGRINS_test.ini")])

    ini_files = get_ini_files(env_name="IGRINS_CONFIG",
                              default_file='')
    '''
    ini_files = config_dir + "/IGRINS_test.ini"
    cfg = LoadConfig(ini_files)

    host_port_list, handler_list = get_handlers(cfg)

    run_server(host_port_list, handler_list)
