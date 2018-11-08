"""
Cleans up files older than a certain amount of time (weeks and days). Behavior defined in configuration.
AS IS, FILES ARE PERMANENTLY DELETED. USING A WHITELIST AND IGNORED DIRECTORY IS RECOMMENDED.

Author: Zachary Cook
Date: February 2018
File: DirectoryCleaner.py
"""

import time
import os
import ctypes
kernel32 = ctypes.windll.kernel32

# Refresh time of the loop in seconds
RefreshRate = 10
# If true, the logs will output
PrintOutput = True
# Config file
ConfigFileDirectory = "DirectoryCleanerConfig.txt"

def ShouldDeleteFile(Directory,Name,FilesToIgnore,DeleteTime):
    # Returns true if file should be deleted, given the age to delete files in seconds
    def PassesTimeCheck():
        # Checks if a file is older than the specified delete time
        LastModified = os.path.getmtime(Directory)
        DateModifiedFromNow = time.time() - LastModified
        return DateModifiedFromNow > DeleteTime

    Negate = "NEGATE" in FilesToIgnore
    if Negate:
        for Word in FilesToIgnore:
            if Word in Name:
                return PassesTimeCheck()

        return False
    else:
        for Word in FilesToIgnore:
            if Word in Name:
                return False

        return PassesTimeCheck()

def ShouldDeleteDirectories(DirectoriesToIgnore):
    # Returns if directories should be deleted
    return not ("KEEP_ALL_DIRECTORIES" in DirectoriesToIgnore)

def Output(String):
    # Print function
    if PrintOutput == True:
        print(String)



def Scan():
    # Main scan function. Reads configuration, reads drives, and handles files.

    DrivesToScan = []
    DirectoriesToScan = []
    DirectoriesToIgnore = {}
    FilesToIgnore = {}

    def ReadConfig():
        # Reads configuration file
        CleanTime = 0

        OpenFile = open(ConfigFileDirectory)
        CurReadMode = ""
        for Line in OpenFile:
            Line = Line.strip()

            if Line == "==========SD_CARD_CLEAR_TIME==========":
                CurReadMode = "SD_CARD_CLEAR_TIME"
            elif Line == "==========DIRECTORIES_TO_SCAN==========":
                CurReadMode = "DIRECTORIES_TO_SCAN"
            elif Line == "==========DRIVES_TO_SCAN==========":
                CurReadMode = "DRIVES_TO_SCAN"
            elif Line == "==========DIRECTORY_NAMES_TO_IGNORE=========":
                CurReadMode = "DIRECTORY_NAMES_TO_IGNORE"
            elif Line == "==========FILES_TO_IGNORE==========":
                CurReadMode = "FILES_TO_IGNORE"
            elif Line != "" and Line[0:2] != "//":
                if CurReadMode == "SD_CARD_CLEAR_TIME":
                    if Line[0:5] == "WEEKS":
                        CleanTime += (60 * 60 * 24 * 7) * int(Line[6:])
                    elif Line[0:4] == "DAYS":
                        CleanTime += (60 * 60 * 24) * int(Line[5:])
                elif CurReadMode == "DIRECTORIES_TO_SCAN":
                    DirectoriesToScan.append(Line)
                elif CurReadMode == "DRIVES_TO_SCAN":
                    DrivesToScan.append(Line)
                elif CurReadMode == "DIRECTORY_NAMES_TO_IGNORE":
                    DirectoriesToIgnore[Line] = True
                elif CurReadMode == "FILES_TO_IGNORE":
                    FilesToIgnore[Line] = True

        OpenFile.close()
        return CleanTime

    CleanTimeThreshold = ReadConfig()



    def DeleteFile(Directory):
        if os.path.isdir(Directory):
            Output("DELETE DIRECTORY: " + Directory)
            os.rmdir(Directory)
        else:
            Output("DELETE FILE: " + Directory)
            os.remove(Directory)

    def ProcessDirectory(Directory):
        # Processes the directory and returns the amount of files left
        Files = os.listdir(Directory)
        FilesKept = 0
        for i in range(0,len(Files)):
            FileName = Files[i]
            FullFileName = Directory + "/" + FileName
            if os.path.isdir(FullFileName):
                if FileName in DirectoriesToIgnore:
                    FilesKept += 1
                else:
                    if ProcessDirectory(FullFileName) == 0:
                        DeleteFile(FullFileName)
                    else:
                        FilesKept += 1
            else:
                if ShouldDeleteFile(FullFileName,FileName,FilesToIgnore,CleanTimeThreshold) == True:
                    DeleteFile(FullFileName)
                else:
                    FilesKept += 1

        return FilesKept

    def GetDrivesToScan():
        # Gets drive letters of computer
        # Adapted from https://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-drive-letters-in-python
        Drives = []
        Bitmask = kernel32.GetLogicalDrives()
        for i in range(65, 91):
            Letter = chr(i)
            if Bitmask & 1:
                Drives.append(Letter)
            Bitmask >>= 1

        return Drives

    def GetDrivesToScanFromLetters(DriveLetters):
        # Returns list of drive letters to scan given a list of all drive letters
        # Adapted from https://stackoverflow.com/questions/8319264/how-can-i-get-the-name-of-a-drive-in-python?rq=1

        FinalDrives = []
        for i in range(0,len(DriveLetters)):
            Letter = DriveLetters[i]
            VolumeNameBuffer = ctypes.create_unicode_buffer(1024)
            FileSystemNameBuffer = ctypes.create_unicode_buffer(1024)

            kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(Letter + ":\\"),
                VolumeNameBuffer,
                ctypes.sizeof(VolumeNameBuffer),
                None,
                None,
                None,
                FileSystemNameBuffer,
                ctypes.sizeof(FileSystemNameBuffer)
            )

            if VolumeNameBuffer.value in DrivesToScan:
                FinalDrives.append(Letter)

        return FinalDrives



    # Run functions
    LettersToScan = GetDrivesToScanFromLetters(GetDrivesToScan())
    for i in range(0,len(LettersToScan)):
        Letter = LettersToScan[i]
        Output("SCANNING DRIVE: " + Letter + ":/")
        ProcessDirectory(Letter + ":/")

    for i in range(0,len(DirectoriesToScan)):
        Directory = DirectoriesToScan[i]
        Output("SCANNING DIRECTORY: " + Directory)
        if os.path.exists(Directory):
            ProcessDirectory(Directory)

if __name__ == '__main__':
    while (True):
        Scan()
        time.sleep(RefreshRate)