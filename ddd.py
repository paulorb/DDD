#!/usr/bin/python
#PauloRB 2017
#v1 - POC

from pygdbmi.gdbcontroller import GdbController
from pprint import pprint
from pygdbmi import gdbmiparser
import json
import linecache
import re
import sys
import unicodedata
import sys


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

#Menu
print("DDD - Data Driven Debug - PauloRB 2017");
print("Usage ddd.py [executable name]");
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
if(len(sys.argv) is 2):
	g_executable = str(sys.argv[1])
else:
	print 'Expected [executable name]'
	sys.exit()

# Start gdb process
gdbmi = GdbController()

# Load binary a.out and get structured response
response = gdbmi.write('-file-exec-and-symbols ' + g_executable)
pprint(response)
response = gdbmi.write('-break-insert main')
pprint(response)
response = gdbmi.write('run')
pprint(response)
response = gdbmi.write('next')
originalCodeLine = ""
isFunction = 0;


g_dictVartoVal = {}

def GetLocals():
	g_dictVartoVal.clear()
	response = gdbmi.write('info locals')
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
		ptyperesponse =  gdbmi.write("ptype " + worditem)
		#print ptyperesponse
		if ptyperesponse[1]['type'] == "console":
			#print "Type" + " "+ptyperesponse[1]['payload']
			#print "WordItem " + worditem
			func = (worditem+"(")
			if ("(void)" in ptyperesponse[1]['payload']) or (func in originalCodeLine):
				#print("Function Found")
				return True;
	return False

for i in range(100):
	
	
	for i in range(len(response)):
		if ('payload' in response[i]) and (response[i]['payload'] is not None):
			if ("The program is not being run" in response[i]['payload'] ):
				print "program finished..."
				response = gdbmi.exit()
				sys.exit()
	
	
	if(len(response)>3 and ("No such file or directory" in response[4]['payload']) ):
		print "Stepping out"
		response = gdbmi.write('fin')
	#print response
	if 'frame' in response[4]['payload']:
		if 'line' in response[4]['payload']['frame']:
			#print(response[4]['payload']['frame']['line'])
			if 'fullname' in response[4]['payload']['frame']:
				#print(response[4]['payload']['frame']['fullname'])
				#print "##################################################"
				lineCode = linecache.getline(response[4]['payload']['frame']['fullname'], int(response[4]['payload']['frame']['line']))
				#print lineCode
				originalCodeLine = lineCode
				lineNumber = response[4]['payload']['frame']['line']
				if(CheckForFunction(lineCode) == True):
					isFunction = 1
		#if 'func' in response[4]['payload']['frame']:
			#print(response[4]['payload']['frame']['func'])

	if isFunction == 1:
		print "Step into..."
		response = gdbmi.write('step')
		#print response
		isFunction = 0
	else:
		#print "Next..."
		response = gdbmi.write('next')	
	
	GetLocals()
	#print(g_dictVartoVal)
	#print originalCodeLine
	for key, value in g_dictVartoVal.items():
		#print("Trying to replace " + key + " to " + value + " in " + originalCodeLine)
		pos = originalCodeLine.find(key)
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
			if(validVariable is True and  pos+len(key)+1 < len(originalCodeLine)):
				if( not originalCodeLine[pos+len(key)].isalpha() and not originalCodeLine[pos+len(key)].isdigit()):
					validVariable = True
				else:
					validVariable = False
			if(validVariable is True):
				originalCodeLine = originalCodeLine.replace(key,'\33[31m' + value+ '\33[37m',1)
	print "Line:" +  lineNumber + " " + originalCodeLine.replace("\n","")
	
		
	
	
response = gdbmi.exit()