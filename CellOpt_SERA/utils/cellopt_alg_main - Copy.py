import sys
import os
import shutil
import time
import datetime
import csv
import math
from multiprocessing import Pool
from collections import OrderedDict
import errno

import cellopt_parser as parser
import cellopt_util
import cellopt_config as conf
import cellopt_sera as sera

sys.path.append(os.environ["CELL_OPT_ROOT_DIR"] + "/local_utils")
cou = cellopt_util.celloptUtil()
conf.defineOptParams(cou)

LOGS = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/algorithm_logs"
INPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/pending"
OUTPUT = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/output"
RUNSPACE = os.environ["CELL_OPT_ROOT_DIR"] + "/workspace/runspace"
OPT_IN = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_in"
OPT_OUT = os.environ["CELL_OPT_ROOT_DIR"] + "/opt_out"

mode = sys.argv[2]
if mode == 'sera':
    FILE_EXT = '.cir'
else:
    FILE_EXT = '.sp'

MOD_OFFSET = 0.1
TARGET_GAP_DIFF_PER_STEP = 0.2


def suspend():
    input("Program suspended, press any key to resume...")


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


def update_attr(object, attribute, value):
    setattr(object, attribute, value)
    info("Attribute " + attribute + "was modified to " + value)


class OptAlgorithm:
    def __init__(self, runid, original_cell_name, score=100000):
        self.runid = runid
        self.master_cell = original_cell_name.split('__')[0]
        self.original_cell_name = original_cell_name
        self.original_score = score
        self.best_score = score
        self.best_score_id = original_cell_name
        self.param_dict = parser.get_sp_params(
            OPT_IN + '/' + runid + '/' + original_cell_name + FILE_EXT)
        self.noparam_netlist = get_noparam_netlist(
            OPT_IN + '/' + runid + '/' + original_cell_name + FILE_EXT)
        self.descend_iteration = 0
        self.param_iteration = 1
        self.current_param = ''
        self.global_start_time = time.time()
        self.timedout_counter = 0
        self.params_offset_dic = OrderedDict()
        self.init_param_offset()

    def generate_mod_netlist(self, mod_param, mod, direction):
        file_name = self.original_cell_name + '_' + \
            str(self.descend_iteration) + '_' + str(self.param_iteration)
        if direction == "POS":
            file_name = file_name + '_POS'
        elif direction == "NEG":
            file_name = file_name + '_NEG'
        else:
            file_name = file_name + '_NTRL'
        mod_netlist = open(INPUT + '/' + file_name + FILE_EXT, 'w')
        mod_netlist.write(".PARAM \n")
        for param in self.param_dict:
            if param == mod_param:
                line = '+ ' + param + '=' + \
                    str(self.param_dict[param] + mod)
            else:
                line = '+ ' + param + '=' + str(self.param_dict[param])
            mod_netlist.write(line + ' \n')
        mod_netlist.write('\n')
        mod_netlist.write(self.noparam_netlist)
        mod_netlist.close()
        return file_name

    def generate_sera_netlist(self, mod_param, mod, direction):
        dir_name = self.original_cell_name + '_' + \
            str(self.descend_iteration) + '_' + str(self.param_iteration)
        if direction == "POS":
            dir_name = dir_name + '_POS'
        elif direction == "NEG":
            dir_name = dir_name + '_NEG'
        else:
            dir_name = dir_name + '_NTRL'
        path = os.path.join(RUNSPACE, dir_name)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        sera_obj = SeraParams()
        sera_obj.dir = dir_name
        mod_netlist = open(os.path.join(path, self.master_cell + '_sera_template' + FILE_EXT), 'w')
        mod_netlist.write("simulator lang = spice\n")
        mod_netlist.write(".PARAM \n")
        for param in self.param_dict:
            if param == mod_param:
                line = '+ ' + param + '=' + \
                    str(self.param_dict[param] + mod)
                sera_obj.param_dict[param] = self.param_dict[param] + mod
            else:
                line = '+ ' + param + '=' + str(self.param_dict[param])
                sera_obj.param_dict[param] = self.param_dict[param]
            mod_netlist.write(line + ' \n')

        mod_netlist.write('\n')
        mod_netlist.write(self.noparam_netlist)
        mod_netlist.close()
        return sera_obj

    def status(self):
        info("Current status: ")
        t = time.time() - self.global_start_time
        print("  Runtime:         = " + str(datetime.timedelta(seconds=round(t))))
        print("  Global iteration = " + str(self.descend_iteration))
        print("  Local iteration  = " + str(self.param_iteration))
        print("  Current param    = " + self.current_param)
        print("  Best score         = " + str(self.best_score))
        print("  Best score ID      = " + self.best_score_id)
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

    def init_param_offset(self):
        for param in cou.parsDict:
            min = cou.parsDict[param].min
            max = cou.parsDict[param].max
            param_offset = (max - min) * MOD_OFFSET
            self.params_offset_dic[param] = param_offset
            print("Updated offset of param %s to %e" % (param, param_offset))

    # def update_param_offset(self, param, score_diff, direction):
    #     prev_param_offset = self.params_offset_dic[param]
    #     new_param_offset = ((TARGET_GAP_DIFF_PER_STEP / score_diff) * (1 + prev_param_offset)) - 1
    #     self.params_offset_dic[param] = new_param_offset
    #     print(
    #         "Updated offset of param %s from %f to %f due to score_diff =%f" %
    #         (param, prev_param_offset, new_param_offset, score_diff))

    def update_param_offset(self, param):
        self.params_offset_dic[param] = self.params_offset_dic[param] / 2
        print("Updated offset of param %s from %f to %f" %
              (param, self.params_offset_dic[param], self.params_offset_dic[param] / 2))

    def ext_update_params(self, update_file_path):
        with open(update_file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.param_dict[row[0]] = row[1]    # Update param


class SeraParams:
    def __init__(self):
        self.dir = ''
        self.qp = 12
        self.qn = 12
        self.param_dict = {}
        self.score = 10 ** 10
        self.q_range = [10, 30]


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


def run_opt_sera(runid, original_cell_name):
    algorithm = OptAlgorithm(runid, original_cell_name)
    info("Item " + original_cell_name + " has started, tail logfile to see progress.")
    info("Opt Mode: SERA Minimization")

    # Redirect output from main stdout to logfile
    # sys.stdout = open(LOGS + '/' + algorithm.original_cell_name + '.log', 'w')
    stop_flag = False
    while not stop_flag:
        algorithm.param_iteration = 1
        current_score = algorithm.best_score
        for param in algorithm.param_dict:
            algorithm.current_param = param
            algorithm.status()
            sys.stdout.flush()

            offset = algorithm.param_dict[param] * MOD_OFFSET

            # Generate modified netlists
            args = []
            args.append(algorithm.generate_sera_netlist(param, offset, "POS"))
            args.append(algorithm.generate_sera_netlist(param, -offset, "NEG"))

            sub_process_pool = Pool(len(args))
            returned_obj_list = sub_process_pool.map(sera.get_sera_score, args)

            for item in returned_obj_list:
                if item.score < algorithm.best_score:
                    algorithm.best_score = item.score
                    algorithm.best_score_id = item.dir
                    for param in item.param_dict:
                        if algorithm.param_dict[param] != item.param_dict[param]:
                            debug("Param " + param + " was modified to " + str(item.param_dict[param]) + " from " + str(algorithm.param_dict[param]))
                            algorithm.param_dict[param] = item.param_dict[param]

            algorithm.param_iteration += 1
        if algorithm.best_score == current_score:
            stop_flag = True
        algorithm.descend_iteration += 1


def run_opt_ext(runid, original_cell_name, original_score):
    algorithm = OptAlgorithm(runid, original_cell_name, float(original_score))
    info("Item " + original_cell_name + " has started, tail logfile to see progress.")
    info("Opt Mode: External")

    # Redirect output from main stdout to logfile
    # sys.stdout = open(LOGS + '/' + algorithm.original_cell_name + '.log', 'w')

    while True:
        path = os.path.join(RUNSPACE,
                            'ext_' + str(algorithm.descend_iteration) + '.csv')
        with open(path, 'w', buffering=0) as file:
            writer = csv.writer(file, delimiter=',')
            csv_row = ['param name', 'pos', 'ntrl', 'neg']     # Header
            writer.writerow(csv_row)

            for param in algorithm.param_dict:
                algorithm.current_param = param
                csv_row = [param]
                algorithm.status()
                sys.stdout.flush()

                mod_pos = algorithm.param_dict[param] * MOD_OFFSET
                mod_neg = -1 * algorithm.param_dict[param] * MOD_OFFSET

                # Generate modified netlists
                mod_positive = algorithm.generate_mod_netlist(
                    param, mod_pos, "POS")
                mod_negative = algorithm.generate_mod_netlist(
                    param, mod_neg, "NEG")
                mod_neutral = algorithm.generate_mod_netlist(param, 0, "NTRL")

                # Datasheet paths
                path_pos = os.path.join(
                    RUNSPACE, mod_positive, mod_positive + "_datasheet.txt")
                path_neg = os.path.join(
                    RUNSPACE, mod_negative, mod_negative + "_datasheet.txt")
                path_ntrl = os.path.join(
                    RUNSPACE, mod_neutral, mod_neutral + "_datasheet.txt")

                algorithm.liberate(mod_positive)
                time.sleep(0.25)
                algorithm.liberate(mod_negative)
                time.sleep(0.25)
                algorithm.liberate(mod_neutral)
                start_time = time.time()

                # timed_out = False
                wait_for_completion = True
                while wait_for_completion:
                    time.sleep(5)
                    status_pos = os.path.exists(path_pos)
                    status_neg = os.path.exists(path_neg)
                    status_ntrl = os.path.exists(path_ntrl)
                    debug('status check:')
                    debug("\t\tpos: " + str(status_pos) + " | neg: " + str(status_neg) + " | ntrl: " + str(status_ntrl))
                    if status_pos and status_neg and status_ntrl:
                        wait_for_completion = False
                        time.sleep(1)       # Avoid read/write race?
                    elif (time.time() - start_time) > 200:      # timeout condition
                        wait_for_completion = False
                        # timed_out = True

                if status_pos:
                    gap_pos = parser.get_gap(path_pos)
                    csv_row.append(str(gap_pos))
                else:
                    csv_row.append('NaN')

                if status_ntrl:
                    gap_ntrl = parser.get_gap(path_ntrl)
                    csv_row.append(str(gap_ntrl))
                else:
                    csv_row.append('NaN')

                if status_neg:
                    gap_neg = parser.get_gap(path_neg)
                    csv_row.append(str(gap_neg))
                else:
                    csv_row.append('NaN')

                writer.writerow(csv_row)
                algorithm.param_iteration += 1
        algorithm.descend_iteration += 1
        suspend()


def run_opt_algorithm(runid, original_cell_name, original_gap):
    algorithm = OptAlgorithm(runid, original_cell_name, float(original_gap))
    info("Item " + original_cell_name + " has started, tail logfile to see progress.")
    info("Opt Mode: Internal")

    # Redirect output from main stdout to logfile
    sys.stdout = open(LOGS + '/' + algorithm.original_cell_name + '.log', 'w')

    fine_tune_factor = 0.5
    # when there is no improvmenrt scale down offset by fine_tune_factor for
    # fine_tune_iterations
    fine_tune_iterations = 10
    fine_tune_itr_cnt = 0
    is_better = True

    while fine_tune_itr_cnt < fine_tune_iterations:

        if not is_better:
            fine_tune_itr_cnt += 1
            print(
                "INFO: Upon non-improvmed descend iteration , reducing offsets and entering fine tune iteration %d" %
                fine_tune_itr_cnt)
            for param in algorithm.params_offset_dic:
                param_offset = algorithm.params_offset_dic[param]
                param_new_offset = param_offset / 2
                algorithm.params_offset_dic[param] = param_new_offset
                print("Updated offset of param %s from %e to %e" %
                      (param, param_offset, param_new_offset))

        is_better = True
        while is_better:

            algorithm.param_iteration = 1
            is_better = False

            # print ("TMP_DBG XYZ")
            for param in algorithm.param_dict:
                algorithm.current_param = param
                algorithm.status()
                sys.stdout.flush()

                if param not in algorithm.params_offset_dic:
                    print(
                        "Missing offset info for param %s , quitting" %
                        param)
                    exit()

                mod_pos = algorithm.params_offset_dic[param]
                mod_neg = algorithm.params_offset_dic[param]

                mod_positive = algorithm.generate_mod_netlist(
                    param, mod_pos, "POS")
                mod_negative = algorithm.generate_mod_netlist(
                    param, -1 * mod_neg, "NEG")

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
                        warning("Liberate run " + mod_negative + " timed out and will be ignored, check Liberate logs in runspace folder.")
                        # os.stat(RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                        algorithm.timedout_counter += 1
                        gap_pos = parser.get_gap(
                            RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                        debug("gap_pos = " + str(gap_pos))
                        if gap_pos < algorithm.best_gap:
                            debug("Param " + param + " was modified to " + str(algorithm.param_dict[param] + mod_pos) + " from " + str(algorithm.param_dict[param]))
                            algorithm.param_dict[param] = algorithm.param_dict[param] + mod_pos
                            # algorithm.update_param_offset(param,score_diff=algorithm.best_score-score_pos , direction="POS")
                            algorithm.best_score = gap_pos
                            algorithm.best_score_id = mod_positive

                            is_better = True

                    elif status_neg:     # =Status_pos timed out
                        warning("Liberate run " + mod_positive + " timed out and will be ignored, check Liberate logs in runspace folder.")
                        # os.stat(RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                        algorithm.timedout_counter += 1
                        gap_neg = parser.get_gap(
                            RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                        debug("gap_neg = " + str(gap_neg))
                        if gap_neg < algorithm.best_score:
                            info("Param " + param + " was modified to " + str(algorithm.param_dict[param] - mod_neg) + " from " + str(algorithm.param_dict[param]))
                            algorithm.param_dict[param] = algorithm.param_dict[param] - mod_neg
                            # algorithm.update_param_offset(param,score_diff=algorithm.best_score-gap_neg , direction="NEG")
                            algorithm.best_score = gap_neg
                            algorithm.best_score_id = mod_negative
                            is_better = True

                    else:
                        warning("Liberate runs " + mod_positive + " and " + mod_negative + " timed out and will be ignored, check Liberate logs in runspace folder.")
                        # os.stat(RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                        # os.stat(RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                        algorithm.timedout_counter += 2
                else:
                    gap_pos = parser.get_gap(RUNSPACE + "/" + mod_positive + "/" + mod_positive + "_datasheet.txt")
                    gap_neg = parser.get_gap(RUNSPACE + "/" + mod_negative + "/" + mod_negative + "_datasheet.txt")
                    debug("gap_pos = " + str(gap_pos))
                    debug("gap_neg = " + str(gap_neg))
                    if gap_pos < algorithm.best_score:
                        debug("Param " + param + " was modified to " + str(algorithm.param_dict[param] + mod_pos) + " from " + str(algorithm.param_dict[param]))
                        algorithm.param_dict[param] = algorithm.param_dict[param] + mod_pos
                        # algorithm.update_param_offset(param,score_diff=algorithm.best_score-gap_pos , direction="POS")
                        algorithm.best_score = gap_pos
                        algorithm.best_score_id = mod_positive
                        is_better = True
                    if gap_neg < algorithm.best_score:
                        debug("Param " + param + " was modified to " + str(algorithm.param_dict[param] - mod_neg) + " from " + str(algorithm.param_dict[param]))
                        algorithm.param_dict[param] = algorithm.param_dict[param] - mod_neg
                        # algorithm.update_param_offset(param,score_diff=algorithm.best_score-gap_neg , direction="NEG")
                        algorithm.best_score = gap_neg
                        algorithm.best_score_id = mod_negative
                        is_better = True
                info("Iteration time: " + str(datetime.timedelta(seconds=round(time.time() - start_time))))
                # Increment local iteration
                algorithm.param_iteration = algorithm.param_iteration + 1
            # Delete residual liberate junk
            for folder in os.listdir(RUNSPACE):
                for file in os.listdir(os.path.join(RUNSPACE, folder)):
                    if file.startswith('altos'):
                        os.remove(os.path.join(RUNSPACE, folder, file))
            # Increment global iteration
            algorithm.descend_iteration = algorithm.descend_iteration + 1

    info("No improvement was decected in the last global iteration, moving final netlist to opt in folder;")
    # Copy netlist to opt_out
    src_path = RUNSPACE + '/' + algorithm.best_score_id + \
        '/' + algorithm.best_score_id + FILE_EXT
    dst_path = OPT_OUT + '/' + runid + '/' + \
        algorithm.master_cell + '__' + str(algorithm.best_score) + FILE_EXT
    shutil.copy2(src_path, dst_path)
    # Copy datasheet to opt_put/datasheets
    src_path = RUNSPACE + '/' + algorithm.best_score_id + \
        '/' + algorithm.best_score_id + '_datasheet.txt'
    dst_path = OPT_OUT + '/' + runid + '/datasheets/' + \
        algorithm.master_cell + '__' + \
        str(algorithm.best_score) + '_datasheet.txt'
    shutil.copy2(src_path, dst_path)

    algorithm.param_iteration = algorithm.param_iteration - 1
    # algorithm.descend_iteration = algorithm.descend_iteration - 1
    algorithm.status()

    sys.stdout = sys.__stdout__     # Redirect output back to system stdout
    info('item ' + algorithm.original_cell_name + ' is done, see log file for details.')
    debug('Total runtime: ' + str(datetime.timedelta(seconds=round(time.time() - algorithm.global_start_time))))


if mode == 'int':
    run_opt_algorithm('test', sys.argv[1], sys.argv[1].split('__')[1])
elif mode == 'ext':
    run_opt_ext('test', sys.argv[1], sys.argv[1].split('__')[1])
elif mode == 'sera':
    run_opt_sera('test', sys.argv[1])
# opt_start('FA')
