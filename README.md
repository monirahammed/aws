# aws

## setEC2InstanceName.py: Add Name TAG to EC2 Instances via Automation Script 


### During creation of new EC2 instance via auto scaling, we can see the new instances do not have any name TAG.
We need to make sure that all the new instances which do not have Name TAG, we need to name those instance.
The name of  the new EC2 instances will have same name as the Tag Value of "elasticbeanstalk:environment-name". 
Thus we can understand a particular EC2 instance created by which  elasticbeanstalk configuration & name of that EC2 instance.


## How this python script (setEC2InstanceName.py) works:

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



