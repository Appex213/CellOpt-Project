************************************************************************
* auCdl Netlist:
* 
* Library Name:  WaveProResearch
* Top Cell Name: DLY_CAP_X2
* View Name:     av_extracted
* Netlisted on:  Apr  6 16:34:15 2020
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
* Cell Name:    DLY_CAP_X2
* View Name:    av_extracted
************************************************************************

.SUBCKT DLY_CAP_X2 A VDD VSS
*.PININFO A:I VDD:B VSS:B
Cc1 A VDD 26.0361e-18 $[CP]
Cc2 N0 VDD 20.3678e-18 $[CP]
Cc3 N1 VDD 845.301e-21 $[CP]
Cc4 N2 VDD 424.827e-21 $[CP]
Cc5 N3 VDD 424.827e-21 $[CP]
Cc6 N4 VDD 171.346e-18 $[CP]
Cc7 N5 VDD 1.71329e-18 $[CP]
Cc8 N6 VDD 1.71329e-18 $[CP]
Cc9 A N1 9.01181e-18 $[CP]
Cc10 A N2 436.896e-21 $[CP]
Cc11 A N3 436.896e-21 $[CP]
Cc12 N0 N1 20.9669e-18 $[CP]
Cc13 A N4 3.48252e-18 $[CP]
Cc14 N7 A 2.2513e-18 $[CP]
Cc15 N8 A 4.54366e-18 $[CP]
Cc16 N5 A 3.00202e-18 $[CP]
Cc17 N6 A 3.00202e-18 $[CP]
Cc18 N4 N0 2.96373e-18 $[CP]
Cc19 N7 N0 1.29374e-18 $[CP]
Cc20 N8 N0 1.37136e-18 $[CP]
Cc21 N5 N0 913.279e-21 $[CP]
Cc22 N6 N0 913.28e-21 $[CP]
Cc23 N5 N9 2.60419e-18 $[CP]
Cc24 N4 N9 5.81571e-18 $[CP]
Cc25 N6 N9 2.60806e-18 $[CP]
Cc26 N10 VDD 78.8973e-18 $[CP]
Cc27 N9 N1 34.2498e-18 $[CP]
Cc28 N9 N2 1.68923e-18 $[CP]
Cc29 N4 N10 2.07061e-18 $[CP]
Cc30 N3 N9 1.68923e-18 $[CP]
Cc31 N8 N9 37.1113e-18 $[CP]
Rrj4 N4 N7 371.7e-3 $[RP]
Rrj5 N7 VSS 198e-3 $[RP]
Rrj6 VSS N8 109.5e-3 $[RP]
Rrj7 N8 VSS 76.29e-3 $[RP]
Rrj8 N7 N5 106.5e-3 $[RP]
Rrj9 N8 N6 106.5e-3 $[RP]
Rrk3 N10 N0 45.0547 $[RP]
Rrk4 N0 N9 50.6403 $[RP]
Rrn1 N1 N4 13 $[RP]
Rrn2 N2 N5 26 $[RP]
Rrn3 N3 N6 26 $[RP]
Rrn_1_1 N1 N4 13 $[RP]
Rro1 N0 A 6.6667 $[RP]
MM0 VDD N10 VDD VDD pch l=120e-9 w=585e-9 m=1
MM1 N2 N9 N3 N1 nch l=120e-9 w=495e-9 m=1
.ENDS

