#conda activate igos2n

export IGRINS_CONFIG=/IGRINS/TEST/Config/IGRINS.ini,/IGRINS/TEST/Config/IGRINS_test.ini

PYTHONBIN=/home/ics/miniconda3/envs/igos2n/bin/python

source ~/.bash_profile
conda activate igos2n

cd code

case "$1" in
	simul)
	    (cd igos2_simul; $PYTHONBIN run_hk_simulator.py)
            ;;

	sub)
	    (cd SubSystems; $PYTHONBIN start_sub.py)
            ;;

        obs)
	    (cd InstSeq; $PYTHONBIN InstSeq.py)
            ;;       

	eng)
	    (cd EngTools; $PYTHONBIN EngTools_gui.py)
            ;;
	
	cli)
	    (cd HKP; $PYTHONBIN HK_cli .py)
            ;;
         
        *)
            echo $"Usage: $0 {simul|sub|obs|eng|cli}"
            exit 1
esac
