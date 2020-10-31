import cellopt_parser as parser
import os
import time
import csv
from collections import OrderedDict
import numpy as np

INPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/pending"
OUTPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/output"
RUNSPACE = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/runspace"
OPTIN = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_in"


class Param:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class caseParams:
    def __init__(self, caseID):
        self.caseID = caseID
        self.params = []

    def add_param(self, param):
        self.params.append(param)


class plot2D:
    def __init__(self):
       self.xVals = None
       self.yVals = None 
       self.zVals = None
       
    def create_npArrays(self, num_pts_per_par):
       self.xVals = np.zeros(shape=num_pts_per_par)
       self.yVals = np.zeros(shape=num_pts_per_par)
       self.zVals = np.zeros(shape=(num_pts_per_par,num_pts_per_par))

    def update_npArrays(self, xIdx,yIdx,xVal,yVal,zVal):
       if (self.xVals[xIdx]!=0) and (self.xVals[xIdx]!=xVal) :
         print ("ERROR xVal mismatch, Quitting")
         print ("ERROR xVal mismatch, Quitting xIdx=%d,xVals[xIdx]=%e,xVal=%e" % (xIdx,xVals[xIdx],xVal))
         exit()
       if (self.yVals[yIdx]!=0) and (self.yVals[yIdx]!=yVal) :
         print ("ERROR yVal mismatch, Quitting yIdx=%d,yVals[yIdx]=%e,yVal=%e" % (yIdx,yVals[yIdx],yVal))
         exit()
       self.xVals[xIdx] = xVal
       self.yVals[yIdx] = yVal       
       self.zVals[xIdx,yIdx] = zVal
       
    def dump(self) :
       print("p2D dump")
       print ("self.xVals=\n%s" % self.xVals )
       print ("self.yVals=\n%s" % self.yVals )
       print ("self.zVals=\n%s" % self.zVals )
       
         
class caseInfo:
    def __init__(self):
        self.casePars = None
        # Currently the skew gap of the run (which we wish to minimize)
        self.result = 10**9
        self.start_time = time.time()
        self.launch_command = ''


class coptDB:
    def __init__(self, dbFileName, master_cell_name):
        self.casesDict = OrderedDict()
        self.master_cell = master_cell_name
        self.dbFileName = dbFileName
        self.createDbFile()
        self.p2D = plot2D()

    def insertCase(self, caseID, launchCmd, start):
        caseInf = caseInfo()
        caseInf.start_time = time.time() - start
        case_path = RUNSPACE + '/' + caseID + '/' + caseID + '.sp'
        casePars = parser.get_sp_params(case_path)
        caseInf.params = casePars
        caseInf.launch_command = launchCmd
        self.casesDict[caseID] = caseInf

    def updateCaseResults(self, caseID):
        result_path = RUNSPACE + "/" + caseID + "/" + caseID + "_datasheet.txt"
        # while not os.path.exists(result_path)
        #     time.sleep(0.1)
        self.casesDict[caseID].result = parser.get_gap(result_path)
        self.updateDbFile(caseID)

    def createDbFile(self):
        dbFile = open(OPTIN + '/' + self.dbFileName + '.csv', 'w+')
        master_pars = parser.get_sp_params(
            OPTIN + '/' + self.master_cell + '.sp')
        title_line = "caseID,"
        for key in master_pars:
            title_line = title_line + key + ','
        title_line = title_line + 'result\n'
        dbFile.write(title_line)
        dbFile.close()

    def updateDbFile(self, caseID):
        print("DEBUG: updateDBfile called for caseID " + caseID)
        dbFile = open(OPTIN + '/' + self.dbFileName + '.csv', 'a')
        case_entry = caseID + ','
        num_params = 0
        for key in self.casesDict[caseID].params:
            case_entry = case_entry + \
                str(self.casesDict[caseID].params[key]) + ','
            if (num_params==0) :
             xVal = self.casesDict[caseID].params[key] 
            if (num_params==1) :
             yVal = self.casesDict[caseID].params[key]              
            num_params += 1
        case_entry = case_entry + str(self.casesDict[caseID].result) + '\n'
        dbFile.write(case_entry)
        dbFile.close()
        if (num_params==2) :
          xIdx = int(caseID.split("_")[2])
          yIdx = int(caseID.split("_")[3])
          zVal = self.casesDict[caseID].result
          self.p2D.update_npArrays(xIdx,yIdx,xVal,yVal,zVal)
           
    def read_csv(self, src_file):
        with open(src_file, 'r') as csv_db:
            reader = csv.reader(csv_db)
            first_line = True
            keys = []
            for row in reader:
                if first_line:
                    keys = row
                    first_line = False
                else:
                    casePars = OrderedDict()
                    for index in range(1, len(row) - 1):
                        casePars[keys[index]] = row[index]
                    caseInf = caseInfo()
                    caseInf.casePars = casePars
                    caseInf.result = row[-1]
                    self.casesDict[row[0]] = caseInf

            csv_db.close()


# Create python grid mode plot file
#  # Applicable only for 2 parameters , assuming 2 parameters
#
#   def createGridPyPlotFile(self,pts_per_par):     
#       gpFile = open(OPTIN + '/' + self.dbFileName + '_gridPlot.py', 'w+')
#       gpFile.write("import numpy as np")
#       gpFile.write("from scipy.interpolate import interp2D")
#       gpFile.write("from mpl_toolkits import mplot3d")
#       gpFile.write("import matplotlib.pyplot as plt")
#       gpFile.close()
#
#   def updateGridPyPlotFile(self, caseID):
#       print("DEBUG: updateDBfile called for caseID " + caseID)
#       gpFile = open(OPTIN + '/' + self.dbFileName + '.csv', 'a')
#       case_entry = caseID + ','
#       for key in self.casesDict[caseID].params:
#           case_entry = case_entry + \
#               str(self.casesDict[caseID].params[key]) + ','
#       case_entry = case_entry + str(self.casesDict[caseID].result) + '\n'
#       gpFile.write(case_entry)
#       gpFile.close()
