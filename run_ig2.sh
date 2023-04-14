#conda activate igos2n

export IGRINS_CONFIG=/IGRINS/TEST/Config/IGRINS.ini,/IGRINS/TEST/Config/IGRINS_test.ini

PYTHONBIN=/home/ics/miniconda3/envs/igos2n/bin/python

case "$1" in
	sub)
	    (cd HKP; $PYTHONBIN start_sub.py)
            ;;

        obs)
	    (cd ObsApp; $PYTHONBIN ObsApp_gui.py 0)
            ;;
         
        obs-simul)
	    (cd ObsApp; $PYTHONBIN ObsApp_gui.py 1)
            ;;

	eng)
	    (cd EngTools; $PYTHONBIN EngTools_gui.py)
            ;;
         
        *)
            echo $"Usage: $0 {sub|obs|obs-simul|eng}"
            exit 1
esac
