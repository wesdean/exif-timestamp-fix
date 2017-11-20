# This has only  been test on Mac OS

import sys
import exifread
import os
import datetime
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("dirName", help="Name of directory to process")
parser.add_argument("-r", "--recursive", help="Process subdirectories", action="count", default=0)
args = parser.parse_args()

DATEFIX_REGEX = re.compile(r": ")


def getExifCreated(fileName):
    f = open(fileName, 'rb')
    tags = exifread.process_file(f)
    tag = tags.get("EXIF DateTimeOriginal")
    if (tag):
        return re.sub(DATEFIX_REGEX, ':0', tags.get("EXIF DateTimeOriginal").values)
    else:
        return None


def processDirectory(dirName):
    fileNames = os.listdir(dirName)
    count = 0
    for fileName in fileNames:
        if (fileName.startswith('.')): continue

        fileName = "{}/{}".format(dirName.rstrip('/'), fileName)
        if (os.path.isfile(fileName)):
            count += processFile(fileName)
        elif (os.path.isdir(fileName) and args.recursive):
            count += processDirectory(fileName)
    return count


def processFile(fileName):
    createdAt = getExifCreated(fileName)
    if (createdAt):
        createdAt = datetime.datetime.strptime(createdAt, '%Y:%m:%d %H:%M:%S')
        fileCreatedAt = datetime.datetime.fromtimestamp(os.stat(fileName).st_birthtime)

        if (createdAt != fileCreatedAt):
            createdAtString = createdAt.strftime('%m/%d/%Y %H:%M:%S')
            os.system('SetFile -d "{}" "{}"'.format(createdAtString, fileName))
            os.system('SetFile -m "{}" "{}"'.format(createdAtString, fileName))
            print("Set created date to " + createdAtString + ": " + fileName)
            return 1
        else:
            print("Create dates match: {}".format(fileName))
    else:
        print("No EXIF data for file: {}".format(fileName))

    return 0


if (len(sys.argv) > 1):
    dirName = args.dirName
    count = 0
    if (os.path.isfile(dirName)):
        count += processFile(dirName)
    else:
        count += processDirectory(dirName)

    print("Done processing {} files".format(count))
else:
    print("No files selected")
