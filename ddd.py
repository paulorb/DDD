#!/usr/bin/python
#PauloRB 2017
#v1 - POC
#1.1 PRB 11/29/2017 Improved performance

from pygdbmi.gdbcontroller import GdbController
from pprint import pprint
from pygdbmi import gdbmiparser
import json
import linecache
import re
import sys
import unicodedata
import sys
import time

cppKeywords =  ["asm","auto","bool","break","case","catch",
                   "char","class","const","const_cast",
                   "continue","default","delete","do","double",
                   "dynamic_cast","else","enum","explicit",
                   "export","extern","false","float","for",
                   "friend","goto","if","inline","int","long",
                   "main","mutable","namespace","new",
                   "operator","private","protected","public",
                   "register","reinterpret_cast","return",
                   "short","signed","sizeof","static",
                   "static_cast","struct","switch","template",
                   "this","throw","true","try","typedef",
                   "typeid","typename","union","unsigned","using",
                   "virtual","void","volatile","wchar_t","while"]
				   
cppOperators = ["::",
"++",
"--",
"()",
"[]",
".",
"->",
"++",
"--",
"+",
"-",
"!",
"~",
"*",
"&",
".*",
"->*",
"*",
"/",
"%",
"+",
"-",
"<<",
">>",
"<",
"<=",
">",
">=",
"==",
"!=",
"&",
"^",
"|",
"&&",
"||",
"?:",
"=",
"+=",
"-=",
"*=",
"/=",
"%=",
"<<=",
">>=",
"&=",
"^=",
"|=",
",",
";",
"(",
")"]

#Global Vars
g_executable = ""
g_args = ""
g_break = ""

# Start gdb process
gdbmi = GdbController()

#Menu
print("DDD - Data Driven Debug - PauloRB 2017");
print("Usage ddd.py [executable name] --break functionname  --args arguments ");
print("Breakpoint will be set to main (default break in this version) ");
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
if(len(sys.argv) is 2):
	g_executable = str(sys.argv[1])
if(len(sys.argv) > 2):
	useargs = 0
	g_executable = str(sys.argv[1])
	for i in range(2,len(sys.argv)):
		if(useargs==1):
			g_args = g_args+ ' ' +sys.argv[i]
		if(sys.argv[i] == "--args"):
			useargs=1
		if(sys.argv[i] == "--break"):
			print "Breakpoint set: " + sys.argv[i+1]
			g_break = sys.argv[i+1]
			response = gdbmi.write("set breakpoint pending on")
			pprint(response)
			response = gdbmi.write('-break-insert -f ' + g_break )
			pprint(response)
	if(useargs==1):
		print "args: " + g_args;
		response = gdbmi.write('-exec-arguments ' + g_args)
		pprint(response)
			
if(len(sys.argv) < 2):
	print 'Expected [executable name]'
	sys.exit()



# Load binary a.out and get structured response
response = gdbmi.write('-file-exec-and-symbols ' + g_executable)
pprint(response)
if(g_break == ""):
	response = gdbmi.write('-break-insert main')
	pprint(response)
response = gdbmi.write('run')
pprint(response)
response = gdbmi.write('next',timeout_sec=5)
originalCodeLine = ""
isFunction = 0;


g_dictVartoVal = {}

def GetLocals():
	g_dictVartoVal.clear()
	response = gdbmi.write('info locals',timeout_sec=0.05)
	for local in response:
		if ("console" in local['type'] and not u"\\n" in local['payload'] ):
			varToval = local['payload'].split("=")
			#print(local['payload'])
			if(len(varToval) >= 2):
				varName = unicodedata.normalize('NFKD', varToval[0]).encode('ascii','ignore') 
				varVal = unicodedata.normalize('NFKD', varToval[1]).encode('ascii','ignore') 
				g_dictVartoVal[varName] = varVal
		

def CheckForFunction(lineCode):
	#print("CheckForFunction")
	for key in range(len(cppKeywords)):
		lineCode =  re.sub(r"\b["+cppKeywords[key]+"]\b", "", lineCode)
		for keyOp in range(len(cppOperators)):
			lineCode = lineCode.replace(cppOperators[keyOp],' ')
			lineCode = lineCode.replace("  "," ")
			words = lineCode.split(" ")  
	#print(words)
	for worditem in words:
		if worditem == '':
			continue
		if worditem == '\n':
			continue
		ptyperesponse =  gdbmi.write("ptype " + worditem,timeout_sec=0.05)
		#print ptyperesponse
		if ptyperesponse[1]['type'] == "console":
			#print "Type" + " "+ptyperesponse[1]['payload']
			#print "WordItem " + worditem
			func = (worditem+"(")
			if ("(void)" in ptyperesponse[1]['payload']) or (func in originalCodeLine):
				#print("Function Found")
				return True;
	return False

while(1==1):
	

	
	if(len(response)>3 and ("No such file or directory" in response[4]['payload']) ):
		print "Stepping out"
		response = gdbmi.write('fin')
		#print response

	#Verify if program finished
	for i in range(len(response)):
		if ('payload' in response[i]) and (response[i]['payload'] is not None):
			if ("The program is not being run" in response[i]['payload'] ):
				print "program finished..."
				response = gdbmi.exit()
				sys.exit()
			if ("exited with code" in response[i]['payload'] ):
				print "program finished..."
				response = gdbmi.exit()
				sys.exit()
			if ("exited normally" in response[i]['payload'] ):
				print "program finished normally..."
				response = gdbmi.exit()
				sys.exit()	
				
	#print "source"
	#responseFrmes = gdbmi.write('info source')
	#print responseFrmes[3]['payload']
	
	if(len(response)<4):
		response = gdbmi.write('next',timeout_sec=0.05)	
		continue
	
	if 'frame' in response[4]['payload']:
		if 'line' in response[4]['payload']['frame']:
			#print(response[4]['payload']['frame']['line'])
			if 'fullname' in response[4]['payload']['frame']:
				#print(response[4]['payload']['frame']['fullname'])
				#print "##################################################"
				#print("Linha numero:",str(response[4]['payload']['frame']['line']))
				lineCode = linecache.getline(response[4]['payload']['frame']['fullname'], int(response[4]['payload']['frame']['line']))
				#print lineCode
				originalCodeLine = lineCode
				lineNumber = response[4]['payload']['frame']['line']
				if(CheckForFunction(lineCode) == True):
					isFunction = 1
		else:
			print "no line member found"
	else:
		#print "no frame found"
		lineAndCode = response[4]['payload']
		print response
		lineAndCodeansii = unicodedata.normalize('NFKD', lineAndCode).encode('ascii','ignore')
		lineAndCodeSplit = lineAndCodeansii.split("\\t\\t")
		#print lineAndCodeSplit
		if(len(lineAndCodeSplit) < 2):
			response = gdbmi.write('next')	
			continue
		
		lineNumber = lineAndCodeSplit[0]
		originalCodeLine = lineAndCodeSplit[1].replace("\\n","")
		#print originalCodeLine
		#print lineNumber
		if(CheckForFunction(lineCode) == True):
			isFunction = 1
		
		
	if isFunction == 1:
		print "Step into..."
		response = gdbmi.write('step')
		#print response
		isFunction = 0
	else:
		#print "Next..."
		response = gdbmi.write('next',timeout_sec=0.05)	
	
	GetLocals()
	#print(g_dictVartoVal)
	#print originalCodeLine
	for key, value in g_dictVartoVal.items():
		#print("Trying to replace " + key + " to " + value + " in " + originalCodeLine)
		pos = originalCodeLine.find(key.lstrip().rstrip())
		validVariable = True
		#print("Pos= ",pos)
		if(pos is not -1):
			if(pos is not 0):
				#print("Analyzing char " + originalCodeLine[pos-1])
				if( not originalCodeLine[pos-1].isalpha() and not originalCodeLine[pos-1].isdigit()):
					#print("validVariable TRUE")
					validVariable = True
				else:
					#print("validVariable FALSE")
					validVariable = False
			if(validVariable is True and  pos+len(key.lstrip().rstrip())+1 < len(originalCodeLine)):
				if( not originalCodeLine[pos+len(key.lstrip().rstrip())].isalpha() and not originalCodeLine[pos+len(key.lstrip().rstrip())].isdigit()):
					validVariable = True
				else:
					validVariable = False
			if(validVariable is True):
				originalCodeLine = originalCodeLine.replace(key.lstrip().rstrip(),'\33[31m' + value+ '\33[37m',1)
	print "Line:" +  lineNumber + " " + originalCodeLine.replace("\n","").lstrip()
	
		
	
	
response = gdbmi.exit()