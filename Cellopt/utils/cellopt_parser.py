import tokenize_string as tok
import time
import statistics as st
from collections import OrderedDict


class DelayLine:
    def __init__(self, cell, timing_arc, min, mid, max):
        self.cell = cell
        self.timing_arc = timing_arc
        self.min = min
        self.mid = mid
        self.max = max


def parse_result(res_file):
    res = open(res_file, 'r')
    res_list = []

    at_delay = False
    at_line = False

    for line in res:
        line_tokens = tok.tokenizeString(line, ["\t", " ", "=", "\n", "+"])
        counter = 0
        skip = False

        if 'Power' in line_tokens:
            at_delay = False
        elif 'Delay' in line_tokens:
            at_delay = True

        if at_delay:
            for token in line_tokens:
                if at_delay and token == 'max':
                    at_line = True
                    skip = True
                elif at_line and token == '|' and not skip:
                    counter += 1
                elif at_line and token != ' ' and counter in range(1, 6):
                    if counter == 1:
                        res_list.append(DelayLine(token, '', 0, 0, 0))
                    elif counter == 2:
                        res_list[-1].timing_arc = token
                    elif counter == 3:
                        res_list[-1].min = token
                    elif counter == 4:
                        res_list[-1].mid = token
                    elif counter == 5:
                        res_list[-1].max = token
                        counter = 0
                        skip = True
                elif at_line and line is '\n':
                    at_line = False

    res.close()
    return res_list


# def get_gap(res_file,gap_type):
def get_gap(res_file):
    delay_list = []
    counter = 0
    while delay_list == []:
        counter += 1
        res_list = parse_result(res_file)
        for delay in res_list:
            delay_list.append(float(delay.mid))
        if counter > 1:
            time.sleep(1)
        if counter == 20:
            print("WARNING: file " + res_file + " returned empty delay list")
            print(res_list)
            return 10**10
    #if gap_type == "STDEV" :
    #   gap = round(st.stdev(delay_list), 6)
    #else :
    try :    
      gap = round(max(delay_list) - min(delay_list), 6)
      return gap
    except:   
      return 10**10
    


def get_sp_params(path):
    src = open(path, 'r')
    param_dict = OrderedDict()
    at_params = False
    is_param_value = False

    for line in src:
        line_tokens = tok.tokenizeString(line, ["\t", " ", "=", "\n"])

        if at_params and line is '\n':
            return param_dict

        if at_params:
            name = value = ''
            for token in line_tokens:
                if token != '+' and token != ' ' and name is '':
                    name = token
                    is_param_value = True
                elif is_param_value and token != '=' and value is '':
                    value = token
                    is_param_value = False
            param_dict[name] = float(value)

        elif '.PARAM' in line_tokens:
            at_params = True


# get_sp_params('C:/Users/Matan/OneDrive - Bar-Ilan University/EnICS/Python_WP_research/py_parser/XOR2_PASSGATE.sp')
# delays = res_parser("XOR2.txt")
# print(f"Delays: {[str(entry) for entry in delays]}")
