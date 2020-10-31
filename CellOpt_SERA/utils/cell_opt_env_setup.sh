#!/bin/tcsh
# find the absolute path to this script
set called=($_)
if ( "$called" != "" ) then  ### called by source 
   set script_fn=`readlink -f $called[2]`
else                         ### called by direct excution of the script
   set script_fn=`readlink -f $0`
endif
echo "Executing $script_fn"

# find referred cell_opt installation absolute path
set script_dir=`dirname $script_fn`
set ORGPATH=`pwd`
cd $script_dir
cd ..
setenv CELL_OPT_ROOT_DIR `pwd`
cd $ORGPATH
echo "CELL_OPT_ROOT_DIR=$CELL_OPT_ROOT_DIR"

module load LIBERATE
