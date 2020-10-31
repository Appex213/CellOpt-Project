#!/bin/bash
 
# $1 - input spice netlist file name  without path and without the '.sp' extension
# $2 - Cell name to characterizer within the spice netlist

# echo "TMP DBG P1=$1 P2=$2"

# Create Liberate run space for this specific cell

# first delete if leftover exist 
export ROOTDIR=$CELL_OPT_ROOT_DIR
export RUNDIR=$CELL_OPT_ROOT_DIR/workspace/runspace/$1
export UTILDIR=$CELL_OPT_ROOT_DIR/utils

if [ -d "$RUNDIR" ] 
then
\rm -r $RUNDIR
fi

echo "RUNDIR = $RUNDIR"

mkdir $RUNDIR

# move the spice input file to the run directory
mv $CELL_OPT_ROOT_DIR/workspace/pending/$1.sp  $RUNDIR/
#go to run directory
cd $RUNDIR

# submit (qrun equivalent)
qrsh -V -cwd -now no  liberate  $CELL_OPT_ROOT_DIR/utils/char_cell.tcl $1 $2 $3 > $1_liberate.log 2>&1  &

echo "INFO launch_char_cel.sh submitted following job (qrun equivalent)"
echo  "qrsh -V -cwd  liberate  $CELL_OPT_ROOT_DIR/utils/char_cell.tcl $1.sp $2 $3>&1  $1_liberate.log &"

