
import matplotlib.pyplot as plt
import re
import copy
import sys
import  get_spice_plot_data as gspd
 


def extractPlotData(spicePrintFile,argNames,argVecs,argScales):
  argIdx_base = 0
  firstPrintGroup = True 
  titleOn = False
  with open(spicePrintFile) as printFile : # open the print file
    found_x = False 
    gotArgNames = False   
    for line in printFile :             
       lineSplit = line.split()
       if not found_x :
         found_x = (lineSplit[0] == "x")  
         continue
       elif (found_x and not gotArgNames) : 
         for i in range(len(lineSplit)) :
              if (i==0 and not firstPrintGroup) : 
                 continue
              argNames.append(lineSplit[i])
              argVecs.append([])           
         gotArgNames = True
         continue
       elif lineSplit[0] == "y" : 
         firstPrintGroup = False 
         found_x = False
         gotArgNames = False
         argIdx_base = argIdx          
         continue
       else :
         argIdx = argIdx_base
         for i in range(len(lineSplit)) :
           if (i==0 and not firstPrintGroup) : 
              continue
           vstr = lineSplit[i]
           if vstr in ("k","m","u","n","p","f","a","K","M","G") :   
             if  argIdx==argIdx_base and not firstPrintGroup :  # ignored freq column has a unit char
                 continue         
             elif vstr=="k" :
              unitFactor = 10**3                         
             elif vstr=="m" :
              unitFactor = 10**-3              
             elif vstr=="u" : 
              unitFactor = 10**-6
             elif vstr=="n" :             
              unitFactor = 10**-9              
             elif vstr=="p" :             
              unitFactor = 10**-12              
             elif vstr=="f" :
              unitFactor = 10**-15
             elif vstr=="a" :
              unitFactor = 10**-18
             elif vstr=="K" :
              unitFactor = 10**3
             elif vstr=="M" :
              unitFactor = 10**6              
             elif vstr=="G" :
              unitFactor = 10**9              
             argVecs[argIdx-1][-1] = argVecs[argIdx-1][-1]*unitFactor
           else :
             argVecs[argIdx].append(float(vstr)*argScales[argIdx]) 
             argIdx = argIdx+1
  # finally remove lines with same value on first (x axis) value, iy seem to confuse matplotlib.pyplot
  for i in range (len(argVecs[0])-1,-1,-1) :
      if (i>0 and (argVecs[0][i]==argVecs[0][i-1])) :
         for j in range(len(argVecs)) :
           del (argVecs[j][i])


   
 
# main

 
if len(sys.argv)<=1 :
         print ("Missing Spectre output *.print file name")
         sys.exit(0)
     
srcNLname = sys.argv[1]     
 
argNames = []
argVecs = []
argScales = [1,1,1,-10000]

extractPlotData(srcNLname,argNames,argVecs,argScales)  

# plot the results
plt.figure(1)
plt.xlabel(argNames[0])
plt.plot(argVecs[0], argVecs[1], label=argNames[1])
plt.plot(argVecs[0], argVecs[2], label=argNames[2])
plt.plot(argVecs[0], argVecs[3], label=argNames[3])
plt.legend()
pltFileName = srcNLname[:srcNLname.find(".")]+".jpg"
plt.savefig(pltFileName)
plt.show()



   
         
         
