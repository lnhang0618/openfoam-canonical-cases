set term pngcairo font "Times,12"

# 第一张图
set output "U_Residual.png"
set xlabel "Time"
set ylabel "Residual"
set format y
set logscale y
plot for [file in system("echo Ux_0 Uy_0 Uz_0")] file using 1:2 with lines title file

# 第二张图
set output "uTau_bottomWall_vs.png"
set xlabel "Time"
set ylabel "uTau_{bottomWall}"
unset logscale y
plot for [file in system("echo uTau_model uTau_bottomWall")] file using 1:2 with lines title file,\
     0.0547883 with lines title "uTau_DNS"


# 第三张图
set output "ReTau_bottomWall.png"
set xlabel "Time"
set ylabel "ReTau_{bottomWall}"
plot for [file in system("echo ReTau_model ReTau_bottomWall")] file using 1:2 with lines title file,\
     219.153 with lines title "ReTau_DNS"

# 显示第三张图
set term x11
replot
pause 10

# 第四张图
set output "pressureGradient.png"
set xlabel "Time"
set ylabel "Pressure Gradient"
unset logscale y
set yrange [0.04:0.08]
plot "pressureGradient" using 1:2 with lines title "Pressure Gradient"