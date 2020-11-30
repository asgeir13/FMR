#encoding: utf8
from __future__ import division
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import xml.etree.ElementTree as ET
import numpy as np
import sys,pickle,os.path,StringIO
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import periodictable as pt
from periodic.table import element
from poleFigure import *

import pdb

# The XMLPLOTTER is specifically written for the X'Pert X-Ray Diffraction 
# output file format .xrdml

# Reading the XML file structure and generate 2Theta and
# intensity axies

def readxml(string):
    if len(string) == 0:
        return 0,0,0
    root = ET.parse(string).getroot()
    rootLen = len(root)
    intens = []     # List to append all sets of intensities 
    props = {}      # Dict of properties
    common = '{http://www.xrdml.com/XRDMeasurement/1.5}' # All tags start with this string for some reason
    for i in range(2,rootLen):
        for child in root[i].iter():
            if spt(child.tag) == "scan":
                scanAxis = child.get('scanAxis')
                props["axis"] = scanAxis
                xAxis = scanAxis.split("-")[0] # This becomes 2Theta if scan is 2Theta-Omega
            if spt(child.tag) == "positions" and child.attrib['axis'] == xAxis:
                xStart = child.find(common+"startPosition").text
                xEnd = child.find(common+"endPosition").text
            if spt(child.tag) == "commonCountingTime":
                countingTime = float(child.text)
                props["time"] = countingTime
            if spt(child.tag) == "header":
                props["date"] = child.find(common+"startTimeStamp").text
            if spt(child.tag) == "intensities":
                I = [float(s) for s in child.text.split(" ")]
        intens.append(I)
    xAxis = np.linspace(float(xStart),float(xEnd), len(I))
    
    # Check if the scan includes multiple scans
    # such as wafer maps
    if np.shape(np.asarray(intens))[0] == 1:
        intens = np.squeeze(intens)

    # This function always retuns CPS
    return xAxis, np.asarray(I)/countingTime, props

    
def spt(tag):
    return tag.split('}')[-1]



def readxml_cts(string):    
    root = ET.parse(string).getroot()
    dataLen = len(root[2][5])
    # Index for the dataPoints
    datLoc = 8
    if (dataLen == 2):
        index = 1
        datLoc += 1
    elif (dataLen == 4):
        index = 3
    elif (dataLen == 3):
        index = 2

    rootLen = len(root)
    if rootLen > 3:
        intens = []
        for i in range(2,rootLen):
            dataTreeLength = len(root[i][5][index])
     
    # Get 2ThetaPositions
            if dataTreeLength == 10: #Attenuator
                I = np.array([float(s) for s in root[i][5][index][9].text.split(" ")])
                attenuation = np.array([float(s) for s in root[i][5][index][7].text.split(" ")])
                countingTime = float(root[i][5][index][8].text)

            elif dataTreeLength  == 9: #No Attenuator
                I = np.array([float(s) for s in root[i][5][index][8].text.split(" ")])
                attenuation = np.ones(len(intens))
                countingTime = float(root[i][5][index][7].text)
            intens.append(I)
        n = len(I)  
     
    
    else:
        dataTreeLength = len(root[2][5][index])

        if dataTreeLength == 10: #Attenuator
            intens = np.array([float(s) for s in root[2][5][index][9].text.split(" ")])
            attenuation = np.array([float(s) for s in root[2][5][index][7].text.split(" ")])
            countingTime = float(root[2][5][index][8].text)

        elif dataTreeLength  == 9: #No Attenuator
            intens = np.array([float(s) for s in root[2][5][index][8].text.split(" ")])
            attenuation = np.ones(len(intens))
            countingTime = float(root[2][5][index][7].text)

        n = len(intens)
    # Get 2ThetaPositions
    if root[2][5].attrib["scanAxis"] == 'Omega':
        endPoints = [float(root[2][5][index][1][0].text), float(root[2][5][index][1][1].text)]
    else:
        endPoints = [float(root[2][5][index][0][0].text), float(root[2][5][index][0][1].text)]
    scanAxis = np.linspace(endPoints[0], endPoints[1], n) 
    
    return scanAxis, intens, countingTime

def convData(inFileName,outFileName=None):    
    # Always returns data in CPS
    
    # If no output filename is given the function
    # outputs the same filename with .dat extension
    if isinstance(inFileName, basestring): # Check if inFileName is a string

        if not outFileName:
            outFileName = inFileName.split('.')[0]+'.dat'

        twoTheta, intens = readxml(inFileName)
         
        #if np.shape(intens)[1]:
        if outFileName[0] != '.':
            orgName = outFileName.split('.')[0]
        else:
            orgName = outFileName.split('.')[1]
        outExt = outFileName.split('.')[-1]

        if len(np.shape(intens)) == 1:
            n = 1
        else:
            n = np.shape(intens)[0]
        for i in range(0,n):
            if i != 0:
                outFileName = orgName + '_%i.' % (i,) + outExt
            delta = twoTheta[1]-twoTheta[0]
            write_header(outFileName, inFileName, 1,delta)
            if n == 1:
                write_element(outFileName, twoTheta,intens)
            else:
                write_element(outFileName, twoTheta,intens[i,:])

        print('%s successfully converted to file %s\n' % (inFileName,outFileName))
    
    elif isinstance(inFileName, list):
        print 'Its a list!'
        for filename in inFileName:
            twoTheta, intens = readxml(filename)
            outFileName = filename.split('.')[0]+'.dat'
            delta = twoTheta[1]-twoTheta[0]
            write_header(outFileName, filename, 1,delta)
            write_element(outFileName, twoTheta,intens)
            print('%s successfully converted to file %s' % (filename,outFileName))


    return 

def write_element(filename, val1,val2):
    f_handle = file(filename, 'a')
    tmp_array = np.column_stack((val1,val2))
    np.savetxt(f_handle, tmp_array, fmt="%.4f", delimiter="\t")
    f_handle.close()

def write_header(filename, val1, val2, val3):
    header = 'Original data: %s\nStep Size: %.5f\tCounting time: %.2f seconds\n2Theta\t#Intensity' % (val1,val3,val2)
    f_handle = file(filename, 'a')
    np.savetxt(f_handle,np.array([]).T,header=header)
    f_handle.close()

def elDens(volDens,elements,ratios):
    # Calculate electron density from the weight density in g/cm3
    uScatt = 0
    for i in range(len(elements)):
        uScatt += element(elements[i]).mass * ratios[i]
    rho = (volDens)/(1.66054 * uScatt)
    return rho


def volDens(elDens,elements,ratios):
    # Calculate weight density from the scatters density in atom/AA3
    uScatt = 0
    for i in range(len(elements)):
        uScatt += element(elements[i]).mass * ratios[i]
    
    rho = elDens*(1.66054 * uScatt)
    return rho

def view(fileList,scale='linear',legend='off',scanName=None,xlims=None,ylims=None, shift=0,customLegend=None, draw=False, fig=None,figWidth = 900, dpi=100, *args, **kwargs):
    
    if fig == None:
       fig = plt.figure(figsize=(figWidth/dpi,.5625*figWidth/dpi),dpi=dpi)

    props = {}
    ax = fig.add_subplot(111)
    lw=0.5
    Imax = 0
    Imin = 0
    TTmax = 0
    TTmin = np.inf
    if isinstance(fileList, list):
        i = 0
        for filename in fileList:
            tth,I,props = readxml(filename)
            scan_label = filename.split('/')[-1].split('.')[0].split('_')[0]
            if scale == 'log':
                ax.plot(tth,I*10**((i)*shift),label=scan_label, *args, **kwargs)
                if max(I)*10**((i)*shift) > Imax:
                    Imax = max(I)*10**((i)*shift)
                if min(I) < Imin:
                    Imin = min(I)
                #ax.set_ylim(Imin,Imax*1000)

            else:
                ax.plot(tth,I+i*shift,label=scan_label, *args, **kwargs)
                if max(I)+i*shift > Imax:
                    Imax = max(I)+i*shift
                if min(I) < Imin:
                    Imin = min(I)
                ax.set_ylim(Imin,Imax+100)
            
            if min(tth) < TTmin:
                TTmin = min(tth)
            if max(tth) > TTmax:
                TTmax = max(tth)
            i += 1
    elif isinstance(fileList, basestring) and len(fileList) > 0:
        tth,I,props = readxml(fileList)
        if len(np.shape(I)) > 1: # IF xrdml file includes more than one scan
            scanRange = [-35,35]
            scanList = [scan for scan in np.linspace(scanRange[0],scanRange[1],len(I))]
            for i in range(0,len(I)):
                if not scanName:
                    genScanName = fileList.split('/')[-1].split('_')[0] + ', y = %.0f' % (scanList[i],)
                    plt.plot(tth,I[i,:]+i*shift,label=genScanName,*args,**kwargs)
                else:
                    plt.plot(tth,I[i,:]+i*shift,label=scanName, *args, **kwargs)
                if max(I[i,:])+i*shift > Imax:
                    Imax = max(I[i,:])+i*shift
                if min(I[i,:])+i*shift < Imin:
                    Imin = min(I[i,:])+i*shift
                 
        else: # If xrdml inclues only one scan
            if not scanName:
                scanName = fileList.split('/')[-1].split('_')[0].split('_')[0]
            ax.plot(tth,I,label=scanName,*args,**kwargs)
            Imax = max(I);Imin = min(I)
        if xlims:
            TTmin = xlims[0];TTmax=xlims[1]
        else:
            TTmax = max(tth);TTmin = min(tth)
            
        if ylims:
            Imin = ylims[0];Imax = ylims[1]

    if fileList:    
        # Generate the figure
        ax.set_xlabel(r'2$\theta$ [deg.]',fontsize=14)
        ax.set_ylabel(r'Intensity [counts/s]',fontsize=14)
        ax.set_yscale(scale)
        ax.set_xlim(TTmin,TTmax)
    
    if legend == 'on':
            
        if customLegend:
            ax.legend(customLegend, loc='best', fontsize=12)
        else:
            ax.legend(loc='best',fontsize=8)
    elif legend == 'drag':
        leg = ax.legend(loc='best',fontsize=8)
        leg.draggable()
    
    ax.tick_params(axis='both',which='both',direction='in',labelsize=12)
    fig.subplots_adjust(bottom=0.10,left=0.08,right=0.96,top=0.96)
    if draw:
        return fig,ax,props
    else:
        plt.show()
        return 0

def weightPerc(materials, atRatios, output=False):
    if atRatios[0] < 1:
        atRatios = np.asarray(atRatios)*1e2
    if np.sum(atRatios) != 100:
        print('\nAttention!\nYour atomic ratios don\'t add to 100%\n')
    n = len(materials)
    weights = np.zeros(n)
    p = np.zeros(n)
    i = 0
    for element in materials:
        for elem in pt.elements:
            if elem.symbol == element:
                weights[i] = elem.mass

        p[i] = weights[i]*atRatios[i]
        i += 1

    wtRatios = p/np.sum(p)
    if output == "print":
        print('Weight% calculation results:')
        for i in range(0,n):
            print(' %s\t%.1f %%at.\t%.1f %%wt.' % (materials[i],atRatios[i],1e2*wtRatios[i]))
    if output == "genx":
        genxString = ""
        for i in range(n):
            genxString += "fw.%s*%.3f+" % (materials[i],wtRatios[i])
        print(genxString[:-1])
    return np.around(wtRatios*1e2,1)

def atomicPerc(materials, wtRatios, output = False):
    n = len(materials)
    weights = np.zeros(n)
    p = np.zeros(n)
    i = 0
    for element in materials:
        for elem in pt.elements:
            if elem.symbol == element:
                weights[i] = elem.mass
        p[i] = wtRatios[i]/weights[i]
        i += 1
    atRatios = p/np.sum(p)    
    if output:
        print('Atomic % calculation results:')
        for i in range(0,n):
            print(' %s\t%.1f %%wt.\t%.1f %%at.' % (materials[i],wtRatios[i],1e2*atRatios[i]))

    return np.around(atRatios*1e2,1)

# Esitmate density from weight percentage
# Formula from:
# http://www.indium.com/blog/interest-in-formula-for-calculating-alloy-density-still-keen-1.php
# 1/rho = x/rho_x + y/rho_y + ...

def weightDens(elements, weights, output=False):
    n = len(elements)
    invRho = 0
    i = 0
    if sum(weights) >= 1:
        weights = np.asarray(weights)/100
    else:
        weights = np.asarray(weights)
    for item in elements:
        for elem in pt.elements:
            if elem.symbol == item or elem.name.lower() == item.lower():
                invRho += weights[i]/elem.density
                i += 1
    if output:
        alloy = ""
        for i in range(n):
            alloy += " %.2f*%s +" % (weights[i],elements[i])
        alloy = alloy[1:-2]
        print("Density of (%s) is: %.2f g/cm3" % (alloy, invRho,))

    return 1/invRho



def getDatabase(DBfile):
    # 
    # Module to read a database file previously generated by this 
    # 
    global database
    DB = open(DBfile, 'r')
    database = DB.read()
    DB.close()
    if len(database) > 0:
        database = pickle.loads(database)
    else:
        print('Database has no entries')
        return 0
    return database

