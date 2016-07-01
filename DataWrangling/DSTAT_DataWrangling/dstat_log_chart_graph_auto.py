__author__ = 'jrschac'
# DSTAT Automation of Chart and Graph to Excel
# Author: Jeffrey Schachtsick
# Last Update: 02/10/2014
# Description: This script is designed to take data from DSTAT log file and place into
#    a spreadsheet.  Then create a few graphs based on the data in the columns from the DSTAT.
# Libraries used: python 2.7.5, python-dateutil-1.5, xlsxwriter

import os
import xlsxwriter
import re

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

def read_lines(the_file, worksheet, w):
    """ Parse the lines from .log file and store into arrays"""
    ListOfData = []
    Cpu_Usage = 'usr', 'sys', 'idl', 'wai', 'hiq', 'siq'
    Cpu_bool = False
    Mem_Usage = 'used', 'buff', 'cach', 'free'
    Mem_bool = False
    Disk_Usage = 'read', 'writ'
    Disk_bool = False
    Net_Usage = 'recv', 'send'
    Net_bool = False
    rowNum = 7
    lineCount = 8

    #with open(the_file) as input_data:
    for line in the_file:
        if "failed" in line:
            error_mssg = line
            print "Error message found in log: ", error_mssg
            worksheet[w].write(0, 0, 'Error Message in log: ' + error_mssg)
            continue
        if "total-cpu-usage" in line:
            ListOfData.append(Cpu_Usage)
            worksheet[w].write(6, 0, 'Total CPU Usage')
            Cpu_bool = True
            if "memory-usage" in line:
                ListOfData.append(Mem_Usage)
                worksheet[w].write(6, 6, 'Memory Usage')
                Mem_bool = True
            if "dsk/sd" in line:
                ListOfData.append(Disk_Usage)
                worksheet[w].write(6, 10, 'Disk Usage')
                Disk_bool = True
            if "net/eth" in line:
                ListOfData.append(Net_Usage)
                worksheet[w].write(6, 12, 'Network Usage')
                Net_bool = True
                continue
            continue
        else:
            line = line.replace("|", " ")
            line = line.replace("\n", "")
            line = re.sub(" +", " ", line)
            lineCount = lineCount + 1
            if line[0] == " ":
                line = line[1:]
            else:
                line = line[0:]
            #print line
            for a in ListOfData:
                colNum = 0
                a = [[y] for y in line.split(" ")]
                #print "This is an a: ", a
                for i in a:
                    #print "This is i:", i[0]
                    if "M" in i[0]:
                        i[0] = (float(i[0].replace("M", ""))*1048576)
                    elif "k" in i[0] and not "dsk" in i[0] and not "ticks" in i[0]:
                        i[0] = (float(i[0].replace("k", ""))*1024)
                    elif "B" in i[0]:
                        i[0] = (float(i[0].replace("B", "")))
                    elif "G" in i[0]:
                        i[0] = (float(i[0].replace("G", ""))*1073741824)
                    try:
                        i = float(i[0])
                        #print "Converting to float!"
                        worksheet[w].write_number(rowNum, colNum, i)
                        colNum = colNum + 1
                    except:
                        worksheet[w].write_row(rowNum, colNum, i)
                        colNum = colNum + 1
            rowNum = rowNum + 1
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
    chart.add_series({'name': [node, 7, 0], 'values': [node, 8, 0, lineCount, 0],})
    chart.add_series({'name': [node, 7, 1], 'values': [node, 8, 1, lineCount, 1],})
    chart.set_title({'name': 'CPU User/Sys Usage'})
    chart.set_y_axis({'name': 'Usage %'})
    chart.set_size({'width': 550, 'height': 400})
    return  chart

def graph_cpu_idle(workbook, node, lineCount):
    """ This will create a chart showing Total CPU Idle in each trace"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 7, 2], 'values': [node, 8, 2, lineCount, 2],})
    chart.set_title({'name': 'CPU Idle'})
    chart.set_y_axis({'name': 'Idle %'})
    chart.set_size({'width': 550, 'height': 400})
    return chart

def graph_mem_free(workbook, node, lineCount):
    """ This will create a chart showing Memory free per trace"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 7, 9], 'values': [node, 8, 9, lineCount, 9],})
    chart.set_title({'name': 'Memory Free'})
    chart.set_y_axis({'name': 'Free Mem(MB)'})
    chart.set_size({'width': 550, 'height': 400})
    return chart

def graph_disk_io(workbook, node, lineCount):
    """ This will create a chart showing read and write of disks during tracing"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 7, 10], 'values': [node, 8, 10, lineCount, 10],})
    chart.add_series({'name': [node, 7, 11], 'values': [node, 8, 11, lineCount, 11],})
    chart.set_title({'name': 'Disk I/O'})
    chart.set_y_axis({'name': 'r/w trans.(Mb)'})
    chart.set_size({'width': 550, 'height': 400})
    return chart

def graph_net_trans(workbook, node, lineCount):
    """ This will create a chart showing network traffic"""
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'name': [node, 7, 12], 'values': [node, 8, 12, lineCount, 12],})
    chart.add_series({'name': [node, 7, 13], 'values': [node, 8, 13, lineCount, 13],})
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
        Cpu_bool, Mem_bool, Disk_bool, Net_bool, newWorksheet, lineCount = read_lines(file, newWorksheet, w)
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
            #newWorksheet.insert_chart('P28', memFreeChart)
        else:
            print "Failure: Data missing for Memory Usage!"
        if Disk_bool == True:
            diskIOChart = graph_disk_io(workbook, node, lineCount)
            ListOfCharts.append(diskIOChart)
            #newWorksheet.insert_chart('Y28', diskIOChart)
        else:
            print "Failure: Data missing from Disk Usage!"
        if Net_bool == True:
            netTraffChart = graph_net_trans(workbook, node, lineCount)
            ListOfCharts.append(netTraffChart)
            #newWorksheet.insert_chart('P49', netTraffChart)
        else:
            print "Failure: Data missing from Network Usage!"
        for graph in ListOfCharts:
            newWorksheet[w].insert_chart(rowGraph,columnGraph, graph)
            rowGraph = rowGraph + 21
        w = w + 1
    workbook.close()

main()