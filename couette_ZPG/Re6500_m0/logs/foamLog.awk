# Awk script for OpenFOAM log file extraction
BEGIN {
    Iteration=0
    resetCounters()
}

# Reset counters used for variable postfix
function resetCounters() {
    clockTimeCnt=0
    contCumulativeCnt=0
    contGlobalCnt=0
    contLocalCnt=0
    CourantMaxCnt=0
    CourantMeanCnt=0
    executionTimeCnt=0
    pCnt=0
    pFinalResCnt=0
    pItersCnt=0
    SeparatorCnt=0
    TimeCnt=0
    UxCnt=0
    UxFinalResCnt=0
    UxItersCnt=0
    UyCnt=0
    UyFinalResCnt=0
    UyItersCnt=0
    UzCnt=0
    UzFinalResCnt=0
    UzItersCnt=0
    # Reset counters for 'Solving for ...'
    for (varName in subIter)
    {
        subIter[varName]=0
    }
}

# Extract value after columnSel
function extract(inLine,columnSel,outVar,a,b)
{
    a=index(inLine, columnSel)
    b=length(columnSel)
    split(substr(inLine, a+b),outVar)
    gsub("[,:]","",outVar[1])
}

# Iteration separator (increments 'Iteration')
/^[ \t]*Time = / {
    Iteration++
    resetCounters()
}

# Time extraction (sets 'Time')
/^[ \t]*Time = / {
    extract($0, "Time = ", val)
    Time=val[1]
}

# Skip whole line with singularity variable
/solution singularity/ {
    next;
}

# Extract: 'Solving for ...'
/Solving for/ {
    extract($0, "Solving for ", varNameVal)

    varName=varNameVal[1]
    file=varName "_" subIter[varName]++
    file="logs/" file
    extract($0, "Initial residual = ", val)
    print Time "\t" val[1] > file

    varName=varNameVal[1] "FinalRes"
    file=varName "_" subIter[varName]++
    file="logs/" file
    extract($0, "Final residual = ", val)
    print Time "\t" val[1] > file

    varName=varNameVal[1] "Iters"
    file=varName "_" subIter[varName]++
    file="logs/" file
    extract($0, "No Iterations ", val)
    print Time "\t" val[1] > file
}

# Extract: 'clockTime'
/ClockTime = / {
    extract($0, "ClockTime =", val)
    file="logs/clockTime_" clockTimeCnt
    print Time "\t" val[1] > file
    clockTimeCnt++
}

# Extract: 'contCumulative'
/time step continuity errors :/ {
    extract($0, "cumulative = ", val)
    file="logs/contCumulative_" contCumulativeCnt
    print Time "\t" val[1] > file
    contCumulativeCnt++
}

# Extract: 'contGlobal'
/time step continuity errors :/ {
    extract($0, " global = ", val)
    file="logs/contGlobal_" contGlobalCnt
    print Time "\t" val[1] > file
    contGlobalCnt++
}

# Extract: 'contLocal'
/time step continuity errors :/ {
    extract($0, "sum local = ", val)
    file="logs/contLocal_" contLocalCnt
    print Time "\t" val[1] > file
    contLocalCnt++
}

# Extract: 'CourantMax'
/Courant Number / {
    extract($0, "max: ", val)
    file="logs/CourantMax_" CourantMaxCnt
    print Time "\t" val[1] > file
    CourantMaxCnt++
}

# Extract: 'CourantMean'
/Courant Number / {
    extract($0, "mean: ", val)
    file="logs/CourantMean_" CourantMeanCnt
    print Time "\t" val[1] > file
    CourantMeanCnt++
}

# Extract: 'executionTime'
/ExecutionTime = / {
    extract($0, "ExecutionTime = ", val)
    file="logs/executionTime_" executionTimeCnt
    print Time "\t" val[1] > file
    executionTimeCnt++
}

# Extract: 'Separator'
/^[ \t]*Time = / {
    extract($0, "Time = ", val)
    file="logs/Separator_" SeparatorCnt
    print Time "\t" val[1] > file
    SeparatorCnt++
}

# Extract: 'Time'
/^[ \t]*Time = / {
    extract($0, "Time = ", val)
    file="logs/Time_" TimeCnt
    print Time "\t" val[1] > file
    TimeCnt++
}
# Extract: 'uTau_model'
/Expression uTau on bottomWall:/ {
    extract($0, "average=", val)
    file="logs/uTau_model"
    print Time "\t" val[1] > file
}
# Extract: 'uTau_bottomWall'
/Expression uTau_wallshear on bottomWall:/ {
    extract($0, "average=", val)
    file="logs/uTau_bottomWall"
    print Time "\t" val[1] > file
}
# Extract: 'ReTau_model'
/Expression ReTau on bottomWall:/ {
    extract($0, "average=", val)
    file="logs/ReTau_model"
    print Time "\t" val[1] > file
}
# Extract: 'ReTau_bottomWall'
/Expression ReTau_wallshear on bottomWall:/ {
    extract($0, "average=", val)
    file="logs/ReTau_bottomWall"
    print Time "\t" val[1] > file
}
# Extract: 'yPlus_topWall'
/Expression yPlus on topWall:/ {
    extract($0, "average=", val)
    file="logs/yPlus_topWall"
    print Time "\t" val[1] > file
}
# Extract: 'yPlus_bottomWall'
/Expression yPlus on bottomWall:/ {
    extract($0, "average=", val)
    file="logs/yPlus_bottomWall"
    print Time "\t" val[1] > file
}
# Extract: 'pressureGradient'
/Pressure gradient source:/ {
    extract($0, "pressure gradient = ", val)
    file="logs/pressureGradient"
    print Time "\t" val[1] > file

    if (Time > 50) {
        sum += val[1]
        count++
    }
}

END {
    if (count > 0) {
        avg = sum / count
        file="logs/pressureGradient_avg"
        print "Average pressure gradient for Time > 50: " avg > file
    }
}