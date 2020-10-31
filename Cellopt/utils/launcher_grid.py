import sys
import os
import random
import shutil
import time
import datetime

import cellopt_util as util
import cellopt_db_manager as db
from itertools import product

sys.path.append(os.environ["CELL_OPT_ROOT_DIR"] + "/local_utils")
import cellopt_config as conf  


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
    

    pts_per_par = int(sys.argv[2])  # number of points per prameter , currently we assume same for all 
    
    ref_netlist = util.celloptUtil()
    conf.defineOptParams(ref_netlist)
    num_params = ref_netlist.numParams
    
    one_dim = list(range(pts_per_par))
    all_dim = [one_dim] * num_params
    # all_dim is now a list of lists, one for each dimension, each list contains the values 0 to num_params-1
    
    # Now iterate over the multi dimention indexes
    for index_list in product(*all_dim):
         grid_point_netlist = util.celloptUtil()
         conf.defineOptParams(grid_point_netlist)
         grid_point_netlist.genGridParams(index_list,pts_per_par)
         idx_str = ""
         for idx in index_list :
           idx_str = idx_str+"_"+str(idx)         
         grid_point_netlist.genGridSpiceNL(idx_str)
    
    database = db.coptDB(cell_name+'_DB',cell_name)
    
    if (num_params==2) :
      print("INFO: creating plot arrays")
      database.p2D.create_npArrays(pts_per_par)
    
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
                database.p2D.dump() 
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
                
    database.database.p2D.dump()   

run('INV1', int(sys.argv[1])) # arg1 = queue length, arg2 = grid points per param (same for all)

