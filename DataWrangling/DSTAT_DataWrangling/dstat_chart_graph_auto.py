__author__ = 'jrschac'
# DSTAT Automation of Chart and Graph to Excel
# Author: Jeffrey Schachtsick
# Last Update: 02/10/2014
# Description: This script is designed to take data from DSTAT CSV file and place into
#    a spreadsheet.  Then create a few graphs based on the data in the columns from the DSTAT.
# Libraries used: python 2.7.5, python-dateutil-1.5, xlsxwriter

import os
import xlsxwriter
import re
import csv

def userSpecify():
    """User specifies directory, to go to"""
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

def open_file(file_name):
    """Open a file."""
    try:
        the_file = open(file_name)
    except IOError as e:
        print("Unable to open the file", file_name)
        the_file = ""
    return the_file

def read_csv_lines(the_file, worksheet, w):
    """ Parse the cells from rows in a .csv file and store into arrays"""
    ListOfData = []
    Cpu_Usage = 'usr', 'sys', 'idl', 'wai', 'hiq', 'siq'
    Cpu_bool = False
    Mem_Usage = 'used', 'buff', 'cach', 'free'
    Mem_bool = False
    Disk_Usage = 'read', 'writ'
    Disk_bool = False
    Net_Usage = 'recv', 'send'
    Net_bool = False
    rowNum = 0
    lineCount = 0

    reader = csv.reader(the_file)
    for row in reader:
        colNum = 0
        if None in row:
            continue
        if "total cpu usage" in row:
            ListOfData.append(Cpu_Usage)
            Cpu_bool = True
            if "memory usage" in row:
                ListOfData.append(Mem_Usage)
                Mem_bool = True
            if 'dsk/sda1' in row:
                ListOfData.append(Disk_Usage)
                Disk_bool = True
            if ('net/eth0' or 'net/eth1' or 'net/eth2' or 'net/eth3') in row:
                ListOfData.append(Net_Usage)
                Net_bool = True
                continue
        worksheet[w].write_row(rowNum, colNum, row)
        for i in row:
            try:
                i = float(i)
                worksheet[w].write(rowNum, colNum, i)
                colNum = colNum + 1
            except ValueError:
                continue
        rowNum = rowNum + 1
        lineCount = lineCount + 1
        continue
    return Cpu_bool, Mem_bool, Disk_bool, Net_bool, worksheet, lineCount

def seperate_file(file):
    """ Parse the name of the node"""
    firstHalf = file.split("\\"[-1])
    #print "This is the node", firstHalf[-2]
    node = firstHalf[-2]
    print "\nReading results for ", node
    return node

def graph_cpu_user_sys(workbook, node, lineCount):
    """ This will create a graph showing Total CPU usage with User and System"""
    #worksheet = workbook.add_worksheet(node + 'Graphs')
    #print "This is the worksheet: ", worksheet
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 5, 0], 'values': [node, 6, 0, lineCount, 0],})
    chart.add_series({'name': [node, 5, 1], 'values': [node, 6, 1, lineCount, 1],})
    chart.set_title({'name': 'CPU User/Sys Usage'})
    chart.set_y_axis({'name': 'Usage %'})
    chart.set_size({'width': 550, 'height': 400})
    return  chart

def graph_cpu_idle(workbook, node, lineCount):
    """ This will create a chart showing Total CPU Idle in each trace"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 5, 2], 'values': [node, 6, 2, lineCount, 2],})
    chart.set_title({'name': 'CPU Idle'})
    chart.set_y_axis({'name': 'Idle %'})
    chart.set_size({'width': 550, 'height': 400})
    return chart

def graph_mem_free(workbook, node, lineCount):
    """ This will create a chart showing Memory free per trace"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 5, 9], 'values': [node, 6, 9, lineCount, 9],})
    chart.set_title({'name': 'Memory Free'})
    chart.set_y_axis({'name': 'Free Mem(MB)'})
    chart.set_size({'width': 550, 'height': 400})
    return chart

def graph_disk_io(workbook, node, lineCount):
    """ This will create a chart showing read and write of disks during tracing"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 5, 10], 'values': [node, 6, 10, lineCount, 10],})
    chart.add_series({'name': [node, 5, 11], 'values': [node, 6, 11, lineCount, 11],})
    chart.set_title({'name': 'Disk I/O'})
    chart.set_y_axis({'name': 'r/w trans.(Mb)'})
    chart.set_size({'width': 550, 'height': 400})
    return chart

def graph_net_trans(workbook, node, lineCount):
    """ This will create a chart showing network traffic"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 5, 12], 'values': [node, 6, 12, lineCount, 12],})
    chart.add_series({'name': [node, 5, 13], 'values': [node, 6, 13, lineCount, 13],})
    chart.set_title({'name': 'Network'})
    chart.set_y_axis({'name': 'Traffic(Mb)'})
    chart.set_size({'width': 550, 'height': 400})
    return chart


def main():
    """ Main management of all functions"""
    path = userSpecify()
    newWorksheet = []
    w = 0
    path_list = path.split(os.sep)
    #print "This is the path list: ", path_list
    dirName = path_list[-1]
    #print "This is the Directory Name: ", dirName

    #List logs into an array
    print "\nFinding dstat logs ..."
    ListOfLogs = []
    for r,d,f in os.walk(path, topdown=False):
       for files in f:
           if files.endswith(".csv") and "dstat" in files:
               ListOfLogs.append(os.path.join(r,files))
    for z in ListOfLogs:
       print "Logs found: ", z
    workbook = xlsxwriter.Workbook(dirName + '_DSTAT_Test.xlsx')
    #print "Created a workbook!", workbook
    print "Created a workbook!"
    file_date_tuple_list = []
    for x in ListOfLogs:
        #Organize list of Logs in reverse order to display latest analysis first
        d = os.path.getmtime(x)
        file_date_tuple = (x,d)
        file_date_tuple_list.append(file_date_tuple)
        file_date_tuple_list.sort(key=lambda x: x[1], reverse=True)
    for each in file_date_tuple_list:
        ListOfCharts = []
        file = open_file(each[0])
        node = seperate_file(each[0])
        newWorksheet.append(workbook.add_worksheet(node))
        #print "Created ", node, " worksheet."
        #print "This is the worksheet here: ", worksheet
        Cpu_bool, Mem_bool, Disk_bool, Net_bool, newWorksheet, lineCount = read_csv_lines(file, newWorksheet, w)
        #print "Cpu_bool is: ", Cpu_bool
        #print "Mem_bool is: ", Mem_bool
        #print "Disk_bool is: ", Disk_bool
        #print "Net_bool is: ", Net_bool
        #Add Graphs
        rowGraph = 7
        columnGraph = 15
        if Cpu_bool == True:
            cpuUsrSysChart = graph_cpu_user_sys(workbook, node, lineCount)
            ListOfCharts.append(cpuUsrSysChart)
            cpuIdleChart = graph_cpu_idle(workbook, node, lineCount)
            ListOfCharts.append(cpuIdleChart)
            #print "Here is the list of Charts: ", ListOfCharts
        else:
            print "Failure: Data missing for Total CPU Usage!"
        if Mem_bool == True:
            memFreeChart = graph_mem_free(workbook, node, lineCount)
            ListOfCharts.append(memFreeChart)
        else:
            print "Failure: Data missing for Memory Usage!"
        if Disk_bool == True:
            diskIOChart = graph_disk_io(workbook, node, lineCount)
            ListOfCharts.append(diskIOChart)
        else:
            print "Failure: Data missing from Disk Usage!"
        if Net_bool == True:
            netTraffChart = graph_net_trans(workbook, node, lineCount)
            ListOfCharts.append(netTraffChart)
        else:
            print "Failure: Data missing from Network Usage!"
        for graph in ListOfCharts:
            newWorksheet[w].insert_chart(rowGraph,columnGraph, graph)
            rowGraph = rowGraph + 21
        w = w + 1
    print "Writing to workbook..."
    workbook.close()

main()

