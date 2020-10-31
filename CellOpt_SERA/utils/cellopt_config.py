
import cellopt_util

def defineOptParams(cou):

    cou.setMasterFileName("c_element.cir")

    #          param name               min       max

    cou.defOptPar("nw", 120e-9, 400e-9)
    cou.defOptPar("pw", 120e-9, 400e-9)
