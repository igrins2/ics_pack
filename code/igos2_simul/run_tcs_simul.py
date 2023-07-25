from tcs_simul import run_server
import Libs.SetConfig as sc

def main():
    import os
    import sys

    #print(sys.argv)
    config_dir = sys.argv[1]
    #config_dir = "/IGRINS/TEST/Config"
    try:
        buffer_file = sys.argv[2]  # "tcsbuf.dat"
    except IndexError:
        buffer_file = None # simul mode

    os.environ["IGRINS_CONFIG"] = ",".join([os.path.join(config_dir,
                                                         "IGRINS.ini"),
                                            os.path.join(config_dir,
                                                         "IGRINS_test.ini")])

    ini_files = sc.get_ini_files(env_name="IGRINS_CONFIG",
                              default_file='')

    cfg = sc.LoadConfig(ini_files)

    host = cfg.get("SC", "tcs-ip")
    port = int(cfg.get("SC", "tcs-port"))
    backlog = 5

    run_server(host, port, backlog, buffer_file=buffer_file)


if __name__ == "__main__":
    main()
