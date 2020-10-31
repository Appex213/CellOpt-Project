# File: template.tcl

#####################################################
#     Define Library Conditions                     #
#####################################################
set_var slew_lower_rise 0.1
set_var slew_lower_fall 0.1
set_var slew_upper_rise 0.9
set_var slew_upper_fall 0.9
 
set_var delay_inp_rise 0.5
set_var delay_inp_fall 0.5
set_var delay_out_rise 0.5
set_var delay_out_fall 0.5
 
set_var max_transition 6.939e-10
set_var min_transition 6.5e-12
set_var min_output_cap 5.3e-16
 
#####################################################
#     Define Characterization Templates             #
#####################################################

define_template -type delay \
	-index_1 {0.0065 0.0175 0.0393 0.0829 0.170 0.3448 0.6939 } \
	-index_2 {0.0014 0.00513 0.0125 0.0275 0.0573 0.117 0.236 } \
        delay_template_7x7_3
 
define_template -type power \
	-index_1 {0.0065 0.0175 0.0393 0.0829 0.170 0.3448 0.6939 } \
	-index_2 {0.0014 0.00513 0.0125 0.0275 0.0573 0.117 0.236 } \
        power_template_7x7_3
 
#####################################################
#     Define Cells                                      #
#####################################################
define_cell \
       -input { A B CIN } \
       -output { SUM COUT } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { A B CIN SUM COUT } \
       FA
       
define_cell \
       -input { IN1 IN2 IN3 } \
       -output { OUT } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { IN1 IN2 IN3 OUT } \
       XOR3


define_cell \
       -input { A B C } \
       -output { OUT } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { A B C OUT } \
       MAJ3

      
define_cell \
       -input { IN } \
       -output { OUT } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { IN OUT } \
       INV1
       

define_cell \
       -input { A } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { A } \
       DLY_CAP_x1
       
       
define_cell \
       -input { A } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { A } \
       DLY_CAP_X2
       
define_cell \
       -input { A } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { A } \
       DLY_CAP_X4
       
define_cell \
       -input { A } \
       -delay delay_template_7x7_3 \
       -power power_template_7x7_3 \
       -pinlist { A } \
       DLY_CAP_X8
       

       
       
