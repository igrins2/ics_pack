### Installation for ics ### 

1. Download "ics_pack" directory from GitHub.


2. Setup the python library

$ cd $HOME/ics_pack/installation
$ sh ics_setup.sh

After setup finished, exit the current terminal, open new terminal


3. Set nfs mount
dcs: server / ics, TelOps: client
(S-192.168.1.11, H-192.168.1.18, K-192.168.1.15)

IGRINS setting directory - $HOME/IGRINS

# dnf install nfs-utils nfs4-acl-tools

# showmount -e 192.168.1.11  //for dcss

# mount -t nfs 192.168.1.11:/home/dcss/DCS/Data $HOME/IGRINS/dcss

# mount | grep nfs

# echo "192.168.1.11:/home/dcss/DCS/Data     $HOME/IGRINS/dcss  nfs     defaults 0 0">>/etc/fstab
# cat /etc/fstab


4. Install rabbitmq server 
$ yum install -y epel-release
$ yum install -y erlang
(yum install -y rabbitmq-server)
$ wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.8.9/rabbitmq-server-3.8.9-1.el7.noarch.rpm
$ sudo rpm --import https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
$ sudo yum install -y rabbitmq-server-3.8.9-1.el7.noarch.rpm

# rabbitmq-plugins enable rabbitmq_management
# systemctl list-unit-files | grep rabbitmq-server
# systemctl enable rabbitmq-server
# systemctl start rabbitmq-server
# rabbitmqctl list_users
# rabbitmqctl add_user "your dcs name" kasi2023
# rabbitmqctl set_user_tags "your dcs name" administrator
# rabbitmqctl list_permissions
# rabbitmqctl delete_user test
# rabbitmqctl set_permissions -p / "your dcs name" ".*" ".*" ".*"

@for reset queue (deleted users)
->rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app

@for firewall
firewall-cmd --permanent --zone=public --add-port=5672/tcp
firewall-cmd --reload

@for registering service
systemctl enable rabbitmq-server

@for starting service
systemctl start rabbitmq-server

@for open tcp port!!
firewall-cmd --permanent --zone=public --add-port=5672/tcp
firewall-cmd --reload


5. Start software

$ sudo systemctl daemon-reload

if simulation:
   $ sh ../ics_pack/run_ics.sh simul
else:
   $ sudo systemctl start subsystem.service
   $ sudo systemctl start InstSeq.service

$ sudo systemctl status subsystem.service
or
$ sudo systemctl status InstSeq.service
-> if some failure, 
   $ sudo systemctl stop InstSeq.service
   $ sudo systemctl stop subsystem.service
   $ sudo systemctl reset-failed (or $ setenforce 0)


after checking "ls -lh" in /ics_pack/installation/run_InstSeq.sh
=> sudo chmod 744 run_InstSeq.sh
after checking "ls -lh" in /ics_pack/installation/run_subsystem.sh
=> sudo chmod 744 run_subsystem.sh

if for observer:
	$ sh ../ics_pack/run_ics.sh obs
elif for engineer:
	$ sh ../ics_pack/run_ics.sh eng
else:	
	$ sh ../ics_pack/run_ics.sh cli

# vi /etc/selinux/config
SELINUX=disabled



