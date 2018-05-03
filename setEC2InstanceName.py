'''
Script Name	: setEC2InstanceName.py
Author		: Moniruddin Ahammed (base64.b64decode("bW9uaXJhaGFtbWVkQGdtYWlsLmNvbQ==")
Objective	: This Python program will set Name Tag of all the EC2 insatnces in a give region. The Name tag
		  Will be set by Value of Tag name 'elasticbeanstalk:environment-name'

Date		: Wed Nov 22 18:05:20 IST 2017
Prerequisite	: aws python SDK (boto3 module) and aws configuation is already set
		: aws configure is set by command $aws configure  and you need to enter your aws_secret_access_key and
		  aws_access_key_id
'''

import boto3
from pprint import pprint
import sys
import logging
from time import strftime
import argparse



def createLogger(dryrun):
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)



	#for dryrun print the loging information on console
	if dryrun:
		handler = logging.StreamHandler()
		handler.setLevel(logging.INFO)
		formatter = logging.Formatter("%(levelname)s - %(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
	

	# create a logging format and pring logger message in a file for actual run
	if not dryrun:
		handler = logging.FileHandler(strftime("setEC2InstanceName_%H_%M_%m_%d_%Y.log"))
		handler.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)

		logger.addHandler(handler)

	return logger

def getAllInstance(reservation):
	if len(reservation) < 1:
		logger.info("******** NO INSTANCE FOUND, Nothing to do ***************");
		return
	for count in range(len(reservation)):
        	instanceInfo=reservation[count]["Instances"];
		for count in range(len(instanceInfo)):
			getIndividualInstanceInfo(instanceInfo[count]);




def getIndividualInstanceInfo(instanceInfo):
        instanceID=instanceInfo["InstanceId"]
	privateIPAddress=instanceInfo["PrivateIpAddress"];
        ec2Instance=ec2Resource.Instance(instanceID);
        NameTagPresent=False;
	elasticBeanstalkEnvName=False;
	logger.info("+++ Logging Information About InstanceID=%s and PrivateIP=%s", instanceID,privateIPAddress);
        if instanceInfo.has_key("Tags"):
                tags=instanceInfo["Tags"];
                for tag in tags:
                        if tag["Key"] == "Name":
				logger.info("TagName Name=%s and InstanceID=%s", tag["Value"], instanceID);
                                NameTagPresent=True
			if tag["Key"] == "elasticbeanstalk:environment-name":
				if tag["Value"] != '':
					elasticBeanstalkEnvName=tag["Value"];
					logger.info("ElasticBeanStalk ENV Name: %s ", elasticBeanstalkEnvName);


	
	if not NameTagPresent:
		logger.warning("Name tag is not present for instance ID: %s and PrivateIP=%s", instanceID,privateIPAddress);
		if elasticBeanstalkEnvName:
			newTags={'Key':'Name','Value':elasticBeanstalkEnvName}
			createTage(instanceID,newTags,privateIPAddress)
		else:
			logger.error("Can not set Name Tag for PrivateIP=%s,Becasue Name Tag Not present but elasticbeanstalk:environment-name also not present for InstanceId %s",privateIPAddress, instanceID);
	else:
		logger.info("Name TAG Already Present for instanceId %s and PrivateIP=%s, no action is required ",instanceID,privateIPAddress)


		
		



def createTage(instanceID, tags,privateIPAddress):
	logger.info(">>>> Creating NAME TAG for Resource %s, PrivateIP=%s and TAG=%s and runType=%s", instanceID ,privateIPAddress,tags,dryrun)
	try:
		ec2.create_tags(DryRun=dryrun, Resources=[instanceID],Tags=[tags]);
	except Exception as e:
		if 'DryRunOperation' not in str(e):
			logger.error("Error in Execution %s", str(e));
			raise
		else:
			logger.info("Dry Run Success for privateIPAddress=%s, you can proceed for actual run", privateIPAddress)
	



def parseArgument():
	parser=argparse.ArgumentParser(add_help=True)
	parser.add_argument('--aws-region', action="store", required="True",
				help="<enter aws region> <eg : --aws-region=ap-south-1>")
	parser.add_argument('--dryrun', action="store_true" ,
				help="default value is False, for just dryrun enter --dryrun")
	
	args=parser.parse_args()
	aws_region=args.aws_region;
	dryrun=args.dryrun
	return [aws_region,dryrun]

if __name__=="__main__":

	aws_region,dryrun=parseArgument()

	logger=createLogger(dryrun);
	logger.info("******Starting a new execution for all instances in Region %s  and DryRun=%s********", aws_region, dryrun);

	try:
		ec2 = boto3.client('ec2', region_name=aws_region)
		ec2Resource=boto3.resource('ec2',region_name=aws_region);
		response = ec2.describe_instances()
		#pprint(response);
		reservation=response["Reservations"];
		#pprint(reservation)
	except:
		print "Exception !!! ", sys.exc_info()[1];
		logger.fatal("Execution Failed, Exception %s, reason: %s",sys.exc_info()[0],sys.exc_info()[1]);
		sys.exit(1)

	getAllInstance(reservation);



