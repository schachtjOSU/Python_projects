#SingleNode_DSTAT_Auto
#Author: Jeffrey Schachtsick
#Last Update: 05/30/2014
#Description: Read from single node CSV file, compute statistical
#    data from node categories, plot data into graphs, and print
#    data and graphs to a file.

# Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
from pandas import Series, DataFrame
import pandas as pd
import csv

# userSpecify Function
def userSpecify():
    """User specifies directory, to establish path"""
    valid = False
    while valid != True:
        userPath = raw_input("\nPlease specify directory path or press Enter key for the current directory: ").strip()
        if userPath == "":
            path = "."
        else:
            path = userPath
        if os.path.exists(path):
            print("Path has been validated")
            valid = True
        else:
            print("Invalid File Path, File Doesn't Exist!  Please try again.")
            continue
        return path
    
# Find Dstat Log
def find_dstat(path):
    print "\nFinding dstat log ..."
    dstatLog = ""
    for r,d,f in os.walk(path, topdown=False):
       for files in f:
           if files.endswith(".csv") and "dstat" in files:
               dstatLog = files
    
    print "Log found: ", dstatLog
    return dstatLog
    
def cpu_use(usage, n, name):
    """ Calculate and graph cpu usage for user and system """
    # Calculate
    usageMean = usage.mean()
    usageMedian = usage.median()
    usageMin = usage.min()
    usageMax = usage.max()
    usageArgMin = usage.argmin()
    usageArgMax = usage.argmax()
    
    print "*****************************************"
    print "*** CPU Usage Statistics for ", name, " ***"
    print "Usage mean %: ", usageMean
    print "Usage median %: ", usageMedian
    print "Minimum usage %: ", usageMin
    print "Maximum usage %: ", usageMax
    print "First row with min usage %: ", usageArgMin
    print "First row with max usage %: ", usageArgMax
    print "*****************************************\n"
    
    # Plot CPU Usage
    fig = plt.figure(n)
    fig.suptitle('CPU ' + name + ' %', fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111)
    ax.set_ylabel('CPU %')
    ax.yaxis.grid()
    usageCpuLine = plt.plot(usage)
    usageCpuMean = plt.axhline(usageMean)
    usageCpuMax = plt.axhline(usageMax)
    usageCpuMin = plt.axhline(usageMin)
    plt.setp(usageCpuLine, color='g', linewidth=0.5)
    plt.setp(usageCpuMean, color='r', linewidth=0.5)
    if name == "Idle":
        plt.setp(usageCpuMin, color='b', linestyle='--', linewidth=0.5)
        label = "Min CPU Idle(~" + str(int(usageMin)) + "%)"
    else:
        plt.setp(usageCpuMax, color='b', linestyle='--', linewidth=0.5)
        label = "Max CPU Usage(~" + str(int(usageMax)) + "%)"
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(["CPU " + name + " %", "Mean(~" + str(int(usageMean)) + "%)", label], bbox_to_anchor=(1.3, 1), loc=7)
    plt.show()

def data_traffic(traffic, n, name):
    """ This will calculate the traffic"""
    # Calculate Stats for Traffic
    trafficMean = traffic.mean()
    trafficMedian = traffic.median()
    trafficMin = traffic.min()
    trafficMax = traffic.max()
    trafficArgMin = traffic.argmin()
    trafficArgMax = traffic.argmax()
    
    print "*****************************************"
    print "*** Traffic Statistics for ", name, " ***"
    print "Traffic mean %: ", trafficMean
    print "Traffic median %: ", trafficMedian
    print "Traffic usage %: ", trafficMin
    print "Traffic usage %: ", trafficMax
    print "First row with min traffic %: ", trafficArgMin
    print "First row with max traffic %: ", trafficArgMax
    print "*****************************************\n"
    
    # Plot Traffic
    fig = plt.figure(n)
    fig.suptitle(name, fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111)
    ax.set_ylabel('Mb')
    ax.yaxis.grid()
    trafficCpuLine = plt.plot(traffic)
    trafficCpuMean = plt.axhline(trafficMean)
    plt.setp(trafficCpuLine, color='g', linewidth=0.5)
    plt.setp(trafficCpuMean, color='r', linewidth=0.5)
    # Conditionals between Traffic
    #Memory Free
    if name == "Memory Free":
        trafficCpuMin = plt.axhline(trafficMin)
        plt.setp(trafficCpuMin, color='b', linestyle='--', linewidth=0.5)
        label = "Lowest Free Space(~" + str(int(trafficMin)) + "Mb)"
    # IO Read and Write
    elif name == "IO Read" or name == "IO Write":
        trafficCpuMax = plt.axhline(trafficMax)
        plt.setp(trafficCpuMax, color='b', linestyle='--', linewidth=0.5)
        label = "Max IO(~" + str(int(trafficMax)) + "Mb)"
    # Network Send and recieve
    else:
        trafficCpuMax = plt.axhline(trafficMax)
        plt.setp(trafficCpuMax, color='b', linestyle='--', linewidth=0.5)
        label = "Max Net Traffic(~" + str(int(trafficMax)) + "Mb)"
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend([name, "Mean(~" + str(int(trafficMean)) + "Mb)", label], bbox_to_anchor=(1.3, 1), loc=7)
    plt.show()

# Main
def main():
    """ Main management of all functions """
    n = 1
    columnList = ['usr', 'sys', 'idl', 'free', 'read', 'writ', 'recv', 'send']
    nameList = ["User", "System", "Idle", "Memory Free", "IO Read", "IO Write", 
    "Network Recieved", "Network Sent"]
    path = userSpecify()
    path_list = path.split(os.sep)
    parsePath = ""
    for item in path_list:
        parsePath = parsePath + item + "\\"
    #print "This is the path list: ", path_list
    #print "This is parsePath: ", parsePath
    #outName = path_list[-1] + "__" + path_list[-2]
    #print "This is the out file name: ", outName
    
    # Find the dstat.csv
    dstatLog = find_dstat(path)
    dstatLogPath = parsePath + dstatLog
    #print dstatLogPath   
    
    # Parse data to DataFrame
    parsed = pd.read_csv(dstatLogPath, skiprows = 6)
    #print parsed
    
    # Calculate for each column and graph columns
    i = 0
    for each in nameList:
        if i < 3:
            usage = parsed[columnList[i]]
            name = nameList[i]
            cpu_use(usage, n, name)
        else:
            traffic = (((parsed[columnList[i]]) / 1024) / 1024)
            name = nameList[i]
            data_traffic(traffic, n, name)
        n += 1
        i += 1
    
    # Correlation and Covariance between usr and sys
    sysUsrCorr = parsed['usr'].corr(parsed['sys'])
    sysUsrCov = parsed['usr'].cov(parsed['sys'])
    print "This is the Correlation between User and System: ", sysUsrCorr
    print "This is the Covarience between User and System: ", sysUsrCov
    
    
main()