.PARAM 
+ maj_inv_n=200e-9
+ maj_inv_p=200e-9
+ maj_pdn_a_1=200e-9
+ maj_pdn_a_2=200e-9
+ maj_pdn_b_1=200e-9
+ maj_pdn_b_2=200e-9
+ maj_pdn_c_1=200e-9
+ maj_pdn_c_2=200e-9
+ maj_pun_a_1=200e-9
+ maj_pun_a_2=200e-9
+ maj_pun_b_1=200e-9
+ maj_pun_b_2=200e-9
+ maj_pun_c_1=200e-9
+ maj_pun_c_2=200e-9



************************************************************************
* Library Name: BalancedLibrary
* Cell Name:    MAJ3
* View Name:    schematic
************************************************************************

.SUBCKT MAJ3 A B C GND OUT VDD
*.PININFO A:I B:I C:I OUT:O GND:B VDD:B
MM13 OUT   net9 GND   GND nch l=60n w=maj_inv_n   m=1
MM5  net27 C    GND   GND nch l=60n w=maj_pdn_c_2 m=1
MM4  net9  B    net27 GND nch l=60n w=maj_pdn_b_1 m=1
MM3  net9  A    net28 GND nch l=60n w=maj_pdn_a_2 m=1
MM2  net28 C    GND   GND nch l=60n w=maj_pdn_c_1 m=1
MM1  net9  A    net29 GND nch l=60n w=maj_pdn_a_1 m=1
MM0  net29 B    GND   GND nch l=60n w=maj_pdn_b_2 m=1
MM12 OUT   net9 VDD   VDD pch l=60n w=maj_inv_p   m=1
MM11 net9  C    net26 VDD pch l=60n w=maj_pun_c_2 m=1
MM10 net26 C    net25 VDD pch l=60n w=maj_pun_c_1 m=1
MM9  net25 B    VDD   VDD pch l=60n w=maj_pun_b_1 m=1
MM8  net25 A    VDD   VDD pch l=60n w=maj_pun_a_1 m=1
MM7  net26 A    net25 VDD pch l=60n w=maj_pun_a_2 m=1
MM6  net9  B    net26 VDD pch l=60n w=maj_pun_b_2 m=1
.ENDS

