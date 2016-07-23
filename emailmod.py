import logging
import datetime
import hardwaremod
import os
import subprocess
import emaildbmod
import networkmod
import sensordbmod
import actuatordbmod

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


# GET path ---------------------------------------------
global MYPATH
print "path ",hardwaremod.get_path()
MYPATH=hardwaremod.get_path()

global IPEXTERNALSENT
IPEXTERNALSENT=""

def send_email(user, pwd, recipient, subject, body):

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.quit()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"


def create_htmlopen():

	html = """\
	<html>
	  <head>

	  </head>
	  <body>
	"""
	return html

def create_htmlclose():

	html = """\
	  </body>
	</html>
	"""
	return html

def create_htmlintro():
	
	html = """\
		<h3>This is a report automatically generated by Hydrosystem</h3>
 	   
	"""
	return html




def create_htmladdresses(address1, address2, port):
	
	address1=address1+":"+port
	address2=address2+":"+port
	html = """\

		<p>Hi, below the links for System connection:</p>
		<p></p>
		   <a href="http://""" + address1 + """">link for remote connection </a>
		<p></p>
		<p></p>
		   <a href="http://""" + address2 + """">link for local connection </a>		   
		<p></p>
		<p></p>
	"""
	return html


def create_htmlmatrix(matrixinfo):


	htmlopen = """<table style="width:100%!important" cellpadding="2" cellspacing="1">"""


	htmlheader="""<tr>"""
	for header in matrixinfo[0]:
		htmlheader = htmlheader+ """<th align="center" style="background: #81BEF7; border:0px !important;">"""+  header  +"""</th> """
	htmlheader = htmlheader+ """</tr> """


	htmltable=""
	for row in matrixinfo[1:]:
		htmltable=htmltable + """<tr> """
		for element in row:
			htmltable = htmltable+ """<td align="center" style="background: #2E64FE; border:0px !important;">"""+  element  +"""</td> """
		htmltable = htmltable+ """</tr> """

	htmlclose = """	</table>"""
	html=htmlopen+htmlheader+htmltable+htmlclose

	return html
 
def send_email_html(user, pwd, recipient, subject, html):

	# me == my email address
	# you == recipient's email address
	gmail_user = user
	gmail_pwd = pwd
	me = user
	you=[]
	for address in recipient.split(";"):
		you.append(address.strip())
	print " Sending mail to : ", recipient

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = me
	msg['To'] =", ".join(you)
	#msg.preamble = 'Our family reunion'

	# Create the body of the message HTML version

	# Record the MIME t
	part1 = MIMEText(html, 'html')
	msg.attach(part1)
	
	#retrieve last picture ------------------------------------
	global MYPATH
	folderpath=os.path.join(MYPATH, "static")
	folderpath=os.path.join(folderpath, "hydropicture")
	sortedlist=sorted(os.listdir(folderpath))
	sortedlist.reverse()
	picturefile="static/hydropicture/"+sortedlist[0]
	
	imgfiles=[]
	referencestr=sortedlist[0].split("@")[0]
	for filelist in sortedlist:
		if filelist.split("@")[0]==referencestr:
			picturefile="static/hydropicture/"+filelist
			imgfiles.append(picturefile)
		
	
	for filename in imgfiles:
		# Open the files in binary mode.  Let the MIMEImage class automatically
		# guess the specific image type.
		print "filename " , filename
		fp = open(filename, 'rb')
		img = MIMEImage(fp.read())
		fp.close()
		msg.attach(img)

	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(me, you, msg.as_string())
		server.quit()
		print 'successfully sent the mail'
		logging.info('mail sent succesfully ')
		return True
	except:
		logging.error('failed to send mail')
		print "failed to send mail"
		return False



def send_email_main(address,title,cmd):
	currentdate=datetime.datetime.now().strftime("%y-%m-%d,%H:%M")
	# got credentials here !
	user=emaildbmod.getaddress()
	pwd=emaildbmod.getpassword()
	recipient=address
	subject=title + "  " + currentdate
	ipext=networkmod.get_external_ip()
	global IPEXTERNALSENT
	IPEXTERNALSENT=ipext
	iplocal=networkmod.get_local_ip()
	if ipext=="":
		print "No external IP address, mail is not sent"
		logging.error('Unable to get external IP address, mail is not sent')
		return False
	else:
		print "Try to send mail"
		htmlbody=create_htmlopen()
		htmlbody=htmlbody+create_htmlintro()
		port=str(networkmod.PUBLICPORT)
		if cmd=="mail+info+link":
			htmlbody=htmlbody+create_htmladdresses(ipext, iplocal, port)
		# table with information
		matrixinfo=sensordbmod.sensorsysinfomatrix()
		htmlbody=htmlbody+create_htmlmatrix(matrixinfo)
		matrixinfo=actuatordbmod.sensorsysinfomatrix()
		htmlbody=htmlbody+create_htmlmatrix(matrixinfo)
		htmlbody=htmlbody+create_htmlclose()
			
		issent=send_email_html(user, pwd, recipient, subject, htmlbody)
	return issent
	


def sendallmail():
	usedfor="mailcontrol"
	hwnamelist=hardwaremod.searchdatalist(hardwaremod.HW_FUNC_USEDFOR,usedfor,hardwaremod.HW_INFO_NAME)
	for hwname in hwnamelist:
		sendmail(hwname)
		
def sendmail(hwname):
	address=hardwaremod.searchdata(hardwaremod.HW_INFO_NAME,hwname,hardwaremod.HW_CTRL_MAILADDR)
	print "mail recipient ", address
	title=hardwaremod.searchdata(hardwaremod.HW_INFO_NAME,hwname,hardwaremod.HW_CTRL_MAILTITLE)
	print "mail title " , title
	cmd=hardwaremod.searchdata(hardwaremod.HW_INFO_NAME,hwname,hardwaremod.HW_CTRL_CMD)
	print "mail type " , cmd
	issent=send_email_main(address,title,cmd)
	return issent




if __name__ == '__main__':
	
	"""
	prova email
	"""
	currentdate=datetime.datetime.now().strftime("%y-%m-%d,%H:%M")
	
	user="hydrosys4@gmail.com"
	pwd="hydrosystem"
	recipient="valerio.angelo@gmail.com"
	subject="Today update " + currentdate
	body="sono il testo prova 2"
	#send_email(user, pwd, recipient, subject, body)
	
	ipext=networkmod.get_external_ip()
	iplocal=networkmod.get_local_ip()
	htmlbody=create_html(ipext, iplocal, "5012")	
	print htmlbody
	send_email_html(user, pwd, recipient, subject, htmlbody)
	

