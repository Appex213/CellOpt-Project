import sys
import os
import random
import shutil
import time
import datetime

import cellopt_util as util
import cellopt_config as conf
import cellopt_db_manager as db

OPTIN  = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_in"
INPUT  = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/pending"
OUTPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/output"
RUNSPACE = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/runspace"



SPACE = " "        # space for command string extraction
BACKGROUND = " & " # run in background for command string extraction

def system_call(cmd_str) :
    status = os.system(cmd_str)
    if status != 0:
        print ("ERROR @ launcher.py : System Call Error on : " + cmd_str)
        exit()

 
def check_timeout(caseID, start, launchCmd):
    elapsed_time = time.time() - start
    print(str(time.time())+'     '+str(start))     # DEBUG
    if elapsed_time > 100:
        print("DEBUG: elapsed_time = "+str(elapsed_time))     # DEBUG
        print("WARNING: Item "+caseID+" timed out, ignoring...")
        # system_call("$CELL_OPT_ROOT_DIR/utils/reset_char_cell.sh "+caseID)
        # shutil.rmtree(RUNSPACE + "/" + caseID)
        # system_call(launchCmd)
        queue.remove(caseID)
                
    
def run(cell_name, parallel_runs):
    parallel_runs = parallel_runs-1
    start = time.time()
    queue = []
    timed_out = []
    source_file_name = ''
    
    system_call("$CELL_OPT_ROOT_DIR/utils/clean_workspace.sh")
    
    for index in range(0,int(sys.argv[2])):
        rnd_netlist = util.celloptUtil()
        conf.defineOptParams(rnd_netlist)
        rnd_netlist.genParamsRandom()
        rnd_netlist.genSpiceNL(str(index))
    
    database = db.coptDB(cell_name+'_DB',cell_name)
    
    while True:
        # Adding files to liberate queue
        if queue.__len__() <= parallel_runs:
         
            # poll till source file is found
            pending_src_files = os.listdir(INPUT)
            if len(pending_src_files) > 0 :
                source_file_name = random.choice(os.listdir(INPUT)) 
                
                # prepare command    
                source_file_name_nopath_noext =  source_file_name.split('.')[0]
                cmd_str = "$CELL_OPT_ROOT_DIR/utils/launch_char_cell.sh " + source_file_name_nopath_noext + SPACE + cell_name 
                redirect_launch_log_str = " > $CELL_OPT_ROOT_DIR/workspace/launch_logs/" + source_file_name_nopath_noext + ".log"
                launch_command = cmd_str + redirect_launch_log_str
                system_call(launch_command)
                print ("INFO: launcher.py issued following system call")
                print (launch_command)
                        
                queue.append(source_file_name_nopath_noext)       # Add to queue
                print("INFO: Added " + source_file_name + " to queue.")
            
                time.sleep(0.25)     # Prevent source deleting timing issue
                database.insertCase(source_file_name_nopath_noext,launch_command,start)      # Add to DB
            
            elif queue.__len__() == 0:
                print("TMP MSG: No pending files, quitting , ... currently a generator is not yet available");
                print("TMP MSG: to reload pending dir, execute: cp workspace/tmp/pending/* workspace/pending/");
                end = time.time()     # DEBUG
                print("INFO: Total runtime: " + str(end - start) + " sec")     # DEBUG
                if timed_out is not []:
                    print("INFO: The following items timed out:")
                    print(timed_out)
                   
                quit()
              
            else:   # If queue is full, wait to prevent msg spam
                time.sleep(5)

        else:   # If queue is full, wait to prevent msg spam
            time.sleep(5)
         
         
        # Removing done files from liberate queue and input folder
        print("DEBUG: current queue:")      # DEBUG
        # print(queue)
        print("INFO: Items in queue: " + str(queue.__len__()))
        print("INFO: Items pending: " + str(pending_src_files.__len__()))
        # print("INFO: Elapsed time: " + str(time.time() - start) + " sec")
        t = time.time() - start
        print("INFO: Elapsed time: " + str(datetime.timedelta(seconds=round(t))))
        for file in queue:
            # check_timeout
            item_time = time.time() - start - database.casesDict[file].start_time
            print(file+'  |  '+str(item_time))
            if (item_time) > 400 :      # timeout condition
                print("WARNING: Item "+file+" timed out and will be ignored. ("+str(item_time)+" sec)")
                timed_out.append(file)
                queue.remove(file)
                print("INFO: " + file + " removed from queue.")
                
            elif os.path.exists(RUNSPACE + "/" + file + "/" + file + "_datasheet.txt"):
                print("INFO: " + file + " is done, updating DB")
                database.updateCaseResults(file)
                #shutil.rmtree(RUNSPACE + "/" + file)     # Remove from runspace
                queue.remove(file)        # Remove from queue
                print("INFO: " + file + " removed from queue.")
        

run('FA', int(sys.argv[1])) # arg1 = queue length, arg2 = netlists to generate
