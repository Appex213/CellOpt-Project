
#####################################################
#     Capture command line arguments                #
#####################################################

set sp_file_name_no_ext  [lindex $argv 0]
set sp_file_name ${sp_file_name_no_ext}.sp
set cell_lib_name [lindex $argv 1]
set threads 4
set char_corner [lindex $argv 2]

#####################################################
#     Set up variables for characterization         #
#####################################################

if {$char_corner == "tt"} {
    set supply_voltage 1.2
    set temperature 25
    set corner_name tt_1p2V_25C
} elseif {$char_corner == "ss"} {
    set supply_voltage 1.08
    set temperature 125
    set corner_name ss_1p08V_125C
} else {
    puts "Corner argument missing or unknown, check launch_char_cell.sh..."
    exit
}

set ground_voltage 0
set cells ${sp_file_name}


#####################################################
#     Set up Technology                             #
#####################################################

if {$char_corner == "tt"} {
    set model_file $::env(UTILDIR)/extsim_include_tt.scs
} elseif {$char_corner == "ss"} {
    set model_file $::env(UTILDIR)/extsim_include_ss.scs
} else {
    puts "Corner argument missing or unknown, check launch_char_cell.sh..."
    exit
}
read_spice -format spectre $model_file
set_var extsim_model_include $model_file

define_leafcell \
	-extsim_model \
	-element \
	-type pmos \
	-pin_position { 0 1 2 3 } \
	pch
define_leafcell \
	-extsim_model \
	-element \
	-type nmos \
	-pin_position { 0 1 2 3 } \
	nch

#read cell spice
read_spice ${cells}

#####################################################
#     Set up Characterization                       #
#####################################################
# Operating Conditions
set_operating_condition -voltage $supply_voltage -temp $temperature \
                  -name ${corner_name}
# Supply voltages
set_vdd -type primary VDD $supply_voltage
set_gnd -ignore_power -type primary GND $ground_voltage

# Read in Cell/Library Templates
source $::env(UTILDIR)/template.tcl

# Always separate conditional timing arcs
set_var conditional_expression separate
set_var force_condition 2
 
#####################################################
#     Characterize Library                          #
#####################################################
char_library -thread $threads -cells ${cell_lib_name} -extsim spectre
#####################################################
#     Export Results                                #
#####################################################
set full_lib_name ${cell_lib_name}
set datasheet_file_name ${sp_file_name_no_ext}_datasheet.txt
write_datasheet -conditional -format text \
       -filename ${datasheet_file_name} ${full_lib_name}
write_library -overwrite -derive_max_capacitance -precision "%.4g" ${sp_file_name_no_ext}.lib
write_verilog -no_err_primitives -timescale "1ns/1ps" ${sp_file_name_no_ext}.v
exec cp ${datasheet_file_name} $::env(ROOTDIR)/workspace/output/
