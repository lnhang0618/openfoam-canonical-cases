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
     0.06373 with lines title "uTau_DNS"


# 第三张图
set output "ReTau_bottomWall.png"
set xlabel "Time"
set ylabel "ReTau_{bottomWall}"
set yrange [160:220]
plot for [file in system("echo ReTau_model ReTau_bottomWall")] file using 1:2 with lines title file,\
     182.08571428571426 with lines title "ReTau_DNS"

# 第四张图
set output "pressureGradient.png"
set xlabel "Time"
set ylabel "Pressure Gradient"
unset logscale y
set yrange [0.0025:0.005]
plot "pressureGradient" using 1:2 with lines title "Pressure Gradient"