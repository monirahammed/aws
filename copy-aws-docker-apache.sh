#!/bin/bash

#Script Name     : copy-aws-docker-apache.sh
#Author          : Moniruddin Ahammed (base64.b64decode("bW9uaXJhaGFtbWVkQGdtYWlsLmNvbQ=="))

#Objective       : This Python program will copy all the EC2 Apache docker container Access log file
#			into your local file system
#                  
#
#		  Date            : Wed Jan  3 05:10:26 EST 2018
#		  Prerequisite    : and aws configuation is already set
#		                  : aws configure is set by command $aws configure  and you need to enter your aws_secret_access_key and
#				                    aws_access_key_id
#
#


your_log_copy_dir='/root/log_copy'
docker_apache_log_file='/usr/local/apache2/logs/access.log'

declare -a regions=('eu-central-1','us-east-1','us-east-2')

#Create an Hash of Bastion Server for each region
declare -A bastion_servers_ip=([eu-central-1]='50.90.50.8' [us-east-1]='50.12.12.34' [us-east-2]='10.10.10.10')

#bastion server access key for each region
declare -A key_pair_name=([eu-central-1]='AWS-Prod1.pem' [us-east-1]='DBProd.pem' [us-east-2]='test.pem')

execute_command() {
	ssh_cmd=$1
	id=`$ssh_cmd`
	echo -n "$id"
}


run_scp_proxy_cmd() {
	ip=$1
	docker_copied_file=$2
	echo $docker_copied_file
	proxyCommand="scp -o LogLevel=QUIET -oStrictHostKeyChecking=no -i ~/.ssh/$bastion_server_key -o ProxyCommand="'"ssh -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=60'"  -i ~/.ssh/$bastion_server_key -W %h:%p ec2-user@$bastion_server"'" '"ec2-user@$ip:/home/ec2-user/$docker_copied_file $your_log_copy_dir/$docker_copied_file"
	echo "Running SCP command to local machine ...................."
	echo "CMD>>> $proxyCommand"
	echo "......................................................."
	eval "$proxyCommand"
	if [ $? -ne 0 ]
	then 
		echo "ERROR : SCP Command Failed: $proxyCommand"
		return 1
	fi
	return 0
}

remove_temp_apache_file() {
	ip=$1
	user=$2
	file=$3
	ssh_remove_file="ssh -Att  -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes -i ~/.ssh/$bastion_server_key  ec2-user@$bastion_server ssh -tt -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes $user@$ip rm $file "
	echo "Running Temp Apache File Remove from Host Docker Machine................"
	echo "CMD>>> $ssh_remove_file"
	echo "..................................................................."
	eval "$ssh_remove_file"
	if [ $? -ne 0 ]
	then 
		echo "ERROR: Failed to Delete File: $ssh_remove_file "
		return 1
	fi
	return 0
}

get_dockerContainerID_command() {
	ip=$1
	user=$2
	ssh_cmd="ssh -Att  -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes -i ~/.ssh/$bastion_server_key  ec2-user@$bastion_server ssh -tt -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes $user@$ip docker ps|grep -i apache|cut -f 1 -d ' ' "
	echo "$ssh_cmd"
	
}

run_docker_cp_cmd(){
	ip=$1
	user=$2
	containerId=$3
	docker_apache_file=$4
	docker_cp_cmd="ssh -Att  -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes -i ~/.ssh/$bastion_server_key  ec2-user@$bastion_server ssh -tt -o LogLevel=QUIET -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes $user@$ip docker cp ${containerId}:${docker_apache_log_file} ./$docker_apache_file"
	echo "Runing cp command , docker container to host machine ............."
	echo "CMD>>> $docker_cp_cmd"
	echo "...................................................................."
	eval "$docker_cp_cmd"
	if [ $? -ne 0 ]
	then 
		echo "ERROR : Command failed : $docker_cp_cmd "
		return 1
	fi
	return 0
}

read_apache_file() {
	apache_file=$1
	exec 3<$apache_file
	while read -u3 line
	do
		data=$line
		ssh_cmd=$( get_dockerContainerID_command "$data" 'ec2-user' )
		docker_id=$( execute_command "$ssh_cmd" )
		docker_cont_id=$(echo "$docker_id"|tr -d '\r')
		echo "***** DOCKER ID: $docker_cont_id"
		docker_copied_file=$( create_docker_copied_file_name "$line" )
		run_docker_cp_cmd "$data" 'ec2-user' "$docker_cont_id" "$docker_copied_file"
		echo "Docker Apache Log Copied to Host($data):status=$?"
		run_scp_proxy_cmd "$data" "$docker_copied_file" 
		echo "Apache log file copied to local machine, status=$?"
		remove_temp_apache_file "$data" 'ec2-user' "$docker_copied_file"
		echo "Removed Apache File from Host($data): status=$?"


	done 

}


create_docker_copied_file_name() {
	ip=$1
	docker_access_apache_log=$region"_"$ip'_docker_apache_access_'$(date +"%Y_%m_%d_%H_%M_%S").log
	echo "$docker_access_apache_log"

}

get_apache_machines() {
	apacheDocker="aws ec2 describe-instances --region "$region"  --query "' "Reservations[].Instances[].[PrivateIpAddress,PublicIpAddress,Platform,Tags[?Key=='"'Name'""]"'.Value|[0],State.Name]"'" --output text|grep -v terminated |grep -i apache |cut -f 1 > $apache_ip_file"

	echo $apacheDocker
	eval "$apacheDocker"
	if [ $? -ne 0 ]
	then 
		echo "Command Failed, cat not get Apache EC2 Instances : $apacheDocker "
		exit 1
	fi
}





region=$1

if [ ${bastion_servers_ip[$region]} ];
then
	echo "Key exists: $region"
else
	echo "Key does not exists: $region"
	echo "Exiting ........"
	echo "Available regions are ${!bastion_servers_ip[@]}"
	echo "Usage : $0 <any_of_above_AWS_region>"
	exit 1;
fi

bastion_server=${bastion_servers_ip[$region]}
bastion_server_key=${key_pair_name[$region]}
apache_ip_file="$your_log_copy_dir""/"$region'_apache_'$(date +"%Y_%m_%d_%H_%M_%S").lst
#apache_ip_file='eu-central-1_apache_2018_01_11_23_07_28.lst'
echo $apache_ip_file
get_apache_machines
read_apache_file $apache_ip_file

