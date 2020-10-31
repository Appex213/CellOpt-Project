#!/bin/bash
 
# $1 - input spice netlist file name  without path and without the '.sp' extension

# --timeout reset--

export ROOTDIR=$CELL_OPT_ROOT_DIR
export RUNDIR=$CELL_OPT_ROOT_DIR/workspace/runspace/$1
export UTILDIR=$CELL_OPT_ROOT_DIR/utils

# move .sp netlist back to pending folder
mv $RUNDIR/$1.sp  $CELL_OPT_ROOT_DIR/workspace/pending/$1.sp

