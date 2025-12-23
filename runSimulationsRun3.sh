#!/bin/bash

# Author: Colby Thompson
# Date: 01/02/2025
# Purpose: Executing this script will generate N 1800GeV di-gluino R-Hadron samples given the current R-Hadron energy deposit model in SimG4Core.
#          The script will then pass the file through the reconstruction chain, and ultimately through the current NTuplizer.
#          The script will also create CSVs of the R-Hadron energy deposits during simulation, and also a CSV of the R-Hadron vertices from the GEN-SIM AOD ROOT file.

# CONTROL CENTER ----------------------

mass=1800
events=1
flavor="gluino" # gluino or stop
cmEnergy="13.6TeV"
ctau='0p1' # mm
quarkDecay="heavy" # heavy or light
neutralinoMass=1300
crab=true
njobs=1
memory=1000

prefix="mgToPythia_"$flavor$mass"to"$quarkDecay"qq_andChi10"$neutralinoMass"_ctau"$ctau"mm"

gensim=true
reco=false

# -------------------------------------

# Create data directory if it does not already exist
dir_name='data/'$prefix
echo "All files will be saved in $dir_name"

if [ ! -d "$dir_name" ]; then
    mkdir -p $dir_name
    echo "creating $dir_name"
fi

# gen-sim output files
genSimRoot="gensim_"$events"Events.root"

# digi-L1-digi2ray output files
digiRawRoot="digiraw_"$events"Events.root"
digiRawOut="digiraw_"$events"Events.out"

# reco output files
recoRoot="reco_"$events"Events.root"
recoOut="reco_"$events"Events.out"

if $gensim; then

    if [ ! -f $dir_name/$genSimRoot ]; then
        echo "Starting step 0: GEN-SIM"
        
        if [ "$flavor" = "gluino" ]; then
            echo "Generating $events gluino R-hadrons events with mass $mass GeV and ctau $ctau mm decaying to $quarkDecay quarks"
            echo "Using MadGraph to Pythia interface for event generation"
            cp mgToPythia_simulate_gluinoRhadron_decays_Run3.py $dir_name/gensim.py

            if $crab; then
                echo "Submitting jobs to CRAB"
                cp crabConfig.py $dir_name/.
                cd $dir_name

                sed -i "s/Type=gensim/Type=gensim/g" crabConfig.py
                sed -i "s/maxEvents=10000/maxEvents=$events/g" crabConfig.py
                sed -i "s/mass=1800/mass=$mass/g" crabConfig.py
                sed -i "s/ctau=1000/ctau='$ctau'/g" crabConfig.py
                sed -i "s/quarkDecay='heavy'/quarkDecay='$quarkDecay'/g" crabConfig.py
                sed -i "s/njobs=100/njobs=$njobs/g" crabConfig.py
                sed -i "s/memory=3000/memory=$memory/g" crabConfig.py

                crab submit -c crabConfig.py
            else
                cd $dir_name
                cmsRun gensim.py maxEvents=$events mass=$mass ctau=$ctau quarkDecay=$quarkDecay outputFile=$genSimRoot > "terminalOutput.log"
            fi

        elif [ "$flavor" = "stop" ]; then
            echo "Generating $events stop R-hadrons events with mass $mass GeV and ctau $ctau mm decaying to $quarkDecay quarks"
            cmsRun simulate_stopRhadron_decays_Run3.py maxEvents=$events mass=$mass ctau=$ctau quarkDecay=$quarkDecay outputFile=$genSimRoot > "terminalOutput.log"
        else
            echo "Invalid flavor specified. Please use 'gluino' or 'stop'."
            exit 1
        fi

        echo "Step 0 completed"
    fi

fi

if $reco; then

    if [ ! -f $digiRawRoot ]; then
        echo "Starting step 1: DIGI-L1-DIGI2RAW"
        cmsDriver.py --filein file:$genSimRoot \
            --fileout file:$digiRawRoot\
            --mc \
            --eventcontent RAWSIM \
            --datatier GEN-SIM-RAW \
            --conditions 150X_mcRun3_2025_realistic_v2 \
            --step DIGI,L1,DIGI2RAW \
            --python_filename step1_cfg.py \
            --era Run3_2025 \
            -n -1 >& $digiRawOut
        echo "Step 1 completed"
    fi

    if [ ! -f $recoRoot ]; then
        echo "Starting step 2: RAW2DIGI-L1Reco-RECO"
        cmsDriver.py --filein file:$digiRawRoot \
            --fileout file:$recoRoot \
            --mc \
            --eventcontent FEVTDEBUGHLT \
            --datatier AODSIM \
            --conditions 150X_mcRun3_2025_realistic_v2 \
            --step RAW2DIGI,L1Reco,RECO \
            --python_filename step2_cfg.py \
            --era Run3_2025 \
            -n -1 >& $recoOut
        echo "Step 2 completed"
    fi
    
fi