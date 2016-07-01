__author__ = 'jrschac'
# DSTAT Automation of generating statistical information between nodes
# Author: Jeffrey Schachtsick
# Last Update:
# Description: This script is designed to look at data inside an already created spreadsheet and create
# useful statistical data in a summary tab between nodes.
# Libraries used: python 2.7.5, xlsxwriter

# Imports
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

def multi_node_graph_cpu_user(chart, sheet, node, workbook, lines, color, average):
    """ This will add series from each node to the chart """
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes CPU User Usage'})
        chart.set_y_axis({'name': 'Usage %'})
        chart.set_size({'width': 1400, 'height': 650})
    #chart.add_series({'values': [sheet, 6, 0, lines, 0], 'line': {'width': 0}, 'trendline': {'type': 'polynomial','name': node, 'order': 10}})
    #chart.add_series({'values': [sheet, 6, 0, lines, 0], 'line': {'width': 0}, 'trendline': {'type': 'moving_average', 'name': node, 'period': 20}})
    chart.add_series({'values': [sheet, 6, 0, lines, 0], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_cpu_sys(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart."""
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes CPU System Usage'})
        chart.set_y_axis({'name': 'Usage %'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 1, lines, 1], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_cpu_idle(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart for Idle CPU usage"""
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes CPU% in Idle'})
        chart.set_y_axis({'name': 'Idle %'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 2, lines, 2], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_mem_free(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart for Disk Free memory """
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes with Free Memory'})
        chart.set_y_axis({'name': 'Free Mem(MB)'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 9, lines, 9], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_read_IO(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart for Disk IO read """
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes with Read Disk IO'})
        chart.set_y_axis({'name': 'read trans.(Mb)'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 10, lines, 10], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_write_IO(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart for Disk IO read """
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes with Write Disk IO'})
        chart.set_y_axis({'name': 'write trans.(Mb)'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 11, lines, 11], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_recive_net(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart for Network Recieved """
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes with Network Recieved'})
        chart.set_y_axis({'name': 'Traffic (Mb)'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 12, lines, 12], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def multi_node_graph_send_net(chart, sheet, node, workbook, lines, color, average):
    """ This will add a series for each node to a chart for Network Sent """
    if chart is None:
        chart = workbook.add_chart({'type': 'line'})
        chart.set_title({'name': 'Multiple Nodes with Network Sent'})
        chart.set_y_axis({'name': 'Traffic (Mb)'})
        chart.set_size({'width': 1400, 'height':650})
    chart.add_series({'values': [sheet, 6, 13, lines, 13], 'line': {'none': True}, 'name': node,
                      'trendline': {'type': 'moving_average', 'period': average, 'line': {'color': color}}})
    return chart

def createStatSheet(workbook, ListOfNodes, LineCounts):
    """ This create a stat sheet and manage statistical functions"""
    print "Creating Stat Sheet..."
    statsheet = []
    chartCpuUser = None
    chartCpuSys = None
    chartCpuIdle = None
    chartMemFree = None
    chartReadDisk = None
    chartWriteDisk = None
    chartNetReceive = None
    chartNetSend = None
    LineColor = ['black', 'yellow', 'blue', 'silver', 'brown', 'red', 'cyan', 'purple', 'gray', 'pink', 'green',
                 'orange', 'lime', 'navy', 'magenta']
    statsheet.append(workbook.add_worksheet('Stat_Sheet'))
    average = raw_input("Please enter the period for moving average: ").strip()
    x = 0
    c = 0
    for sheet in ListOfNodes:
        #print "This is awesome!  ", x
        node = ListOfNodes[x]
        lines = LineCounts[x]
        color = LineColor[c]
        chartCpuUser = multi_node_graph_cpu_user(chartCpuUser, sheet, node, workbook, lines, color, average)
        chartCpuSys = multi_node_graph_cpu_sys(chartCpuSys, sheet, node, workbook, lines, color, average)
        chartCpuIdle = multi_node_graph_cpu_idle(chartCpuIdle, sheet, node, workbook, lines, color, average)
        chartMemFree = multi_node_graph_mem_free(chartMemFree, sheet, node, workbook, lines, color, average)
        chartReadDisk = multi_node_graph_read_IO(chartReadDisk, sheet, node, workbook, lines, color, average)
        chartWriteDisk = multi_node_graph_write_IO(chartWriteDisk, sheet, node, workbook, lines, color, average)
        chartNetReceive = multi_node_graph_recive_net(chartNetReceive, sheet, node, workbook, lines, color, average)
        chartNetSend = multi_node_graph_send_net(chartNetSend, sheet, node, workbook, lines, color, average)
        x = x + 1
        c = c + 1
        if c == 15:
            c = 0
    x = x - 1
    #chartCpuUser = chartCpuUser.set_legend({'delete_series': [0, 3]})
    statsheet[0].write('A1', 'Run Date: ')
    statsheet[0].write('D1', 'Number of Nodes run: ')
    statsheet[0].write('F1', 'Run time to complete(seconds): ')
    statsheet[0].write('A2', 'uCluster Tray: ')
    statsheet[0].write('D2', 'uCluster FW (MC, RC, ethtray): ')
    statsheet[0].write('A3', 'CPU type: ')
    statsheet[0].write('D3', 'EC CPU version: ')
    statsheet[0].write('A4', 'OS version: ')
    statsheet[0].write('D4', 'igb version: ')
    statsheet[0].write('F4', 'SSD space: ')
    statsheet[0].write('A5', 'Other configuration: ')
    statsheet[0].write('B7', 'Moving Average for graphs below is ' + average)
    statsheet[0].insert_chart('B8', chartCpuUser)
    statsheet[0].insert_chart('B41', chartCpuSys)
    statsheet[0].insert_chart('B74', chartCpuIdle)
    statsheet[0].insert_chart('B107', chartMemFree)
    statsheet[0].insert_chart('B140', chartReadDisk)
    statsheet[0].insert_chart('B173', chartWriteDisk)
    statsheet[0].insert_chart('B206', chartNetReceive)
    statsheet[0].insert_chart('B239', chartNetSend)
    statsheet[0].activate()
    return workbook

def main():
    """ Main management of all functions"""
    path = userSpecify()
    newWorksheet = []
    lineCounts = []
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
    ListOfNodes = []
    n = 0
    for each in file_date_tuple_list:
        ListOfCharts = []
        file = open_file(each[0])
        node = seperate_file(each[0])
        ListOfNodes.append(node)
        n = n + 1
        newWorksheet.append(workbook.add_worksheet(node))
        #print "Created ", node, " worksheet."
        #print "This is the worksheet here: ", worksheet
        Cpu_bool, Mem_bool, Disk_bool, Net_bool, newWorksheet, lineCount = read_csv_lines(file, newWorksheet, w)
        lineCounts.append(lineCount)
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
    workbook = createStatSheet(workbook, ListOfNodes, lineCounts)
    print "Writing to workbook..."
    workbook.close()

main()
