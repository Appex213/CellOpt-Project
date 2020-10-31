import random as rand
import re
import tokenize_string as tok
import os
import cellopt_paths

PATH_TO_SRCFILE  = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_in"
PATH_TO_INPUT  = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/pending"

class celloptParam : 
  def __init__(self,name,min,max): 
     self.name = name
     self.min  = min  
     self.max  = max
     self.currVal = 0 
 
         
class celloptUtil :

      masterFileName = "" 
      numParams = 0      

      def __init__(self): 
        self.parsDict = {}
                                             
      def defOptPar(self,name,min,max)     : 
          self.parsDict[name]=celloptParam(name,min,max)
          self.numParams += 1        

      def setMasterFileName(self, fileName) :
          self.masterFileName = fileName
                
      def genParamsRandom(self) :
         global par
         for (name,p) in self.parsDict.items() :
           p.currVal = rand.random()*(p.max-p.min) + p.min
           
      def genGridParams(self,index_list,pts_per_par) :
         pidx = 0
         for (name,p) in self.parsDict.items() :
           p.currVal = ((p.max-p.min)/(pts_per_par-1))*index_list[pidx] + p.min
           print("GEN_DBG: p.max=%e ; p.min=%e ; pts_per_par=%e ; pidx=%d , index_list[pidx] = %d ; p.currVal =%e" % (p.max,p.min,pts_per_par,pidx,index_list[pidx],p.currVal))           
           pidx += 1
      
                           
      def genSpiceNL(self,id="defID") : 
        srcFile = open(PATH_TO_SRCFILE+"/"+self.masterFileName,"r")  # source master
        srcFileNamePrefix = self.masterFileName[:self.masterFileName.find(".")] 
        modFile = open(PATH_TO_INPUT+"/"+srcFileNamePrefix+"_"+id+".sp","w")  # Generated with Modified parameters

        parDetected = False
        paramOn=False        
       
        for line in srcFile :
        
          if paramOn and (line[0]!="+") :
             paramOn = False
             
          #lineTokens = re.split('(\W)|=',line)
          lineTokens = tok.tokenizeString(line, ["\t"," ","=","\n"])

          for t in lineTokens :
              if t==".PARAM" :
                   paramOn = True                                                           
              elif paramOn and (t in self.parsDict.keys()) :
                   p = self.parsDict[t]
                   parDetected = True
              elif parDetected and (t!='=') and (t!=' ')  :
                   randInRange = rand.random()*(p.max-p.min) + p.min
                   if (randInRange < 1e-9) or (randInRange > 1e-6) : # not a nano scale value
                     t = "%-.3g" % randInRange
                   else :
                     t = ("%.0f" % round(randInRange*1e+9,3)) +"e-9"  # assumed preferred nano mantis                     
                   parDetected = False
                   
              modFile.write(t)
                                                
        srcFile.close()
        modFile.close()
        
        
        
      def genGridSpiceNL(self,id="defID") : 
        srcFile = open(PATH_TO_SRCFILE+"/"+self.masterFileName,"r")  # source master
        srcFileNamePrefix = self.masterFileName[:self.masterFileName.find(".")] 
        modFile = open(PATH_TO_INPUT+"/"+srcFileNamePrefix+"_"+id+".sp","w")  # Generated with Modified parameters

        parDetected = False
        paramOn=False        
       
        for line in srcFile :
        
          if paramOn and (line[0]!="+") :
             paramOn = False
             
          #lineTokens = re.split('(\W)|=',line)
          lineTokens = tok.tokenizeString(line, ["\t"," ","=","\n"])

          for t in lineTokens :
              if t==".PARAM" :
                   paramOn = True                                                           
              elif paramOn and (t in self.parsDict.keys()) :
                   p = self.parsDict[t]
                   parDetected = True
              elif parDetected and (t!='=') and (t!=' ')  :
                   gridInRange = p.currVal
                   if (gridInRange < 1e-9) or (gridInRange > 1e-6) : # not a nano scale value
                     t = "%-.3g" % gridInRange
                   else :
                     t = ("%.0f" % round(gridInRange*1e+9,3)) +"e-9"  # assumed preferred nano mantis                     
                   parDetected = False
                   
              modFile.write(t)
                                                
        srcFile.close()
        modFile.close()
        
        
        
        
        
                 



