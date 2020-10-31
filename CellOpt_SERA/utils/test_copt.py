
import cellopt_util as util
import cellopt_config as conf

par=""

cou = util.celloptUtil()
conf.defineOptParams(cou)
cou.genParamsRandom()
cou.genSpiceNL()

