************************************************************************
* auCdl Netlist:
* 
* Library Name:  WaveProResearch
* Top Cell Name: DLY_CAP_X8
* View Name:     av_extracted
* Netlisted on:  Apr  6 16:39:16 2020
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
* Cell Name:    DLY_CAP_X8
* View Name:    av_extracted
************************************************************************

.SUBCKT DLY_CAP_X8 A VDD VSS
*.PININFO A:I VDD:B VSS:B
Cc1 A VDD 24.9436e-18 $[CP]
Cc2 N0 VDD 845.301e-21 $[CP]
Cc3 N1 VDD 424.827e-21 $[CP]
Cc4 N2 VDD 424.827e-21 $[CP]
Cc5 N3 VDD 170.43e-18 $[CP]
Cc6 N4 VDD 1.71329e-18 $[CP]
Cc7 N5 VDD 1.71329e-18 $[CP]
Cc8 A N0 4.19006e-18 $[CP]
Cc9 A N1 436.896e-21 $[CP]
Cc10 A N2 436.896e-21 $[CP]
Cc11 A N3 3.48252e-18 $[CP]
Cc12 N6 A 1.79609e-18 $[CP]
Cc13 N7 A 3.91547e-18 $[CP]
Cc14 N4 A 3.00202e-18 $[CP]
Cc15 N5 A 3.00202e-18 $[CP]
Cc16 N4 N8 6.37057e-18 $[CP]
Cc17 N3 N8 9.35903e-18 $[CP]
Cc18 N5 N8 6.59355e-18 $[CP]
Cc19 N9 VDD 228.763e-18 $[CP]
Cc20 N9 N0 12.4222e-18 $[CP]
Cc21 N4 N9 913.279e-21 $[CP]
Cc22 N5 N9 913.28e-21 $[CP]
Cc23 N8 N0 50.7734e-18 $[CP]
Cc24 N8 N1 18.7604e-18 $[CP]
Cc25 N6 N8 21.9483e-18 $[CP]
Cc26 N3 N9 6.35856e-18 $[CP]
Cc27 N2 N8 18.7604e-18 $[CP]
Cc28 N7 N8 37.9201e-18 $[CP]
Rrj4 N3 N6 371.7e-3 $[RP]
Rrj5 N6 VSS 198e-3 $[RP]
Rrj6 VSS N7 109.5e-3 $[RP]
Rrj7 N7 VSS 76.29e-3 $[RP]
Rrj8 N6 N4 106.5e-3 $[RP]
Rrj9 N7 N5 106.5e-3 $[RP]
Rrk3 N9 N10 12.2415 $[RP]
Rrk4 N10 N8 13.6382 $[RP]
Rrn1 N0 N3 13 $[RP]
Rrn2 N1 N4 26 $[RP]
Rrn3 N2 N5 26 $[RP]
Rrn_1_1 N0 N3 13 $[RP]
Rro1 N10 A 6.6667 $[RP]
MM0 VDD N9 VDD VDD pch l=480e-9 w=585e-9 m=1
MM1 N1 N8 N2 N0 nch l=480e-9 w=495e-9 m=1
.ENDS

