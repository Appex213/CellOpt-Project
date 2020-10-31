import sys
import os
import shutil
import time
import datetime
import csv
import math
from multiprocessing import Pool
from collections import OrderedDict

import cellopt_parser as parser

LOGS = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/algorithm_logs"
INPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/pending"
OUTPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/output"
RUNSPACE = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/runspace"
OPT_IN = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_in"
OPT_OUT = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_out"

MOD_OFFSET = 0.01
MOD_POS = 1 + MOD_OFFSET
MOD_NEG = 1 - MOD_OFFSET

INIT_POINTS = 1 # 20


def system_call(cmd_str):
    status = os.system(cmd_str)
    if status != 0:
        print("ERROR @ launcher.py : System Call Error on : " + cmd_str)
        exit()


def debug(msg):
    print(get_date() + " DEBUG: " + msg)


def info(msg):
    print(get_date() + " INFO: " + msg)


def warning(msg):
    print(get_date() + " WARNING: " + msg)


def get_date():
    return '[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']'


class OptAlgorithm:
    def __init__(self, runid, original_cell_name, gap=100000):
        self.runid = runid
        self.master_cell = original_cell_name.split('__')[0]
        self.original_cell_name = original_cell_name
        self.original_gap = gap
        self.best_gap = gap
        self.best_gap_id = original_cell_name
        self.param_dict = parser.get_sp_params(
            OPT_IN + '/' + runid + '/' + original_cell_name + '.sp')
        self.noparam_netlist = get_noparam_netlist(
            OPT_IN + '/' + runid + '/' + original_cell_name + '.sp')
        self.global_iteration = 1
        self.local_iteration = 1
        self.current_param = ''
        self.global_start_time = time.time()
        self.timedout_counter = 0

    def generate_mod_netlist(self, mod_param, modifier):
        file_name = self.original_cell_name + '_' + \
            str(self.global_iteration) + '_' + str(self.local_iteration)
        if modifier == MOD_POS:
            file_name = file_name + '_POS'
        else:
            file_name = file_name + '_NEG'
        mod_netlist = open(INPUT + '/' + file_name + '.sp', 'w')
        mod_netlist.write(".PARAM \n")
        for param in self.param_dict:
            if param == mod_param:
                line = '+ ' + param + '=' + \
                    str(self.param_dict[param] * modifier)
            else:
                line = '+ ' + param + '=' + str(self.param_dict[param])
            mod_netlist.write(line + ' \n')
        mod_netlist.write('\n')
        mod_netlist.write(self.noparam_netlist)
        mod_netlist.close()
        return file_name

    def status(self):
        info("Current status: ")
        t = time.time() - self.global_start_time
        print("  Runtime:         = " + str(datetime.timedelta(seconds=round(t))))
        print("  Global iteration = " + str(self.global_iteration))
        print("  Local iteration  = " + str(self.local_iteration))
        print("  Current param    = " + self.current_param)
        print("  Best gap         = " + str(self.best_gap))
        print("  Best gap ID      = " + self.best_gap_id)
        print("  Timed out        = " + str(self.timedout_counter))
        print("  Param list: ")
        for param in self.param_dict:
            print("    " + param + " = " + str(self.param_dict[param]))

    def liberate(self, cell):
        cmd_str = "$CELL_OPT_ROOT_DIR/utils/launch_char_cell.sh " + \
            cell + ' ' + self.master_cell
        redirect_launch_log_str = " > $CELL_OPT_ROOT_DIR/workspace/launch_logs/" + cell + ".log"
        launch_command = cmd_str + redirect_launch_log_str
        system_call(launch_command)
        info("cellopt_algorithm.py issued following system call:")
        print(launch_command)


def get_noparam_netlist(src_file):
    src = open(src_file, 'r')
    noparam_netlist = ''
    read = params = False
    for line in src:
        if '.PARAM' in line:
            params = True
        if params and line == '\n':
            read = True
        if read:
            noparam_netlist = noparam_netlist + line
    src.close()
    return noparam_netlist


def run_opt_algorithm(runid, original_cell_name, original_gap):
    algorithm = OptAlgorithm(runid, original_cell_name, float(original_gap))
    info("Item " + original_cell_name +
         " has started, tail logfile to see progress.")

    # Redirect output from main stdout to logfile
    sys.stdout = open(LOGS + '/' + algorithm.original_cell_name + '.log', 'w')

    is_better = True
    while is_better:
        algorithm.local_iteration = 1
        is_better = False
        for param in algorithm.param_dict:
            algorithm.current_param = param
            algorithm.status()
            sys.stdout.flush()

            mod_positive = algorithm.generate_mod_netlist(param, MOD_POS)
            mod_negative = algorithm.generate_mod_netlist(param, MOD_NEG)
            algorithm.liberate(mod_positive)
            time.sleep(0.25)
            algorithm.liberate(mod_negative)
            start_time = time.time()

            timed_out = False
            wait_for_completion = True
            while wait_for_completion:
                time.sleep(1)
                # status_pos = os.path.exists(OUTPUT + "/" + mod_positive + "_datasheet.txt")
                status_pos = os.path.exists(
                    RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                # status_neg = os.path.exists(OUTPUT + "/" + mod_negative + "_datasheet.txt")
                status_neg = os.path.exists(
                    RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                if status_pos and status_neg:
                    wait_for_completion = False
                    time.sleep(1)       # Avoid read/write race?
                elif (time.time() - start_time) > 200:      # timeout condition
                    wait_for_completion = False
                    timed_out = True

            if timed_out:
                if status_pos:      # =Status_neg timed out
                    warning("Liberate run " + mod_negative +
                            " timed out and will be ignored, check Liberate logs in runspace folder.")
                    # os.stat(RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                    algorithm.timedout_counter += 1
                    gap_pos = parser.get_gap(
                        RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                    debug("gap_pos = " + str(gap_pos))
                    if gap_pos < algorithm.best_gap:
                        debug("Param " + param + " was modified to " + str(
                            algorithm.param_dict[param] * MOD_POS) + " from " + str(algorithm.param_dict[param]))
                        algorithm.param_dict[param] = algorithm.param_dict[param] * MOD_POS
                        algorithm.best_gap = gap_pos
                        algorithm.best_gap_id = mod_positive
                        is_better = True

                elif status_neg:     # =Status_pos timed out
                    warning("Liberate run " + mod_positive +
                            " timed out and will be ignored, check Liberate logs in runspace folder.")
                    # os.stat(RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                    algorithm.timedout_counter += 1
                    gap_neg = parser.get_gap(
                        RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                    debug("gap_neg = " + str(gap_neg))
                    if gap_neg < algorithm.best_gap:
                        info("Param " + param + " was modified to " + str(
                            algorithm.param_dict[param] * MOD_NEG) + " from " + str(algorithm.param_dict[param]))
                        algorithm.param_dict[param] = algorithm.param_dict[param] * (
                            MOD_NEG)
                        algorithm.best_gap = gap_neg
                        algorithm.best_gap_id = mod_negative
                        is_better = True

                else:
                    warning("Liberate runs " + mod_positive + " and " + mod_negative +
                            " timed out and will be ignored, check Liberate logs in runspace folder.")
                    # os.stat(RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                    # os.stat(RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                    algorithm.timedout_counter += 2
            else:
                gap_pos = parser.get_gap(
                    RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                gap_neg = parser.get_gap(
                    RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                debug("gap_pos = " + str(gap_pos))
                debug("gap_neg = " + str(gap_neg))
                if gap_pos < algorithm.best_gap:
                    debug("Param " + param + " was modified to " + str(
                        algorithm.param_dict[param] * MOD_POS) + " from " + str(algorithm.param_dict[param]))
                    algorithm.param_dict[param] = algorithm.param_dict[param] * MOD_POS
                    algorithm.best_gap = gap_pos
                    algorithm.best_gap_id = mod_positive
                    is_better = True
                if gap_neg < algorithm.best_gap:
                    debug("Param " + param + " was modified to " + str(
                        algorithm.param_dict[param] * MOD_NEG) + " from " + str(algorithm.param_dict[param]))
                    algorithm.param_dict[param] = algorithm.param_dict[param] * \
                        (MOD_NEG)
                    algorithm.best_gap = gap_neg
                    algorithm.best_gap_id = mod_negative
                    is_better = True
            info("Iteration time: " +
                 str(datetime.timedelta(seconds=round(time.time() - start_time))))
            # Increment local iteration
            algorithm.local_iteration = algorithm.local_iteration + 1
        # Delete residual liberate junk
        for folder in os.listdir(RUNSPACE):
            for file in os.listdir(os.path.join(RUNSPACE, folder)):
                if file.startswith('altos'):
                    os.remove(os.path.join(RUNSPACE, folder, file))
        # Increment global iteration
        algorithm.global_iteration = algorithm.global_iteration + 1

    info("No improvement was decected in the last global iteration, moving final netlist to opt in folder;")
    # Copy netlist to opt_out
    src_path = RUNSPACE + '/' + algorithm.best_gap_id + \
        '/' + algorithm.best_gap_id + '.sp'
    dst_path = OPT_OUT + '/' + runid + '/' + \
        algorithm.master_cell + '__' + str(algorithm.best_gap) + '.sp'
    shutil.copy2(src_path, dst_path)
    # Copy datasheet to opt_put/datasheets
    src_path = RUNSPACE + '/' + algorithm.best_gap_id + \
        '/' + algorithm.best_gap_id + '_datasheet.txt'
    dst_path = OPT_OUT + '/' + runid + '/datasheets/' + \
        algorithm.master_cell + '__' + \
        str(algorithm.best_gap) + '_datasheet.txt'
    shutil.copy2(src_path, dst_path)

    algorithm.local_iteration = algorithm.local_iteration - 1
    algorithm.global_iteration = algorithm.global_iteration - 1
    algorithm.status()

    sys.stdout = sys.__stdout__     # Redirect output back to system stdout
    info('item ' + algorithm.original_cell_name +
         ' is done, see log file for details.')
    debug('Total runtime: ' +
          str(datetime.timedelta(seconds=round(time.time() - algorithm.global_start_time))))


def euclid_dist(point_1, point_2):
    dist = 0
    for param in point_1:
        if param != 'result':
            dist = dist + (float(point_1[param]) - float(point_2[param]))**2
    return math.sqrt(dist)


def select_points(cell_name):
    db = {}  # OrderedDict()
    point_list = {}  # OrderedDict()
    with open(OPT_IN + '/' + cell_name + '_DB.csv', newline='') as csv_db:
        reader = csv.DictReader(csv_db)
        for row in reader:
            sorted_row = OrderedDict(
                sorted(row.items(), key=lambda item: reader.fieldnames.index(item[0])))
            db[row['caseID']] = sorted_row
            del db[row['caseID']]['caseID']

    not_enough_points = True
    threshold = 3
    while not_enough_points:
        for cell in db:
            if not point_list:      # = point_list is empty, first iteration.
                point_list[cell] = db[cell]
            else:
                point_too_close = False
                for point in point_list:
                    if euclid_dist(db[cell], db[point]) < threshold:
                        point_too_close = True
                if not point_too_close:
                    point_list[cell] = db[cell]
                if len(point_list) == INIT_POINTS:
                    break
        if len(point_list) >= INIT_POINTS:
            not_enough_points = False
        else:
            threshold = threshold - 0.5
            debug('not enough points, decreasing distance threshold to ' + str(threshold))

    return point_list


def opt_start(cell_name):
    system_call("$CELL_OPT_ROOT_DIR/utils/clean_workspace.sh")

    runid = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('OptAlgorithm started on ' + runid)
    os.mkdir(OPT_IN + '/' + runid)
    os.mkdir(OPT_OUT + '/' + runid)
    os.mkdir(OPT_OUT + '/' + runid + '/datasheets')

    points = select_points(cell_name)
    noparam_netlist = get_noparam_netlist(OPT_IN + '/' + cell_name + '.sp')
    argument_list = []

    for point in points:
        file_name = cell_name + '__' + points[point]['result']
        point_netlist = open(OPT_IN + '/' + runid +
                             '/' + file_name + '.sp', 'w')
        point_netlist.write(".PARAM \n")
        for param in points[point]:
            if param != 'result':
                line = '+ ' + param + '=' + str(points[point][param])
            point_netlist.write(line + ' \n')
        point_netlist.write('\n')
        point_netlist.write(noparam_netlist)
        point_netlist.close()
        info("Created netlist for " + point + " as " + file_name)

        argument_list.append((runid, file_name, file_name.split('__')[1]))

    time.sleep(5)       # Wait for write buffer to flush
    pool = Pool(4)
    pool.starmap(run_opt_algorithm, argument_list)

    shutil.copytree(LOGS, OPT_OUT + '/' + runid + '/logs')
    print("OptAlgorithm finished running on " +
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


run_opt_algorithm('test',sys.argv[1],sys.argv[1].split('__')[1])
# opt_start('FA')
