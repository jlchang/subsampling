#!/usr/bin/python
from subprocess import Popen, STDOUT
import os
import signal

outputroot = "/cil/shed/sandboxes/jlchang/troubleshooting/output/"

##########USER INPUT##########
#input file must be formatted with labels in all caps, in the order bam, name, epitope, subsampling program (Labeled PROGRAM, enter samtools, picard or michele) and optional beds. Also must be all caps and with no extra whitespace between elements
inputPath = outputroot + "percentCalcInputTest"
fullInputRaw = open(inputPath, "r") #opens full input file
fullInput = fullInputRaw.readlines() #turns input into list by line
fullInput = [i[:-1] for i in fullInput] #removes the \n from the end of each list element

#makes lists of each input value from input file
bams = fullInput[fullInput.index("BAM")+1:fullInput.index("NAME")]
names = fullInput[fullInput.index("NAME")+1:fullInput.index("EPITOPE")]
epitopes = fullInput[fullInput.index("EPITOPE")+1:fullInput.index("PROGRAM")]

#Needed so next time the file is opened doesn't go all weird
fullInputRaw.close()

#saves program and beds, depending on if optional beds are provided
#also makres hasBeds as true or false
if 'BED' in open(inputPath).read():
	hasBeds = True
	programs = fullInput[fullInput.index("PROGRAM")+1:fullInput.index("BED")]
	beds = fullInput[fullInput.index("BED")+1:len(fullInput)]
else:	
	hasBeds = False
	programs = fullInput[fullInput.index("PROGRAM")+1:len(fullInput)]
	

##########GIVEN VALUES AND INITIALIZATION##########
targetSampleVals = [1, 20, 50, 70]
seeds = [1,2,3]

#loops through bams
for i in range(0,len(bams)):
	##########MAKES FLAGSTAT FROM BAM##########
	#Makes directory for flagstats
	flagDirPath = outputroot+"flagstats/"+names[i]+"_"+epitopes[i] #makes path to directory
	print flagDirPath,", 0755"
	os.mkdir(flagDirPath, 0755) #makes directory
	
	#Makes directory for cov and awk if beds are given (not run until last script)
	bedDirPath = outputroot+"bedtools/"+programs[i]+"/"+names[i]+"_"+epitopes[i] #makes path to directory
	os.mkdir(bedDirPath, 0755)
	
	#system call to make flagstat
	flagstatOutputFilepath = outputroot+"flagstats/"+names[i]+"_"+epitopes[i]+"/"+names[i]+"_"+epitopes[i]+"_wholebam.flagstat"
	flagstatOutput = open(flagstatOutputFilepath, "w")
	flagstatSysCall = "source /broad/software/scripts/useuse && use Samtools && samtools flagstat "+bams[i]
	flagstatjob = Popen(flagstatSysCall, stdout=flagstatOutput, stderr=STDOUT, shell=True, preexec_fn=os.setsid)
	flagstatjob.communicate()[0]
#	os.killpg(os.getpgid(flagstatjob.pid), signal.SIGTERM)
	flagstatjobResult = flagstatjob.returncode
	print "flagstatjobResult: "  
	print flagstatjobResult
	flagstatOutput.close()

#	##########CALCULATES TOTAL READS##########
	print flagstatOutputFilepath
	flagstat  = open(flagstatOutputFilepath, "r") #opens flagstat
	print flagstat
	flagstat_list = flagstat.readlines() #saves flagstat as a list
	print flagstat_list
	print "flagstat_list above"
#	print flagstat_list[0]
	rawLine = flagstat_list[1] #saves second element in flagstat list, which is the first line of the flagstat and contains total failed and passed reads (first is samtools pending)
	flagstat.close() #closes flagstat that was read into list

	passedReads = rawLine[:rawLine.find("+")-1] #saves passed reads, everything before the + sign
	failedReads = rawLine[rawLine.find("+")+2:rawLine.find("in total")-1] #saves failed reads, everything after the + sign bt before "in total"
	totalReads = float(passedReads) + float(failedReads) #converts into floats and finds total (NEEDS TO BE FLOAT FOR PERCENT CALCULATION TO WORK)

#	###########SEND COMMAND TO BASH SCRIPT FOR EVERY SIZE AND SEED##########
#	for k in range(1, len(targetSampleVals)+1):
#		#finds percent for each size
#		percent = targetSampleVals[k-1]*1000 / totalReads
#		
#		#prevents major disasters in case of error
#		if percent>1:
#			percent = 1
#
#        	for p in range (1, len(seeds)+1):
#	        	#calls subsampling script for every size AND seed
#			
#			if hasBeds == True:
#				subsampleSysCall = "source /broad/software/scripts/useuse && use UGER && qsub /cil/shed/sandboxes/jlchang/echou/subsampleScripts/picardGeneralSubsetTest.sh "+bams[i]+" "+names[i]+" "+epitopes[i]+" "+targetSampleVals[k-1]+" "+percent+" "+seeds[p-1]+" "+programs[i]+" "+beds[i]
#				
#			else:
#				subsampleSysCall = "source /broad/software/scripts/useuse && use UGER && qsub /cil/shed/sandboxes/jlchang/echou/subsampleScripts/picardGeneralSubsetTest.sh "+bams[i]+" "+names[i]+" "+epitopes[i]+" "+targetSampleVals[k-1]+" "+percent+" "+seeds[p-1]+" "+programs[i]+" noBeds"
#		
#		Popen(subsampleSysCall, shell=True)	

## Should output:
	# -qsub path to sampling program {path to bam} {name} {epitope} [size] {percents} [seed]
	# ^ constant {depends on file} [varies in predetermined way, within file]


