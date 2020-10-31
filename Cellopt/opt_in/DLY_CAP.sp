************************************************************************
* auCdl Netlist:
* 
* Library Name:  WaveProResearch
* Top Cell Name: DLY_CAP
* View Name:     schematic
* Netlisted on:  Apr  5 11:00:23 2020
************************************************************************

*.BIPOLAR
*.RESI = 2000 
*.RESVAL
*.CAPVAL
*.DIOPERI
*.DIOAREA
*.EQUATION
*.SCALE METER
.PARAM



************************************************************************
* Library Name: WaveProResearch
* Cell Name:    DLY_CAP
* View Name:    schematic
************************************************************************

.SUBCKT DLY_CAP A VDD VSS
*.PININFO A:I VDD:I VSS:I
MmXI0_MXNA1 VSS A VSS VSS nch_lvt l=60n w=495.00n m=1
MmXI0_MXPA1 VDD A VDD VDD pch_lvt l=60n w=585.00n m=1
.ENDS

