#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Transmission Cleanup
#  (main.py)
#  
#  Copyright 2014 Nicolas Cova <nicolas.cova.work@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import time
import subprocess
import datetime
from datetime import date

def main():
    try:
        file1 = open("server.txt")
    except:
        file1 = open("server.txt","w")
        file1.write("username\n")
        file1.write("password\n")
        file1.write("transmission.example.com:9091")
        file1.close()
        print("Created server.txt.  Adapt this file for your server settings.")
        return 1

    temp = file1.read().splitlines()
    username = temp[0]
    password = temp[1]
    remoteAddr = temp[2]
    authUser = username + ":" + password
    print("Found server information...")
    print("Username: " + username)
    print("Password: " + password)
    print("Remote  : " + remoteAddr)

    try:
        commandResult = subprocess.check_output(["transmission-remote",remoteAddr,"--auth", authUser, "-l"])
    except CalledProcessError:
        dateAndTime = time.strftime("%H:%M:%S") + " " + time.strftime("%d/%m/%Y")
        print(dateAndTime + " ERROR: something went wrong checking the torrents listing.") 
        return -1
        
    splitResult = commandResult.split("\n")

    # Remove items which are just empty strings
    while True:
        try:
            splitResult.remove("")
        except ValueError:
            # Insert error message here
            break

    # Remove first and last items so the list only contains torrent info.
    # If the length of the list is smaller than 2, just exit.
    if len(splitResult) > 2:
        splitResult.pop(0)
        splitResult.pop()
    else:
        return 0

    # For the remaining items, check if any of them contains '100%' and
    # add them to a completed torrents list.
    completedTorrents = []
    for item in splitResult:
        if "100%" in item:
            torrentId = item.lstrip().split()[0].rstrip("*")
            torrentName = item[item.rfind("      "):len(item)].lstrip()
            completedTorrents.append((torrentId,torrentName))

    # For each torrentId in the completed Torrents list, remove the
    # trailing spaces and execute the shell command to remove the torrent
    torrentsRemoved = False
    idleTorrents = []
    try:
        for item in completedTorrents:
            commandResult = subprocess.check_output(["transmission-remote",remoteAddr,"--auth",authUser, "-t", item[0], "--info"])
            splitResult = commandResult.split("\n")
            for line in splitResult:
                if "Latest activity:" in line:
                    newLine = line.split(":  ")
                    date_time_obj = datetime.datetime.strptime(newLine[1], '%c')
                    today = datetime.datetime.now()
                    timeDelta = today-date_time_obj
                    tooOld = datetime.timedelta(7)
                    if timeDelta>=tooOld:
                        #print(item[1])
                        #print(timeDelta)
                        #print('')
                        idleTorrents.append((item[0],item[1],timeDelta))
                        #print(date_time_obj.date())
                    #print(timeDelta)
                    #print(today)
                    #print(date_time_obj.date())
    except CalledProcessError:
        dateAndTime = time.strftime("%H:%M:%S") + " " + time.strftime("%d/%m/%Y")
        print(dateAndTime + " ERROR: something went wrong with 'check_output'. " + commandResult)
        return -1

    for item in idleTorrents:
        commandResult = subprocess.check_output(["transmission-remote",remoteAddr,"--auth",authUser,"-t",item[0],"-rad"])
        print("Removed: " + item[1])

    return 0

if __name__ == '__main__':
    main()

