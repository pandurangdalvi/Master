# -*- coding: utf-8 -*-
"""
file storage utility
"""

import logging
import os
import os.path
import shutil
import string
from datetime import datetime,date,timedelta
import json

# ///////////////// -- GLOBAL VARIABLES AND INIZIALIZATION --- //////////////////////////////////////////

global DATABASEPATH
DATABASEPATH="database"

# ///////////////// --- END GLOBAL VARIABLES ------







#-- start DB utility--------////////////////////////////////////////////////////////////////////////////////////	
def dbpath(filename):
	return os.path.join(DATABASEPATH, filename)	

def readfiledata(filename,filedata): 
	if os.path.isfile(dbpath(filename)): #file is there
		# read the selected table file
		in_file = open(dbpath(filename),"r")
		lines = in_file.readlines()
		in_file.close()
		del filedata[:]
		#print " ln " , lines
		for ln in lines:
			filedata.append(json.loads(ln))
		#print IOdata[0]["name"]
		return True
	else:
		print "----------------------------------------------------------------------> warning no file ", filename 
		return False
		


def savefiledata(filename,filedata):
# questo possibile lista di dizionario: { 'name':'', 'm':0.0, 'q':0.0, 'lastupdate':'' } #variabile tipo dizionario
	out_file = open(dbpath(filename),"w")
	for line in filedata:
		#jsonStr=json.dumps(line, sort_keys=True, indent=14)
		jsonStr=json.dumps(line, sort_keys=True)
		out_file.write(jsonStr)
		out_file.write("\n")
	out_file.close()

def appendfiledata(filename,filedata):
# questo il possibile dizionario: { 'name':'', 'm':0.0, 'q':0.0, 'lastupdate':'' } #variabile tipo dizionario
	out_file = open(dbpath(filename),"a")
	for line in filedata:
		jsonStr=json.dumps(line)
		out_file.write(jsonStr)
		out_file.write("\n")
	out_file.close()
	
def savechange(filename,searchfield,searchvalue,fieldtochange,newvalue):
	filedata=[]
	readfiledata(filename,filedata)
	# questo il possibile dizionario: { 'name':'', 'm':0.0, 'q':0.0, 'lastupdate':'' } #variabile tipo dizionario
	for line in filedata:
		if line[searchfield]==searchvalue:
			line[fieldtochange]=newvalue
			savefiledata(filename,filedata)
			return True
	return False
	

	
	
def deletefile(filename):
	try:
		os.remove(dbpath(filename))
		return True
	except OSError:
		return False

def copydbfileto(filename,dst):
	try:
		copyfile(dbpath(filename), dst)
		return True
	except OSError:
		return False
	
# utility functions --------------------------------------
	
def searchdata(filename,recordkey,recordvalue,keytosearch):
	IOdata=[]
	readfiledata(filename,IOdata)
	for ln in IOdata:
		if recordkey in ln:
			if ln[recordkey]==recordvalue:
				if keytosearch in ln:
					return ln[keytosearch]	
	return ""


def searchdatalist(filename,recordkey,recordvalue,keytosearch):
	IOdata=[]
	readfiledata(filename,IOdata)
	datalist=[]
	for ln in IOdata:
		if recordkey in ln:
			if ln[recordkey]==recordvalue:
				if keytosearch in ln:
					datalist.append(ln[keytosearch])	
	return datalist



def getfieldinstringvalue(filename,fielditem,stringtofind,valuelist):
	IOdata=[]
	readfiledata(filename,IOdata)
	del valuelist[:]
	for line in IOdata:
		name=line[fielditem]
		if name.find(stringtofind)>-1:
			valuelist.append(name)	
	
	
	
#--end --------////////////////////////////////////////////////////////////////////////////////////		
	
	
if __name__ == '__main__':

	FILENAME='dummy.txt'
	data=[
	{"lastupdate": "", "name": "ECsensor1", "pin": 7, "m": 1.0, "controllercmd": "", "q": 0.0, "IOtype": "di"},
	{"lastupdate": "", "name": "ECsensor1enable", "pin": 4, "m": 1.0, "controllercmd": "", "q": 0.0, "IOtype": "do"},
	{"lastupdate": "", "name": "PHsensor1", "pin": 0, "m": 1.0, "controllercmd": "5", "q": 0.0, "IOtype": "ai"}
	]
	savefiledata(FILENAME,data)
	savechange(FILENAME,"name","ECsensor1","q",2.0)
	filedata=[]
	readfiledata(FILENAME,filedata)
	print filedata





