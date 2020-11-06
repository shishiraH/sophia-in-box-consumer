set datafile separator ","
set xdata time
set style data lines
set autoscale y
set terminal x11 size 1300,800

set multiplot layout 2, 1
set lmargin at screen 0.03
set offsets 0, 0, 1, 1

set linetype 1 lc rgb "dark-violet" lw 4 pt 0
set linetype 2 lc rgb "sea-green"   lw 4 pt 7
set linetype 3 lc rgb "dark-red"    lw 4 pt 5 pi -1
set linetype 4 lc rgb "blue"        lw 4 pt 8
set linetype 5 lc rgb "dark-orange" lw 4 pt 3
set linetype 6 lc rgb "black"       lw 4 pt 11
set linetype 7 lc rgb "goldenrod"   lw 4
set linetype 8 lc rgb "light-coral" lw 4
set linetype 9 lc rgb "#808000"     lw 4
set linetype 10 lc rgb "#008080"    lw 4
set linetype 11 lc rgb "#191970"    lw 4
set linetype 12 lc rgb "#8B4513"    lw 4
set linetype cycle 12

rows = system("wc -l ".inputfile)
if (rows > 600) N = rows - 600; else N = 0
#plot for [i=2:50] inputfile every ::N using 0:i w l title columnheader

cols = system("head -n1 ".inputfile." | tr -cd , | wc -c")
plot for [i=2:cols+1:2] inputfile every ::N using 0:i w l title columnheader
plot for [i=3:cols+1:2] inputfile every ::N using 0:i w l title columnheader

#first_sr_col = 1 + cols - (4 * 2)
#plot for [i=2:first_sr_col:2] inputfile every ::N using 0:i w l title columnheader
#plot for [i=3:first_sr_col:2] inputfile every ::N using 0:i w l title columnheader
#plot for [i=first_sr_col+1:cols+1:2] inputfile every ::N using 0:i w l title columnheader
#plot for [i=first_sr_col+2:cols+1:2] inputfile every ::N using 0:i w l title columnheader

unset multiplot
pause 0.2
reread
