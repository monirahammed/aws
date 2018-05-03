'''
Script Name     : awsEC2CheckNTPConfig.py
Author          : Moniruddin Ahammed  (base64.b64decode("bW9uaXJhaGFtbWVkQGdtYWlsLmNvbQ==")
Objective       : This Python program will check all the EC2 insatnces in a give region for correct NTP config
                  

Date            : Fri Jul  7 06:03:20 EDT 2017
Prerequisite    : aws python SDK (boto3 module) and aws configuation is already set
                : aws configure is set by command $aws configure  and you need to enter your aws_secret_access_key and
                  aws_access_key_id
'''



from pprint import pprint
import sys 
import logging
from time import strftime
import re
import os
import getpass




ssh_ok_ip={}
ssh_error_ip={}
email_file_name=""
logDirPath='/root/NTP/logs'
workDirPath='/root/NTP/works'

toAddress=['xyskj@jksja.com']

ntp_file_loc={'linux': '/etc/ntp.conf'}
ntp_server_identiy={'linux': {'text1': 'server', 'text2':'iburst'}}   #pattern to check inside ntp config file
drift_file='/var/lib/ntp/ntp.drift';

aws_region_list=['eu-central-1','us-east-1','us-east-2']  #list of aws region that will be checked for NTP 
#aws_region_list=['eu-central-1']  #list of aws region that will be checked for NTP 


time_server = {
	'us-east-1' :"10.10.10.10",
	'eu-central-1' : "10.10.10.10",
	'us-east-2' : "prod-aws-server.com|10.10.10.10",
	'ap1' :  "xyz_placeholder"
};


bastion_server={
	'eu-central-1':{'ip': "50.10.101.0",'key_pair_name':'xysprod.pem', 'user': 'ec2-user'},
	'us-east-1':{'ip': "50.123.123.12",'key_pair_name': 'pbcrod.pem', 'user':'ec2-user'},
	'us-east-2':{'ip':"18.12.34.12", 'key_pair_name': 'MAN', 'user': 'ubuntu'}
}



def writeEmailLogHeader():
    myhost = os.uname()[1]
    userName=getpass.getuser()
    email_logger.info("\n\n\t\t           This Script was executed from Machine=%s by user=%s of Region=%s\n\n", myhost,userName,region);




def createLogger(region):
	global email_file_name

	file_logger = logging.getLogger("NTP.file")
	file_logger.setLevel(logging.INFO)
	log_file_name=strftime(logDirPath+'/'+region+"_NTP_log_file_%H_%M_%m_%d_%Y.log")
	file_handler = logging.FileHandler(log_file_name)
	file_handler.setLevel(logging.INFO)
	file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(file_formatter)
	file_logger.addHandler(file_handler)

	email_logger = logging.getLogger("NTP.email")
	email_logger.setLevel(logging.INFO)
	email_file_name=strftime(logDirPath +'/'+region+"_NTP_email_%H_%M_%m_%d_%Y.log")
	email_handler = logging.FileHandler(email_file_name);
	email_handler.setLevel(logging.INFO)
	email_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	email_handler.setFormatter(email_formatter)
	email_logger.addHandler(email_handler)

	return file_logger, email_logger



def createNewNTPfile(fileName):
	# NTP configuration here
	print "Creating a new NTP file: ", fileName
	ntpconfig ="\
#LPM NTP settings \n\
driftfile /var/lib/ntp/ntp.drift \n\
server "+ time_server[region]['ip'] + " iburst \n\
server 0.amazon.pool.ntp.org iburst \n\
server 1.amazon.pool.ntp.org iburst \
"

	writeFile=open(fileName, "w")
	writeFile.write(ntpconfig)
	writeFile.close()


def createDriftFile(driftFile):
	openFile = open(driftFile,'a')
	openFile.close()
	


def checkNTPFile(fileName):
	with open(fileName,'r') as infile:
		for line in infile:
			#print line
			 if checkPatternExists(line):
			 	#print "line Match :", line
				return True
			
	return False


def checkPatternExists(line):
	patternMatch=True
	for text in rePatternToCheck:
		if not re.search(rePatternToCheck[text], line):
			patternMatch=False
	
	return patternMatch
		
	

def createREPattern():
	checkStrings=getNTPServerIdentityText()
	reCompilePattern={}
	for text in checkStrings:
		reCompilePattern[text]=re.compile(checkStrings[text],flags=0)

	reCompilePattern[time_server[region]]=re.compile(time_server[region],flags=0)
	return reCompilePattern

def getNTPServerIdentityText():
	return ntp_server_identiy['linux']


def getNTPConfigFile():
	return ntp_file_loc['linux']


def checkAllNTPFile(region):
	global ntpError
	regionIPFile=workDirPath+'/'+region + "_IP.lst"
	email_logger.info("\n\n\n*********************************************************\n\n")
	with open(regionIPFile, 'r') as IPFile:
		for line in IPFile:
			line=line.strip()
			if ssh_error_ip.has_key(line): continue
			ntpFileName=workDirPath+'/'+region +"_" +line + ".ntp"
			#print ntpFileName
			if not checkNTPFile(ntpFileName):
				ntpError=1
				file_logger.error("We need to modify NTP file for IP=%s",line)
				email_logger.error("We need to modify NTP file for IP=%s",line)


def getRunningECInstance(region):
	regionIPFile=workDirPath+'/'+region + "_IP.lst";
	bastion_server_ip=bastion_server[region]['ip'];

	listCommand="aws ec2 describe-instances --region "+ region + " --query \"Reservations[].Instances[].[PrivateIpAddress,PublicIpAddress,Platform,Tags[?Key=='Name'].Value|[0],State.Name]\" --output text|grep -v terminated |grep -v windows|grep -v " + bastion_server_ip +"| cut -f 1 > "+ regionIPFile 
	print listCommand
	file_logger.info("Get List Of IP Command --> %s", listCommand)
	os.system(listCommand)


def getNTPFileInLocalMachine(regionIPFile):
	global ntpError

	bastion_server_ip=bastion_server[region]['ip'];
	bastion_server_user=bastion_server[region]['user']
	bastion_server_key_pair=bastion_server[region]['key_pair_name']
	bastion_server_ssh_cmd="ssh -At -i ~/.ssh/"+bastion_server_key_pair + "  " + bastion_server_user+"@"+bastion_server_ip;

	with open(regionIPFile,'r') as inputfile:
		for line in inputfile:
			cmdList=[]
			line=line.strip()
			ntpFileName=workDirPath+'/'+region +"_" +line + ".ntp"
			cmd_ec2_user=bastion_server_ssh_cmd + " ssh -t -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes  ec2-user@" + line + " cat /etc/ntp.conf > " + ntpFileName
			cmd_ubuntu=bastion_server_ssh_cmd  + " ssh -t -oStrictHostKeyChecking=no -oConnectTimeout=10 -oBatchMode=yes  ubuntu@" + line + " cat /etc/ntp.conf > " + ntpFileName
			cmd_root=bastion_server_ssh_cmd  + " ssh -t -oStrictHostKeyChecking=no  -oConnectTimeout=10 -oBatchMode=yes root@" + line + " cat /etc/ntp.conf > " + ntpFileName
			cmdList.append(cmd_ec2_user)
			cmdList.append(cmd_ubuntu)
			cmdList.append(cmd_root)
			doSSH(cmdList, line)   #create ssh command for all probable ssh user's name
	    



def doSSH(cmdList,line):
	file_logger.info("*************************  SSH command of IP=%s ******************************",line);
	ssh_cmd_success=0
	ssh_cmd_fail=0
	global ntpError

	for cmd in cmdList:
		file_logger.info("SSH command %s", cmd)
		try:
			retValue=os.system(cmd)
			if retValue != 0:
				ssh_cmd_fail=1
				ssh_error_ip[line]=1
				file_logger.error("Error: Can not do SSH to IP=%s", line)
			else:
				ssh_cmd_success=1
				ssh_ok_ip[line]=1
				print "OK SSH for IP : ", line
				file_logger.info("Success SSH to IP=%s",line)
				break
		except Exception as e:
			ntpError=1
			ssh_cmd_fail=1
			print "Exception occured " + str(e)
			file_logger.error("Error in getting NTP file for IP=%s",line)
			file_logger.error("Exception Occured for  IP=%s , error: %s",line,str(e))


	if not ssh_cmd_success:
			ntpError=1
			email_logger.error("Error: Can not do SSH to IP=%s", line)
	else:
		if line in ssh_error_ip:
			del ssh_error_ip[line]

	return ssh_cmd_success


def sendEmail(textMsg):
    import smtplib

    # Import the email modules we'll need
    from email.mime.text import MIMEText
    from email.MIMEMultipart import MIMEMultipart   

    fromAddress='Moniruddin Ahammed <sjkjak@com>'
    msg=MIMEMultipart()

    if ntpError == 1 : 
        msg['Subject'] = 'AWS NTP Status : Error, ' + " Region=" + region
    else:
        msg['Subject'] = 'AWS NTP Status : Success, ' + " Region=" + region
    
    msg['From'] =fromAddress
    msg['To'] = ",".join(toAddress)
    body=str(textMsg)
    msg.attach(MIMEText(body, 'plain'))

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(fromAddress,toAddress, msg.as_string())
    s.quit()




def readLogFile(file):
	fileData=open(file, 'r').read()
	return fileData


if __name__=="__main__":
	global region


	for reg in aws_region_list:
		global ntpError
		ntpError=0
		region=reg
		if not bastion_server.has_key(region):
			print "This key does not exist in our code, bastion_server dictionary ",region
			continue
		
		file_logger,email_logger=createLogger(region)

		rePatternToCheck=createREPattern();

		writeEmailLogHeader()

		getRunningECInstance(region)
		regionIPFile=workDirPath+'/'+region + "_IP.lst"
		getNTPFileInLocalMachine(regionIPFile);
		checkAllNTPFile(region)

		sendEmail(readLogFile(email_file_name))


		#if not checkNTPFile(getNTPConfigFile()):
		#	print " We need to modify the ntp file "
		#	createNewNTPfile('/home/monir/AWS/testNTP.conf')
		#else:
			#print "NTP file is OK, We do not need to update it"

		#createDriftFile('/home/monir/AWS/testDrift.cfg');
	

	#pprint(getNTPServerIdentityText())
