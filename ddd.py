#!/usr/bin/python
from pygdbmi.gdbcontroller import GdbController
from pprint import pprint
from pygdbmi import gdbmiparser
import json
import linecache
import re
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

# Start gdb process
gdbmi = GdbController()

# Load binary a.out and get structured response
response = gdbmi.write('-file-exec-and-symbols a.out')
pprint(response)
response = gdbmi.write('-break-insert main')
pprint(response)
response = gdbmi.write('run')
pprint(response)
response = gdbmi.write('next')
originalCodeLine = ""
isFunction = 0;
for i in range(100):
	
	#print(response[0])
	#print(response[1])
	#print(response[2])
	#print(response[3])
	#print(response[4])
	
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
				for key in range(len(cppKeywords)):
					lineCode =  re.sub(r"\b["+cppKeywords[key]+"]\b", "", lineCode)
				for keyOp in range(len(cppOperators)):
					lineCode = lineCode.replace(cppOperators[keyOp],' ')
				lineCode = lineCode.replace("  "," ")
				words = lineCode.split(" ")  
				#print lineCode
				#print words
				isFunction = 0
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
							isFunction = 1
							continue
						else:		
							responseItem = gdbmi.write("p " + worditem)
							if responseItem[1]['type'] == "console":
								#print responseItem
								#print worditem + " "+responseItem[1]['payload']
								val = responseItem[1]['payload'].replace("\n","") #remove new line from value
								findequal = val.find("=")
								if findequal != -1:
									val = val[findequal+1:]
								originalCodeLine = originalCodeLine.replace(worditem,'\33[31m' + val + '\33[37m')
								#print originalCodeLine
				print "Line:" + response[4]['payload']['frame']['line'] + " " + originalCodeLine.replace("\n","")
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
	
response = gdbmi.exit()