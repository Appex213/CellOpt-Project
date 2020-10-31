#!/bin/bash

if [ -d $CELL_OPT_ROOT_DIR/workspace/runspace ] 
then 
\rm -r $CELL_OPT_ROOT_DIR/workspace/runspace
mkdir  $CELL_OPT_ROOT_DIR/workspace/runspace
fi



if [ -d $CELL_OPT_ROOT_DIR/workspace/output ] 
then 
\rm -r $CELL_OPT_ROOT_DIR/workspace/output
mkdir  $CELL_OPT_ROOT_DIR/workspace/output
fi


if [ -d $CELL_OPT_ROOT_DIR/workspace/launch_logs ] 
then 
\rm -r $CELL_OPT_ROOT_DIR/workspace/launch_logs
mkdir  $CELL_OPT_ROOT_DIR/workspace/launch_logs
fi


if [ -d $CELL_OPT_ROOT_DIR/workspace/algorithm_logs ] 
then 
\rm -r $CELL_OPT_ROOT_DIR/workspace/algorithm_logs
mkdir  $CELL_OPT_ROOT_DIR/workspace/algorithm_logs
fi
