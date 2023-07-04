# Installation for ics

1. Download `ics_pack` directory from GitHub.

2. Setup the python library
	```
	$ cd $HOME/ics_pack/installation
	$ sh ics_setup.sh
	```
	After setup finished, exit the current terminal, **open new terminal**!!!
3. Set nfs mount
	- dcs: server / ics, TelOps: client
	
		**S-192.168.1.11, H-192.168.1.18, K-192.168.1.15** (IP address may be changed for the future)

	- IGRINS setting directory - $HOME/IGRINS
		
		- example for dcss
		```
		# dnf install nfs-utils nfs4-acl-tools
		# showmount -e 192.168.1.11
		# mount -t nfs 192.168.1.11:/home/dcss/DCS/Data $HOME/IGRINS/dcss
	
		# mount | grep nfs
	
		# echo "192.168.1.11:/home/dcss/DCS/Data     $HOME/IGRINS/dcss  nfs     defaults 0 0">>/etc/fstab
		# cat /etc/fstab
		```
4. Install rabbitmq server 
	```
	$ yum install -y epel-release
	$ yum install -y erlang
	```
	- yum install -y rabbitmq-server
	```
	$ wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.8.9/rabbitmq-server-3.8.9-1.el7.noarch.rpm
	$ sudo rpm --import https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
	$ sudo yum install -y rabbitmq-server-3.8.9-1.el7.noarch.rpm
	```
	```
	# rabbitmq-plugins enable rabbitmq_management
	# systemctl list-unit-files | grep rabbitmq-server
	# systemctl enable rabbitmq-server
	# systemctl start rabbitmq-server
	# rabbitmqctl list_users
	# rabbitmqctl add_user igos2n kasi2023
	# rabbitmqctl set_user_tags igos2n administrator
	# rabbitmqctl list_permissions
	# rabbitmqctl delete_user test
	# rabbitmqctl set_permissions -p / igos2n ".*" ".*" ".*"
	```
	- for reset queue (deleted users)
	```
	# rabbitmqctl stop_app
	# rabbitmqctl reset
	# rabbitmqctl start_app
	```
	- for firewall
	```
	# firewall-cmd --permanent --zone=public --add-port=5672/tcp
	# firewall-cmd --reload
	```
	- for registering service
	```
	# systemctl enable rabbitmq-server
	```
	- for starting service
	```
	# systemctl start rabbitmq-server
	```
	- for open tcp port!!
	```
	# firewall-cmd --permanent --zone=public --add-port=5672/tcp
	# firewall-cmd --reload
	```
5. Start software
	```
	$ sudo systemctl daemon-reload
	$ sudo systemctl enable subsystem.service
	$ sudo systemctl enable InstSeq.service
	```
	- If simulation
   	```
	$ sh ../ics_pack/run_ics.sh simul
	```
	- Else
   	```
   	$ sudo systemctl start subsystem.service
   	$ sudo systemctl start InstSeq.service
	```
	```
	$ sudo systemctl status subsystem.service
	$ sudo systemctl status InstSeq.service
	```
	- If some failure
	```
   	$ sudo systemctl stop InstSeq.service
   	$ sudo systemctl stop subsystem.service
   	$ sudo systemctl reset-failed
	```
	or 
	```
	$ sudo setenforce 0
	```
	After checking permission
	```
	$ cd .../ics_pack/installation/run_InstSeq.sh
	$ ls -lh
	$ sudo chmod 744 run_InstSeq.sh
	$ sudo chmod 744 run_subsystem.sh
	```
	- For observer
	```
	$ sh ../ics_pack/run_ics.sh obs
	```
	- For engineer
	```
	$ sh ../ics_pack/run_ics.sh eng
	```
	or
	```
	$ sh ../ics_pack/run_ics.sh cli
	```
6. For starting "subsystem.service" and "InstSeq.service" without error automatically when system is rebooting,

	`# vi /etc/selinux/config`
	```
	SELINUX=disabled
	```



