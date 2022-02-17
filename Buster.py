
from builtins import print
import os, os.path # needed for cycling thru each file
import sys
import subprocess
from pathlib import Path # to make/create directories
import zipfile # Needed to unzip files


package = "docx2txt"
try:
    __import__(package) # For word doc conversion
except ImportError:
    print("System doesn't have needed modules. Installing now...\n")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("\nOne time install of needed modules complete. Continuing with program...\n")

import docx2txt 


##### REMEMBER!! MOSS FILE AND BUSTER FILE NEED TO BE IN SAME DIR. 
# Also DIR's to scan need to be inside original directory to work



########################################################
#
# You can use wget -r -np __MOSS-LINK__ to download the results to .html
#
########################################################


### TO DO ###
# Pull text from PDF's as well
# Write results to CSV file
# Build tool to reconsile CSV data with MOSS data somehow
# Ideally include the MOSS links to matching assignments as well
# This will make 1 unified output of data

# Check how it counts the number of original lines. I've seen it say 54 / 24 original before (is it adding both as a total somehow?)



### FUTURE WORK
# Add function to look at SIMILARITY (ie, color vs colour) and consider if that line is a match or not. This will fix the problem of users changing variables names.
# Add function that splits up word docs as sentences (a line is between 2 ./?/! type of thing instead of exact)






### USER EDITABLE VARIABLES

DIR_TO_SCAN = "" # change this if you want the subdir to the script to be named differently
ORIGINAL_ASSIGNMENT_NAME = "" # Ensure this is INSIDE the DIR_TO_SCAN folder

DEFAULT_LINE_LIMIT = 50
DEFAULT_DELTA = 20

DEBUG_STATUS = False # If true output is verbose. False looks cleaner
INCLUDE_NEG_RESULTS = False # Change to true to list neg results as well
PRINT_MOSS_COMMAND = False # Includes MOSS command line in results output
FILE_PATHS_INCLUDE_ROOT = False # Don't go to root file path unless needed. MOSS becomes messy with names.


# Welcome
print("\n\nWelcome! This script will scan a folder and compare all files with one another looking for sameness.\n")



CURR_DIR = os.path.dirname(sys.argv[0]) # current dir of script

# TODO: csvFileLocation = CURR_DIR + "/results.csv" # location to post results in csv format


# Verify Current Dir. If not compiled as executeable via cxfreeze, then pull the current dir via python
if CURR_DIR == "":
    CURR_DIR = os.getcwd()
    if DEBUG_STATUS == True:
        print("\n\nUpdated directory location with os.getcwd().")


if DEBUG_STATUS == True:
    print(f"\nThe current directory is: {CURR_DIR}\n")


# Confirm DIR name with user
print(f"\nThis program will scan a subfolder from where this script currently is located.\n\n**** This script is currently in:\n{CURR_DIR}\n\nYou need to enter the full name of the folder inside the location above (copy and paste the folder name)\n")
DIR_TO_SCAN = input("Enter the name of the folder to check here: ")

print(f"\n{DIR_TO_SCAN}   <- Is the folder that will be investigated.\n")






### SYSTEM VARIABLES

MATCHING_LINE_LIMIT = 0 # this is a percent cutoff for recording similarities as a whole number
TYPE_OF_FILE_TO_SCAN = "" # File Extenstion. You need to pick a singular type at this time
DELTA_BETWEEN_TWO_FILES = 0.00 # % Diff between 2 files to print at the end
FILTER_ORIGINAL_ASSIGNMENT_OUT = False

MATCHING_POSITIVE_HITS = [] # iterate thru this with: percent = [0 + 3], file1 = [1 + 3], file2 = [2 + 3]
ORIGINAL_ASSIGNMENT_LINES = [] # Holds lines of original assignment
LIST_OF_NEGATIVE_HITS = [] # This is a global variable
LIST_OF_EMPTY_HITS = [] # Records files that are empty
MOSS_FILE_EXISTS = False # Will convert to true and prompt MOSS que if moss.pl is in the same dir as this script




# TODO: csvFileLocation = CURR_DIR + "/results.csv" # location to post results in csv format



# Determine current directory
Path(f"{CURR_DIR}/{DIR_TO_SCAN}").mkdir(parents=True, exist_ok=True) 
SCANNING_DIR = CURR_DIR + "/" + DIR_TO_SCAN


# Verify moss.pl exists in this directory
try:
    mossFile = open("moss.pl", "r")
    mossFile.close()
    MOSS_FILE_EXISTS = True
    print("Moss file found")
except:
    print("Failed to open moss.pl file or moss.pl is not present in script directory")
    MOSS_FILE_EXISTS = False










######################################################## FUNCTIONS ########################################################


def ListOfFilesToScan():
    global TYPE_OF_FILE_TO_SCAN
    global DEBUG_STATUS
    global CURR_DIR
    global SCANNING_DIR
    global ORIGINAL_ASSIGNMENT_NAME
    global DIR_TO_SCAN
    global FILE_PATHS_INCLUDE_ROOT

    
    filesToScanList = []

    if TYPE_OF_FILE_TO_SCAN == "":
        TYPE_OF_FILE_TO_SCAN = ".py"


    if DEBUG_STATUS == True: 
        print(f"\nThe current directory is: {CURR_DIR}")
        print(f"The scanning directory containing files is: {SCANNING_DIR}\n")

    for root, dirs, files in os.walk(SCANNING_DIR):
        # select file name
        for file in files:
            
            # check the extension of files
            if file.endswith(TYPE_OF_FILE_TO_SCAN):
                
                if file[0] != ".": # Make sure it's not a hidden file
                    
                    if FILE_PATHS_INCLUDE_ROOT == True:
                        # Full file path from root level
                        fullFilePath = root + "/" + file
                    
                    elif FILE_PATHS_INCLUDE_ROOT == False:
                        # Use relative file paths
                        tempFilePath = root[len(CURR_DIR):] + "/" + file
                        fullFilePath = "." + tempFilePath
                        if DEBUG_STATUS == True:
                            print(f"File Location: {tempFilePath}")



                    if DEBUG_STATUS == True:
                        print(f"The following files will be scanned in this order: \n")
                        print(f"The file is: {file}")
                        print(f"The file directory location is: {root}") # Shows the dirpath of the file
                        print(f"The full filepath is: {fullFilePath}")


                    # Don't include the original assignment in the list of files to compare directly                
                    if file != ORIGINAL_ASSIGNMENT_NAME:
                        filesToScanList.append(fullFilePath) # Add all files you need to scan to a list



    return filesToScanList





def MossOutput(wantStarterOutput):
    global TYPE_OF_FILE_TO_SCAN
    global DEBUG_STATUS
    global CURR_DIR
    global SCANNING_DIR
    global ORIGINAL_ASSIGNMENT_NAME
    global DIR_TO_SCAN
    global PRINT_MOSS_COMMAND
    
    
    

    TYPE_OF_FILE_TO_SCAN = ".py"


    filesToScanList = ListOfFilesToScan()
    

    mossOutputLine = "perl moss.pl -l python "

    if wantStarterOutput == True:
        checkForDOCX = ORIGINAL_ASSIGNMENT_NAME[-5:]
        if DEBUG_STATUS == True:
            print(f"LAST 5 CHAR ARE {checkForDOCX}")
        if checkForDOCX.lower() == ".docx":
            mossOutputLine += "-b " + "\"" + SCANNING_DIR + "/" + ORIGINAL_ASSIGNMENT_NAME + ".py\" "
        else:
            mossOutputLine += "-b " + "\"" + SCANNING_DIR + "/" + ORIGINAL_ASSIGNMENT_NAME + "\" "


    if wantStarterOutput == True:
        for each in filesToScanList:
            
            lengthToCheck = len(ORIGINAL_ASSIGNMENT_NAME)
            lengthToCheck2 = lengthToCheck + 3 #for adding .py above
            nameToCheck = ORIGINAL_ASSIGNMENT_NAME + ".py"
            
            if each[-lengthToCheck2:] == nameToCheck:
                print("if passed")
                pass # do NOT add the temp starting assignment itself to the file list
            else:
                mossOutputLine += "\"" + each + "\"" + " " # add file to MOSS output line
    else:
        for each in filesToScanList:
            mossOutputLine += "\"" + each + "\"" + " " # add file to MOSS output line
            
        


    if PRINT_MOSS_COMMAND == True:    
        print("\n\nThe line you will want to copy and paste into terminal from the MOSS directory is: \n\n")
        print(mossOutputLine)
        print("\n\n\n")

    return mossOutputLine
    




def ConvertWordToTxt():
    print("This will convert word files to txt first.")

    global DIR_TO_SCAN
    global TYPE_OF_FILE_TO_SCAN
    global CURR_DIR
    global SCANNING_DIR
    global DEBUG_STATUS
    global ORIGINAL_ASSIGNMENT_NAME


    ### Begin Output Starting With Working Directories
    if DEBUG_STATUS == True:
        print(f"\nThe current directory is: {CURR_DIR}")
        print(f"The scanning directory containing files is: {SCANNING_DIR}\n")

        # Declare all files to be scanned
        print(f"The following files will be converted in this order: ")

    for root, dirs, files in os.walk(SCANNING_DIR):
        # select file name
        for file in files:
            
            # check the extension of files
            if file.endswith(TYPE_OF_FILE_TO_SCAN):
                if DEBUG_STATUS == True:
                    print(file)
                
                if file[0] != "~":

                    fileWithLocation = SCANNING_DIR + "/" + file
                    text = docx2txt.process(fileWithLocation)
                    
                    newFileName = SCANNING_DIR + "/" + file + ".py" # TODO: modded from .txt to .py for MOSS testing
                    with open(newFileName, "w") as text_file:
                        print(text, file=text_file)


    print("\n\nDocx files have been converted to txt in prep for scanning.\n")
    

    if ORIGINAL_ASSIGNMENT_NAME[-5:] == ".docx":
        ORIGINAL_ASSIGNMENT_NAME = ORIGINAL_ASSIGNMENT_NAME + ".py" # TODO: modded from .txt to .py for MOSS testing
        
        




def UnZipFiles():
    
    global DIR_TO_SCAN
    global CURR_DIR
    global SCANNING_DIR
    global DEBUG_STATUS
  
    zipFilesToUnzip = []

    # TODO: Scan folder for all ZIP files and load into a list
    
    for root, dirs, files in os.walk(SCANNING_DIR):
    # select file name
        for file in files:
        
            

        # check the extension of files
            if file.endswith(".zip"):
                
                # Note full path to zip
                fullZipPath = root + "/" + file
                if DEBUG_STATUS == True:
                    print(f"Temp var is: {fullZipPath}") # List all files to be unzipped

                zipFilesToUnzip.append(fullZipPath) # Add all files you need to scan to a list

    if DEBUG_STATUS == True: 
        print(zipFilesToUnzip) # unzip files list of individual file names


    # Unzip all files in the scanning directory
    for each in zipFilesToUnzip:
        #path_to_zip_file = SCANNING_DIR + "/" + each
        
        path_to_zip_file = each
        
        if DEBUG_STATUS == True:
            print(f"Path to Zip File: {path_to_zip_file}")
        
        try:
            with zipfile.ZipFile(path_to_zip_file, mode = 'r', allowZip64 = True) as zip_ref:
                
                if DEBUG_STATUS == True:
                    print(f"Zip_Ref: {zip_ref}")
                    print(f"Scanning Directory: {SCANNING_DIR}")
                    print(f"{each}")

                
                ######
                fileNameWithoutExtension = each[:-4]
                

                if DEBUG_STATUS == True:
                    print(fileNameWithoutExtension)

                
                #zipFileExtractLocation = SCANNING_DIR + "/" + fileNameWithoutExtension
                zipFileExtractLocation = fileNameWithoutExtension

                
                #zip_ref.extractall(SCANNING_DIR)
                zip_ref.extractall(zipFileExtractLocation)
                print(f"Unzipped: {zipFileExtractLocation}")

        except:
            print(f"Issue with unzipping file:\n{path_to_zip_file}")
    
    
    



def LineSimilarity():
    print("This will be used to further evaluate individual lines (ie, color vs colour being the same")
    # https://softwareengineering.stackexchange.com/questions/330934/what-algorithm-would-you-best-use-for-string-similarity
    # https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings
    # http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf
    # http://theory.stanford.edu/~aiken/moss/






def Spacer():
    print("\n\n\n\n")
    print("###########################################################")
    print("\n")






def OriginalAssignmentInput(originalFileLocation):
    
    startingLines = []
    
    # Convert original to temp file and remove whitespace
    o1 = open(originalFileLocation, "a")
    o1.close()
    o1 = open(originalFileLocation, "r")
    
    if DEBUG_STATUS == True:
        print(f"Currently checking original file: {originalFileLocation}")
        
    # Temp files. Don't change this
    f1 = open("temporiginal.py", "w")

    # Strip blank lines from  file and store them in temporiginal
    for line in o1:
        if not line.isspace():
            f1.write(line)
            tempLine = line.replace(" ", "")
            if tempLine[0] != "#": # Don't count original lines if they are comments
                startingLines.append(tempLine.strip()) 
    o1.close()
    f1.close()


    return startingLines






def MatchingOutput(MATCHING_POSITIVE_HITS, DELTA_BETWEEN_TWO_FILES, ORIGINAL_ASSIGNMENT_LINES):
    
    global LIST_OF_EMPTY_HITS
    global userFileType

    Spacer()

    ### 1. Print matches with a specific DELTA
    i = 0
    print(f"The following have a difference of less than {DELTA_BETWEEN_TWO_FILES}% to each other and are within the matching threshold:\n\n")
    while i < len(MATCHING_POSITIVE_HITS):
        delta = MATCHING_POSITIVE_HITS[i] - MATCHING_POSITIVE_HITS[i + 1]
        if delta < 0:
            delta *= -1
        delta = round(delta, 3)
        
        #DELTA_BETWEEN_TWO_FILES
        if delta <= DELTA_BETWEEN_TWO_FILES and delta > 0:
        
            if MATCHING_POSITIVE_HITS[i + 3] != MATCHING_POSITIVE_HITS[i + 4]:
                
                ### PRINTING OUTPUT HERE ###
                
                print("** Threshold Match **")
                print(f"\n{MATCHING_POSITIVE_HITS[i]}% / {MATCHING_POSITIVE_HITS[i + 1]}% similarity % between both files with a % difference of {delta}% and {MATCHING_POSITIVE_HITS[i + 2]} difference in total overall lines")
                if userFileType.upper() == "W":
                    print(f"File 1 with {MATCHING_POSITIVE_HITS[i + 6]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 3][:-3]}")
                    print(f"File 2 with {MATCHING_POSITIVE_HITS[i + 7]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 4][:-3]}")
                else:
                    print(f"File 1 with {MATCHING_POSITIVE_HITS[i + 6]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 3]}")
                    print(f"File 2 with {MATCHING_POSITIVE_HITS[i + 7]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 4]}")
                print(f"Number of lines that match original assignment: {MATCHING_POSITIVE_HITS[i + 5]} / {len(ORIGINAL_ASSIGNMENT_LINES)} lines")
                if MATCHING_POSITIVE_HITS[i + 6] == 0:
                    print(f"File 1 contained no user work.")
                elif MATCHING_POSITIVE_HITS[i + 7] == 0:
                    print(f"File 2 contained no user work.")
                print("\n ------------------------------------------------------------------------------------------------------------------------------------------ \n")
        
        i += 8
    


    # Spacer between printouts
    Spacer()

    # 2. Print users with no completed work.
    i = 0
    print("The following are EMPTY assignments. They are matches to the original assignment meaning the user did no work and submitted an empty assignment):\n\n")
    
    while i < len(LIST_OF_EMPTY_HITS):
        if userFileType.upper() == "W":
            print(f"{LIST_OF_EMPTY_HITS[i][:-3]}")
        else:
            print(f"{LIST_OF_EMPTY_HITS[i]}")
        i += 1

    
    # Spacer between printouts
    Spacer()


    # 3. Print only PERFECT MATCHES
    i = 0
    print("The following are PERFECT matches to each other (one may have a fewer lines but the smallest doc is a match):\n\n")
    while i < len(MATCHING_POSITIVE_HITS):
        if MATCHING_POSITIVE_HITS[i] == MATCHING_POSITIVE_HITS[i + 1] and MATCHING_POSITIVE_HITS[i] > 99.99:
            if MATCHING_POSITIVE_HITS[i + 3] != MATCHING_POSITIVE_HITS[i + 4]:
                print(f"\n{MATCHING_POSITIVE_HITS[i]}% / {MATCHING_POSITIVE_HITS[i + 1]}%  =  (Difference in total overall lines: {MATCHING_POSITIVE_HITS[i + 2]})")
                
                if userFileType.upper() == "W":
                    print(f"File 1 with {MATCHING_POSITIVE_HITS[i + 6]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 3][:-3]}")
                    print(f"File 2 with {MATCHING_POSITIVE_HITS[i + 7]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 4][:-3]}")
                else:
                    print(f"File 1 with {MATCHING_POSITIVE_HITS[i + 6]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 3]}")
                    print(f"File 2 with {MATCHING_POSITIVE_HITS[i + 7]} user entered lines of work: {MATCHING_POSITIVE_HITS[i + 4]}")

                print(f"Number of lines that match original assignment: {MATCHING_POSITIVE_HITS[i + 5]} / {len(ORIGINAL_ASSIGNMENT_LINES)} lines.")
                if MATCHING_POSITIVE_HITS[i + 6] == 0:
                    print(f"File 1 contained no user work.")
                elif MATCHING_POSITIVE_HITS[i + 7] == 0:
                    print(f"File 2 contained no user work.")
        i += 8



    


def NegativeSimilarity():
    global LIST_OF_NEGATIVE_HITS

    # NEGATIVE OUTPUT

    Spacer()

    print(f"The following are all the negative/rejected comparisons:\n\n")
    i = 0

    while i < len(LIST_OF_NEGATIVE_HITS):
        delta = LIST_OF_NEGATIVE_HITS[i] - LIST_OF_NEGATIVE_HITS[i + 1]
        if delta < 0:
            delta *= -1
        delta = round(delta, 3)
                
        print(f"\n{LIST_OF_NEGATIVE_HITS[i]}% / {LIST_OF_NEGATIVE_HITS[i + 1]}% similarity % between both files with a % difference of {delta}% and {LIST_OF_NEGATIVE_HITS[i + 2]} difference in total overall lines")
        print(f"File 1 with {LIST_OF_NEGATIVE_HITS[i + 6]} user entered lines of work: {LIST_OF_NEGATIVE_HITS[i + 3]}")
        print(f"File 2 with {LIST_OF_NEGATIVE_HITS[i + 7]} user entered lines of work: {LIST_OF_NEGATIVE_HITS[i + 4]}")
        print(f"Number of lines that match original assignment: {LIST_OF_NEGATIVE_HITS[i + 5]} / {len(ORIGINAL_ASSIGNMENT_LINES)} lines")
        if LIST_OF_NEGATIVE_HITS[i + 6] == 0:
            print(f"File 1 contained no user work.")
        elif LIST_OF_NEGATIVE_HITS[i + 7] == 0:
            print(f"File 2 contained no user work.")
        print("\n ------------------------------------------------------------------------------------------------------------------------------------------ \n")

    i += 8




    # Spacer between printouts
    Spacer()






def ScanExactLineCopies(ORIGINAL_ASSIGNMENT_LINES, MATCHING_LINE_LIMIT, filesToScanList):
    
    global DEBUG_STATUS
    global LIST_OF_NEGATIVE_HITS
    global LIST_OF_EMPTY_HITS
    global userFileType

    totalFilesToScan = len(filesToScanList)
    print("Progress...\n")

    try:
        percentCompletedPerFile = 100 / totalFilesToScan
    except:
        if DEBUG_STATUS == True:
            print("Error calculating percentage completion of files")
            percentCompletedPerFile = 1

    


    if DEBUG_STATUS == True:
        print(f"We are going to print the following list of files:\n{filesToScanList}")

    LIST_OF_POSITIVE_HITS = []
    

    studentCounter = 0

    while studentCounter < len(filesToScanList):

        
        baseFile = filesToScanList[studentCounter]
        
        counter2 = studentCounter + 1 # Don't compare two of the same files. Also every file previous has already been compared. ##IMPORTANT!

        try: 
            percentCompleted = studentCounter * percentCompletedPerFile
        except:
            if DEBUG_STATUS == True:
                print("Error calculating percentage completion of files")
                percentCompleted = 1

        
        # PRINT THE PROGRESS ON SCREEN
        print(f"{round(percentCompleted, 1)}%")
        

        while counter2 < len(filesToScanList):
        
            readyToFlipFiles = False
            bothFilesCompared = False

            while bothFilesCompared == False:
                
                
                
                
                # FILES NEED TO BE COMPARED TO EACH OTHER (A to B then B to A)
                # Use READY TO FLIP FILES for this (change o1 and o2)




                ###fileToCheck = SCANNING_DIR + "/" + filesToScanList[counter2]
                fileToCheck = filesToScanList[counter2]
                
                #########################################################################################################

                if readyToFlipFiles == False:
                # Open both files and strip any blank lines from each. Store the results into 2 temp files
                    o1 = open(baseFile, "r")
                    o2 = open(fileToCheck, "r")

                    if DEBUG_STATUS == True:
                        print(f"Currently checking baseFile: {baseFile}")
                        print(f"Currently checking fileToCheck: {fileToCheck}\n\n")

                    # Temp files. Don't change these
                    f1 = open("temp1.py", "w")
                    f2 = open("temp2.py", "w")


                    # Strip blank lines from each file and store them in temp1 and temp2
                    for line in o1:
                        if not line.isspace():
                            f1.write(line)


                    for line in o2:
                        if not line.isspace():
                            f2.write(line)

                    o1.close()
                    o2.close()
                    f1.close()
                    f2.close()
                else:
                    o2 = open(baseFile, "r")
                    o1 = open(fileToCheck, "r")

                    if DEBUG_STATUS == True:
                        print(f"Currently checking baseFile: {baseFile}")
                        print(f"Currently checking fileToCheck: {fileToCheck}\n\n")

                    # Temp files. Don't change these
                    f1 = open("temp1.py", "w")
                    f2 = open("temp2.py", "w")


                    # Strip blank lines from each file and store them in temp1 and temp2
                    for line in o1:
                        if not line.isspace():
                            f1.write(line)


                    for line in o2:
                        if not line.isspace():
                            f2.write(line)

                    o1.close()
                    o2.close()
                    f1.close()
                    f2.close()

                    bothFilesCompared = True # Done comparing both files so reset for the next round.



                # Now open and compare temp files
                f1 = open("temp1.py", "r")


                # Vars for comparing from File 1
                i = 0
                totalLinesFile1 = 0
                sameLines = 0
                totalLinesInFile2 = 0
                percentSimilar = 0.0
                codeLinesFile1 = 0
                commentedLinesFile1 = 0
                listOfSameLines = []
                originalAssignLineComfirmed1 = 0





                # Compare each seperate line in file 1 with each individual line in file 2
                for line in f1:

                    totalLinesFile1 += 1
                    
                    # Remove spaces from each line
                    strippedLine1 = line.replace(" ", "")
                    

                    # Check to see if it's a python comment. If it is, count it as a comment
                    if line[0] == "#" or strippedLine1[0] == "#":
                        commentedLinesFile1 += 1
                        if DEBUG_STATUS == True:
                            print(f"Commened line: {line}")
                    
                    
                    ## ORIGINAL ASSIGNMENT CODE
                    
                    elif (strippedLine1.strip() in ORIGINAL_ASSIGNMENT_LINES):
                        # If strippedLine1 is in the original assignment, don't mark it as a same line (ie, do nothing here)
                        originalAssignLineComfirmed1 += 1

                        

                        if DEBUG_STATUS == True:
                            print(f"Currently checking baseFile: {baseFile}")
                            print(f"Currently checking fileToCheck: {fileToCheck}\n\n")
                            print(strippedLine1)
                            print(originalAssignLineComfirmed1)
                            
                            print("Line is from original assignment in file 1.")
                            print(strippedLine1)

                    # Otherwise it's a usable line
                    else:
                        codeLinesFile1 += 1
                    
                    
                    









                    f2SingleSimilarLineMonitor = False # This is method 1 of preventing multiple of the same lines to register as hits in file 2
                    f2LineNumber = 0
                    totalLinesInFile2 = 0
                    commentedLinesFile2 = 0
                    codeLinesFile2 = 0
                    originalLineComfirmed = 0
                    originalAssignLineComfirmed2 = 0

                    # Keep opening and closing file 2 to look at every line
                    f2 = open("temp2.py", "r")
                    for line2 in f2:
                        
                        totalLinesInFile2 += 1
                        strippedLine2 = line2.replace(" ", "")
                        

                        # Lines can be only COMMENTED, ORIGINAL, OR CODELINES
                        if line2[0] == "#" or strippedLine2[0] == "#":
                            commentedLinesFile2 += 1

                        elif (strippedLine2.strip() in ORIGINAL_ASSIGNMENT_LINES):
                            # If strippedLine1 is in the original assignment, don't mark it as a same line (ie, do nothing here)
                            originalAssignLineComfirmed2 += 1

                            if DEBUG_STATUS == True:
                                print("Line is from original assignment in file 2.")
                                print(strippedLine2)
                                
                        # Otherwise it's a usable line
                        else:
                            codeLinesFile2 += 1


                        f2LineNumber += 1 # Taking note of what line number we are on in F2. Needed to ensure they are not repeated.
                        

                        
                        if strippedLine1.strip() == strippedLine2.strip() and strippedLine2[0] != "#" and f2LineNumber not in listOfSameLines:       
                            if DEBUG_STATUS == True:
                                print("Identical Line Found")                        
                                print(line.strip())
                                print(line2.strip())
                                print(f"On file 2 line number: {f2LineNumber}\n")
                                
                            # Either a same line or an assignment line. Never both.
                            if (strippedLine1.strip() in ORIGINAL_ASSIGNMENT_LINES):
                                # This matched line is from the original, ignore.
                                if DEBUG_STATUS == True:
                                    print("Skipping matched line. This is in the original assignment.")
                            else:
                                sameLines += 1 # THE LINES ARE THE SAME HERE


                            # Same line recording
                            listOfSameLines.append(f2LineNumber)
                            
                        
                        # elif ADD ACCEPTIABLE SIMILARITY CHECK HERE!!!

                    f2.close()





                # closing file1
                f1.close()									
                    
                # sameLines = lines that are the same to another file. Are verified not in original assignment
                # totalLinesFile1 = Overall number of lines in File 1
                # codeLinesFile1 = Number of code/text lines that are not any other category
                # commentedLinesFile1 = comments in code. They start with #
                # originalAssignLineComfirmed1 = Num of lines that match the original assignment. Comments were removed when building this list

                # TotalLines = codeLines + originalLines + commentedLines
                # Note how same is not part of this equation.

                # TotalLines - OrginalLines - CommentedLines = CodeLines
                # If CodeLines = 0 then they didn't write anything (use 100 - x as in 100% - x = percent written)
                # Amount User Wrote = CodeLines / (Total - Commented)
                # 

                

                # Note file names and paths
                if readyToFlipFiles == False:
                    file1 = filesToScanList[studentCounter]
                    file2 = filesToScanList[counter2]
                elif readyToFlipFiles == True:
                    file1 = filesToScanList[counter2]
                    file2 = filesToScanList[studentCounter]
                    


                if DEBUG_STATUS == True:
                    print(f"\n\nNumber of similar lines: {sameLines}\n")
                    
                    print(f"File 1: {file1}")
                    print(f"Total number of coded lines in File 1: {codeLinesFile1}")
                    print(f"Total commented lines in File 1: {commentedLinesFile1}")
                    print(f"Overall total number of lines in File 1: {totalLinesFile1}")
                    print(f"The number of lines in File 1 that matches the original assignment: {originalAssignLineComfirmed1}")
                    
                    print("\n")
                    
                    print(f"File 2: {file2}")
                    print(f"Total number of coded lines in File 2: {codeLinesFile2}")
                    print(f"Total commented lines in File 2: {commentedLinesFile2}")
                    print(f"Overall total number of lines in File 2: {totalLinesInFile2}")
                    print(f"The number of lines in File 1 that matches the original assignment: {originalAssignLineComfirmed2}")

                    print("\n")




                # TODO: THIS AREA DOES CALCULATION OF LINE SIMILARY. CAN IT SHOW:
                # % Original is included in assignment
                # % Diff of original to assignment
                # Can I get a % similar overall (but STILL include the perfect matches?)
                # 100% match is correct but I want to see the % of diff/addition as well

                ######## Can I give a number that REMOVES the original assignment in the %same comparison?




                if commentedLinesFile1 + originalAssignLineComfirmed1 + codeLinesFile1 == totalLinesFile1:
                    if DEBUG_STATUS == True:
                        print("All lines accounted for in search")
                else:
                    if DEBUG_STATUS == True:
                        print("\n\nLINES MISSING IN COUNT! Check commented, coded, and total lines above.")
                    

                
                if codeLinesFile2 != 0:
                    percentSimilar = (sameLines / codeLinesFile2) * 100 # COMPARED TO FILE TWO USEABLE LINES, how many were the same?
                    
                    percentSimilar = round(percentSimilar, 3)
                    diffInTotalLines = totalLinesFile1 - totalLinesInFile2
                    if diffInTotalLines < 0:
                        diffInTotalLines *= -1
                
                else:
                    diffInTotalLines = totalLinesFile1 - totalLinesInFile2
                    

                if DEBUG_STATUS == True:
                    print(f"\nPercent similar: {percentSimilar}%\n\n")

                if readyToFlipFiles == False:
                    tempPercentSimilar = percentSimilar
                    
                    

                ######### RECORD HITS TO RECORD
                if readyToFlipFiles == True and (percentSimilar >= MATCHING_LINE_LIMIT or tempPercentSimilar >= MATCHING_LINE_LIMIT):
                    LIST_OF_POSITIVE_HITS.append(tempPercentSimilar)
                    LIST_OF_POSITIVE_HITS.append(percentSimilar)

                    LIST_OF_POSITIVE_HITS.append(diffInTotalLines)

                    LIST_OF_POSITIVE_HITS.append(filesToScanList[studentCounter])
                    LIST_OF_POSITIVE_HITS.append(filesToScanList[counter2])

                    LIST_OF_POSITIVE_HITS.append(originalAssignLineComfirmed1)

                    LIST_OF_POSITIVE_HITS.append(codeLinesFile1)
                    LIST_OF_POSITIVE_HITS.append(codeLinesFile2)

                    


                else:
                    LIST_OF_NEGATIVE_HITS.append(tempPercentSimilar)
                    LIST_OF_NEGATIVE_HITS.append(percentSimilar)

                    LIST_OF_NEGATIVE_HITS.append(diffInTotalLines)

                    LIST_OF_NEGATIVE_HITS.append(filesToScanList[studentCounter])
                    LIST_OF_NEGATIVE_HITS.append(filesToScanList[counter2])
                    
                
                # Empty Files are Noted
                if codeLinesFile1 == 0 and readyToFlipFiles == False:
                    if filesToScanList[studentCounter] not in LIST_OF_EMPTY_HITS:
                        LIST_OF_EMPTY_HITS.append(filesToScanList[studentCounter])
                        
                

                ### Both Files
                readyToFlipFiles = True

            
            
            
            


            
            #########################################################################################################
            counter2 += 1 # Increment to next file to compare to

        studentCounter += 1 # Start comparing file #2, then 3, etc

    ## END OF FUNCTION
    return LIST_OF_POSITIVE_HITS














######################################################## MAIN PROGRAM ########################################################


# Ask if they want to filter out original assignment
userFilterOriginal = input("\nDo you want to filter out the boiler-plate material (original assignment or initally given work) from the rest of content in a submission?\nYou would use this if you provided a starter document or initial code users were supplied. This prevents having matching lines across files when it's simpily directions or initial content given to the user.\n(Y)es or (N)o?: ")

if userFilterOriginal.upper() == "Y":
    print(f"\nThe default original file must be in the same folder as the files being scanned.\n")
    ORIGINAL_ASSIGNMENT_NAME = input("Enter the starter file file name (include the file extension): ")
    print(f"\n{ORIGINAL_ASSIGNMENT_NAME}   <- is the starting assignment to that's going to be used.")
    FILTER_ORIGINAL_ASSIGNMENT_OUT = True
    
else:
    FILTER_ORIGINAL_ASSIGNMENT_OUT = False


# Ask the user what % cutoff they want (as a number)
userCutoff = input(f"\n\nWhat percent similarity cutoff do you want? {DEFAULT_LINE_LIMIT}% is the current default.\nEnter 67.5% as 67.5 for example: ")
if userCutoff == "":
    MATCHING_LINE_LIMIT = DEFAULT_LINE_LIMIT
else:
    try:
        MATCHING_LINE_LIMIT = float(userCutoff)
    except:
        print("Input failed. Exiting...")
        exit()


userDelta = input(f"\nEnter the delta cutoff (% difference between two files) you'd like to see. {DEFAULT_DELTA}% is the current default: ")
if userDelta == "":
    DELTA_BETWEEN_TWO_FILES = DEFAULT_DELTA
else:
    try:
        DELTA_BETWEEN_TWO_FILES = float(userDelta)
    except:
        print("Input failed. Exiting...")
        exit()





# Determine file type
while True:
    userFileType = input("\n\nWhat do you want to do?\n(W)ord docs scanned\n(P)ython files scanned\n(C)# files scanned\n(U)nzip files in the folder\n(M)oss Output from Stanford\n(Q)uit\n")
    if userFileType.upper() == "W":
        TYPE_OF_FILE_TO_SCAN = ".docx" # Set to docx for conversion
        ConvertWordToTxt() # First convert all docx's to txt, then continue
        # TODO: modded from .txt to .py for MOSS testing
        TYPE_OF_FILE_TO_SCAN = ".py" # Then set to txt to scan
        break
    
    elif userFileType.upper() == "P":
        TYPE_OF_FILE_TO_SCAN = ".py"
        break
    
    elif userFileType.upper() == "C":
        print("I'll get to that eventually")
        exit()
    
    elif userFileType.upper() == "U":
        UnZipFiles()
    
    elif userFileType.upper() == "M":
        
        if MOSS_FILE_EXISTS == True:
            # Check if user even entered an original assignment. If yes...
            if FILTER_ORIGINAL_ASSIGNMENT_OUT == True:
                useStarter = input("Do you want to factor in starter assignment? (Y)es or (N)o: ").upper()
                if useStarter == "Y":
                    mossOutputLine = MossOutput(True)
                else:
                    mossOutputLine = MossOutput(False)
            # If no, don't ask to include it. Continue with not using it
            else:
                mossOutputLine = MossOutput(False)
            
            runMoss = input("Would you like to run the MOSS scan now? (Y)es or (N)o?: ").upper()
            if runMoss == "Y":
                os.system(mossOutputLine)
            else:
                print("If you decide to later, here is the line to run:\n\n")
                print(mossOutputLine)
            runMoss = "" # Clear variable
        else:
            # Moss.pl does NOT exist
            print("\nThe \"moss.pl\" file does not exist. MOSS functions are turned off.\n\nPlease visit http://theory.stanford.edu/~aiken/moss/ to enroll and setup MOSS.\n\nOnce enrolled, keep moss.pl in the same folder as this script and this feature will work.\n")

    elif userFileType.upper() == "Q":
        print("Goodbye\n\n")
        exit()
    else: 
        print("Invalid selection.")






### Begin Output Starting With Working Directories

if DEBUG_STATUS == True: 
    print(f"\nThe current directory is: {CURR_DIR}")
    print(f"The scanning directory containing files is: {SCANNING_DIR}\n")


# File all file names/paths and add them to a list
filesToScanList = []
filesToScanList = ListOfFilesToScan()





#################### FILE MATCHING SCAN ####################

print(f"\n\nThis may take a couple minutes. Please be patient.\nBeginning file line matching scan...\n\n\n")



# Reterive original assignment lines
startingAssignmentFullFilePath = SCANNING_DIR + "/" + ORIGINAL_ASSIGNMENT_NAME
if DEBUG_STATUS == True:
    print(f"Starting Assignment Location: {startingAssignmentFullFilePath}\n\n")

if FILTER_ORIGINAL_ASSIGNMENT_OUT == True:
    ORIGINAL_ASSIGNMENT_LINES = OriginalAssignmentInput(startingAssignmentFullFilePath)
    if DEBUG_STATUS == True:
        print(f"The original assignment lines are:\n\n{ORIGINAL_ASSIGNMENT_LINES}\n\n")





# Call function to scan matching lines in files and save results into MATCHING_POSITIVE_HITS
MATCHING_POSITIVE_HITS = ScanExactLineCopies(ORIGINAL_ASSIGNMENT_LINES, MATCHING_LINE_LIMIT, filesToScanList)





# NEGATIVE OUTPUT
if INCLUDE_NEG_RESULTS == True:
    NegativeSimilarity()





# POSITIVE OUTPUT
MatchingOutput(MATCHING_POSITIVE_HITS, DELTA_BETWEEN_TWO_FILES, ORIGINAL_ASSIGNMENT_LINES)





# REMOVE BASE DIR TEMP FILES
try:
    os.remove("temp1.py")
    os.remove("temp2.py")
    os.remove("temporiginal.py")
except:
    print("Failed to cleanup some temp files.")






# Output MOSS Link if it's present
if MOSS_FILE_EXISTS == True:
    printMoss = input("\n\n\nDo you also want the MOSS (Stanford University's Plagiarism Dectection) output? (Y)es or (N)o: ")
    if printMoss.upper() == "Y":
        if FILTER_ORIGINAL_ASSIGNMENT_OUT == True:
            mossIncStarterAssignment = input("Include starter assignment? (Y)es or (N)o: ")
            if mossIncStarterAssignment.upper() == "Y":
                mossOutputLine = MossOutput(True)
            else:
                mossOutputLine = MossOutput(False)
        else:
            mossOutputLine = MossOutput(False)

        runMoss = input("Would you like to run the MOSS scan now? (Y)es or (N)o?: ").upper()
        if runMoss == "Y":
            os.system(mossOutputLine) # Run the moss command line in the same window
        else:
            print("If you decide to later, here is the line to run:\n\n")
            print(mossOutputLine)
            print("\n\n")

        runMoss = "" # Clear variable


print("\nGoodbye!\n\n")




