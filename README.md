# aws Automation Scripts : 

## setEC2InstanceName.py: Add Name TAG to EC2 Instances via Automation Script 


### During creation of new EC2 instance via auto scaling, we can see the new instances do not have any name TAG.
We need to make sure that all the new instances which do not have Name TAG, we need to name those instance.
The name of  the new EC2 instances will have same name as the Tag Value of "elasticbeanstalk:environment-name". 
Thus we can understand a particular EC2 instance created by which  elasticbeanstalk configuration & name of that EC2 instance.


### How this python script (setEC2InstanceName.py) works:

This script takes the name of aws region for which we need to set the Name of EC2 Instance and another argument --dryrun (optional).
if we mention --dryrun , then it will show what the script will do . But it will not make any actual changes to the EC2 instances.  
if we do not mention --dryrun, then it will make actual changes to the EC2 instances. 
if you want to print privateIPAddress and Name TAG just use --printIP option . It will print only PrivateIP and Name TAG of EC2 instances. will not make any modificaiton to present EC2 instances. 


Prerequisite: 

    Make sure you have installed python boto3 module. This python AWS SDK tool.
    aws configuation is already set.  aws configure is set by command $aws configure and you need to enter your aws_secret_access_key and aws_access_key_id


## How to run the script : 

** $python setEC2InstanceName.py --help **
              

usage: setEC2InstanceName.py [-h] --aws-region AWS_REGION [--dryrun]
[--printIP]

optional arguments:
-h, --help show this help message and exit
--aws-region AWS_REGION     <enter aws region> <eg : --aws-region=ap-south-1>
--dryrun default value is False, for just dryrun enter --dryrun
--printIP default value is False, if you just want to print  PrivateIP and Name Tag use --printIP



## Check awsEC2CheckNTPConfig.py  File 

### Objective:  When a new EC2 instance is created, it has got a default NTP config file and NTP servers is the default one. We want the NTP server name (time sync server) to be as per our requirement. 


Prerequisite: 

    Make sure you have added the aws_access_key_id and aws_secret_access_key via  aws cli config command. 
    you need to add required keys using $ssh-add <keys>  
    run  the script using pythong awsEC2CheckNTPConfig.py
    Always refer the updated script, below attached script may not be always updated one.  
    

### How it Works:   The python program takes a list of AWS region names and for each region :

- 1 Get all the running EC2 instances name, ip address.
- 2 As most of the EC2 has got private IP address and we have some restricted security group for those EC2 , we need to do ssh to bastion servers.
- 3 From bastion servers we do ssh to specific IP address of EC2 instance. 
> ssh -At -i ~/.ssh/testProd.pem  ec2-user@10.110.10.23 ssh -t -oStrictHostKeyChecking=no  -oConnectTimeout=10 -oBatchMode=yes root@10.10.110.10 cat /etc/ntp.conf > /home/mahammed/works/eu-central-1_10.10.50.215.ntp

- 4 we copy all the the NTP config file in our local machine from where we run the script and name of the copied ntp file is stored as region_name_IP.ntp
- 5 Our Python program check the contents of each NTP config file and if the NTP server's name is different, we need to modify that server's ntp file.
- 6 The program sends an e-mail to concern users about the success/error with list of servers name that required NTP config file modification. 



--------------------------------------------------------------------------------------------------------------------------
## Automation: Check AWS Route53 entries, get 'A' records list and send E-mail

### Objectives: 

 A script to check DNS for xys.abc.docm.com and sap.dpa.coma.com. The script will ensure that there are

- 1) 3 IP addresses for each.

- 2) Each of those addresses is reachable via ping/http.

- 3) verify that those IPs are part of our pool of our EC2 AWS addresses.

- 4) Send e-mail notification. 


**Our python script will check route53 entries and will send email in below format .  This is for success email .  If there is anything wrong , it will send email with subject "Route53 Status : Error".    Email body will contains detail of error log.** 

##------------------------------------------------------------------------------------------------------------------

## Automation:  copy-aws-docker-apache.sh :  Copy All ECS Apache Docker log files into your local machine for a given AWS Region


**Objective: This bash shell script will copy all the Apache ECS container access.log files into your local machine for a given a AWS region. 



*Make sure you have added all the required keys using the command like $ssh-add .ssh/LPMprod.pem ,(machine from where you are running the script)  for ssh-add error, please see the below comment section.



**How it works: 

 - Get all the Apache ECS instances for a given AWS region and stored the ip list in  a file.

> $aws ec2 describe-instances --region eu-central-1 --query "Reservations[].Instances[].[PrivateIpAddress,PublicIpAddress,Platform,Tags[?Key=='Name'].Value|[0],State.Name]" --output text|grep -v terminated |grep -i apache |cut -f 1 > /root/log_copy/eu-central-1_apache_2018_01_15_01_43_52.lst
- get the container id from each apache EC2 instances. 
- copy the apache access.log file from docker container to docker host machine using docker cp command
- Now using scp with ssh proxy copy the log file from docker host machine to your own local machine
- Delete the log files from docker host machine.  Note we are copying the log file from docker container to docker host machine as we can not copy the log files from docker container to our local machine

