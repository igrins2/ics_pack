import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Libs.SetConfig as sc
from hk_simul import get_handlers, run_server

if __name__ == "__main__":
    
    # Port 0 means to select an arbitrary unused port

    #config_dir = sys.argv[1]
    #print(config_dir)
    config_dir = "/home/ics/IGRINS/Config"
    
    # IGRINS.ini simulation->True
    ini_file = config_dir + "/IGRINS.ini"
    cfg = sc.LoadConfig(ini_file)
    cfg.set("MAIN", "simulation", "True")
    sc.SaveConfig(cfg, ini_file)

    # IGRINS_test.ini
    ini_file_test = config_dir + "/IGRINS_test.ini"
    cfg_test = sc.LoadConfig(ini_file_test)

    host_port_list, handler_list = get_handlers(cfg_test)

    run_server(host_port_list, handler_list)
    
    # IGRINS.ini simulation->False
    cfg = sc.LoadConfig(ini_file)
    cfg.set("MAIN", "simulation", "False")
    sc.SaveConfig(cfg, ini_file)
