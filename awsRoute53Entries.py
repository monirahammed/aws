#!/usr/bin/python
'''
Script Name : awsRoute53Entries.py
Author      : Moniruddin Ahammed (base64.b64decode("bW9uaXJhaGFtbWVkQGdtYWlsLmNvbQ=="))
Objective   : This Python program will fetch DNS A records from route53 and will check :
				1) All the corresponding A records and if they are reachable.
				2) The A records of those DNS records is part of our public IP 
				3) Number of A records corresponding to a DNS name


Date        : Mon Dec 19 05:08:59 EST 2016
Prerequisite    : aws python SDK (boto3 module) and aws configuation is already set
        : aws configure is set by command $aws configure  and you need to enter your aws_secret_access_key and
          aws_access_key_id
'''


import boto3
from pprint import pprint
import sys
import logging
from time import strftime
import argparse
import json
import pyping
import requests
import os
import getpass



#send email to below recipients
#toAddress=['example@mydomain.com']

requests.packages.urllib3.disable_warnings()

 


hostedZones={};
allARecordSet=[];
allAvailablePublicIP=[]
allReachableIP={}
inputDNS='inputDNSName.com.';
email_file_name=strftime("route53_email_%H_%M_%m_%d_%Y.log")
route53Error=0


checkDNSEntries={'checkList':[{'name':'subdomainName1.inputDNSName.com.',
			     	'ipCount':3,
			     	 'method':'http'},
			     {'name':'subdomainName2.inputDNSName.com..',
			     	'ipCount':3,
				'method':'http'}
			     ] #make sure you enter a . at the end of name
		}




def createLogger():
        file_logger = logging.getLogger("route53.file")
	file_logger.setLevel(logging.INFO)

	file_handler = logging.FileHandler(strftime("route53_log_file_%H_%M_%m_%d_%Y.log"))
	file_handler.setLevel(logging.INFO)
	file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(file_formatter)
	file_logger.addHandler(file_handler)
    

        email_logger = logging.getLogger("route53.email")
	email_logger.setLevel(logging.INFO)

	email_handler = logging.FileHandler(email_file_name);
	email_handler.setLevel(logging.INFO)
	email_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	email_handler.setFormatter(email_formatter)

        email_logger.addHandler(email_handler)

        return file_logger, email_logger




def getAllIPAddress():
	client = boto3.client('ec2',region_name='eu-central-1')
	regions= client.describe_regions()['Regions'];

	file_logger.info("Fetching All Available Public IP(s) all Regions ");

	for region in regions:
		region_name=region['RegionName']
		client = boto3.client('ec2', region_name=region_name)
		response = client.describe_instances();
		reservation=response["Reservations"]
		file_logger.info("\tFetching All Available Public IP(s) for AWS Region=%s",region_name);

		for count in range(len(reservation)):
			instancesInfo=reservation[count]["Instances"];
			for index in range(len(instancesInfo)):
				#pprint(instance['PublicIpAddress'])
				if instancesInfo[index].has_key('PublicIpAddress'):
	#				pprint(instancesInfo[index]['PublicIpAddress'])
					allAvailablePublicIP.append(instancesInfo[index]['PublicIpAddress']);






def getHostedZoneName():
	client = boto3.client('route53')
	response = client.list_hosted_zones()
	if response['IsTruncated']:
		file_logger.fatal("There more hosted zones, modify the program....Can not Go Ahead ");

	for res in response['HostedZones']:
		zoneId=res['Id'].split('/')[2];
		hostedZones[res['Name']]=zoneId


	

#response = client.list_resource_record_sets(
#    HostedZoneId='string',
#    StartRecordName='string',
#    StartRecordType='SOA'|'A'|'TXT'|'NS'|'CNAME'|'MX'|'NAPTR'|'PTR'|'SRV'|'SPF'|'AAAA'|'CAA',
#    StartRecordIdentifier='string',
#    MaxItems='string'
#)


def sendHttpRequest(ip):
	global route53Error
	url ="http://"+ip
	headers = {
	    'cache-control': "no-cache",
	    }

	try:
		response = requests.request("GET", url, headers=headers, verify=False)
		if response.status_code == requests.codes.ok:
			file_logger.info("\tHTTP Request Success for  URL=%s", url)
			email_logger.info("\tHTTP Request Success for  URL=%s", url)
			return 1;
		else:
			route53Error=1
			file_logger.error("\tHTTP Request Failed, Can not reach URL=%s", url)
			email_logger.error("\tHTTP Request Failed, Can not reach URL=%s", url)
			return 0;
	except Exception as e:
		route53Error=1
		file_logger.error("Exception Occured for HTTP Request of URL=%s, Exception %s", url, str(e))
		email_logger.error("Exception Occured for HTTP Request of URL=%s, Exception %s", url, str(e))
		return 0;
			
	



def getRecordSet(zoneId):
	client = boto3.client('route53')
	recordSets=client.list_resource_record_sets(
		HostedZoneId=zoneId
	)
	return recordSets




def getARecords(recordSets):
	if recordSets['IsTruncated']:
		file_logger.fatal("This program neeeds modification, number of recordSet is more..exit");

	for record in recordSets['ResourceRecordSets']:
		if record['Type'] == 'A'  and record.has_key('ResourceRecords') :
			allARecordSet.append(record)
		

def pingIP(ip):
	global route53Error

	try:
		response=pyping.ping(ip)
		if response.ret_code == 0:
			file_logger.info("\tPING request is Success for URL=%s", ip)
			email_logger.info("\tPING request is Success for URL=%s", ip)
			return 1;
		else:
			route53Error=1;	
			file_logger.error("\tPING request failed for URL=%s", ip)
			email_logger.error("\tPING request failed for URL=%s", ip)
			return 0;
	except Exception as e:
		route53Error=1;	
		file_logger.error("Exception Occured for PING Request of URL=%s, Exception %s", url, str(e))
		email_logger.error("Exception Occured for PING Request of URL=%s, Exception %s", url, str(e))
		return 0;
		
		



def fetchHostZoneARecords(inputDNS):
	for keys in hostedZones.keys():
	#	print keys, hostedZones[keys];
		if keys == inputDNS:
			recordSets= getRecordSet(hostedZones[keys])
			getARecords(recordSets)
		
	


def getAllReachableIPInfo(allARecordSet):
	global route53Error
	for record in allARecordSet:
		dnsName=record['Name'];
		found=False;
		matchRecord={};

		for entry in checkDNSEntries['checkList']:
			if dnsName == entry['name']:
				found=True
				matchRecord=entry
				
		if not found: continue;	

		allReachableIP[dnsName]=[]
		
		file_logger.info("\n\n\t\tChecking IP(s) corresponding to Name Server=%s ....\n", record['Name'])
		email_logger.info("\n\n\t\tChecking IP(s) corresponding to Name Server=%s ....\n", record['Name'])

		ipCount=len(record['ResourceRecords']);
		matchRecordIPCount=matchRecord['ipCount'];
		if ipCount != matchRecordIPCount:
			route53Error=1
			file_logger.error("\tError Number of IP(s)=%s in AWS do not match with Route53 Records for DNS=%s with expected IP Count=%s",ipCount,matchRecord['name'], matchRecordIPCount);
			email_logger.error("\tError Number of IP(s)=%s in AWS do not match with Route53 Records for DNS=%s with expected IP Count=%s",ipCount,matchRecord['name'], matchRecordIPCount);

		
		for ip in record['ResourceRecords']:
			ipAddress=ip['Value'];	
			if ipAddress in allAvailablePublicIP:
				if matchRecord['method'] == 'http':
					if sendHttpRequest(ipAddress):
						allReachableIP[dnsName].append({'ip':ipAddress,'reachable': 1})
					else:
						route53Error=1
						allReachableIP[dnsName].append({'ip':ipAddress,'reachable': 0})
				if matchRecord['method'] == 'ping':
					if pingIP(ipAddress):
						allReachableIP[dnsName].append({'ip':ipAddress,'reachable': 1})
					else:
						route53Error=1
						allReachableIP[dnsName].append({'ip':ipAddress,'reachable': 0})

			else:
				route53Error=1
				file_logger.error("\tSome is spoofing the IP=%s, it does not belong to our IP pool", ip['Value'])
				email_logger.error("\tSome is spoofing the IP=%s, it does not belong to our IP pool", ip['Value'])


def sendEmail(textMsg):
	import smtplib

	# Import the email modules we'll need
	from email.mime.text import MIMEText
	from email.MIMEMultipart import MIMEMultipart	

	fromAddress='Moniruddin Ahammed <moniruddin@xyx.com>'
	#toAddress=['mahammed@lexmark.com','biswdas@lexmark.com', 'ankita.roy@lexmark.com']
	msg=MIMEMultipart()

	if route53Error == 1 :
		msg['Subject'] = 'Route53 Status : Error'
	else:
		msg['Subject'] = 'Route53 Status : Success'
		
	msg['From'] =fromAddress
	msg['To'] = ",".join(toAddress)
	body=str(textMsg)
	msg.attach(MIMEText(body, 'plain'))

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail(fromAddress,toAddress, msg.as_string())
	s.quit()



def writeEmailLogHeader():
	myhost = os.uname()[1]
	userName=getpass.getuser()
	email_logger.info("\n\n\t\t           This Script was executed from Machine=%s by user=%s\n\n", myhost,userName);
	

def readLogFile(file):
	fileData=open(file, 'r').read()
	return fileData




if __name__=="__main__":

	file_logger, email_logger=createLogger();
	writeEmailLogHeader();
	getHostedZoneName()
	getAllIPAddress();
	fetchHostZoneARecords(inputDNS)
	getAllReachableIPInfo(allARecordSet)
	if route53Error == 1:
		sendEmail(readLogFile(email_file_name))


