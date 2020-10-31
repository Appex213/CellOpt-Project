import os

Qmin = 10
Qmax = 14
steps = 3

q = Qmin
deltaQ = float(Qmax-Qmin)/float(steps)
os.system("echo "" > sweep_qcrit.print")

for i in range(steps+1) : 
     
   qStr = "%2.2f" % q     
   os.system("sed 's/QVal/%s/g' c_element_sera_template.cir > sweep_qcritic_run.cir" % qStr)
   os.system("qrsh -V -cwd spectre sweep_qcritic_run.cir")   
   os.system("cp sweep_qcritic_run.print >> sweep_qcrit_%s.print" % str(i))
   os.system("cat sweep_qcritic_run.print >> sweep_qcrit.print")  
   q = q+deltaQ