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
ctau='1000' # mm
quarkDecay="heavy" # heavy or light
neutralinoMass=1300
conditions="150X_mcRun3_2024_realistic_v2"
era="Run3_2024"
madgraph=false
pileup_filelist="dbs:/Neutrino_E-10_gun/RunIIISummer24PrePremix-Premixlib2024_140X_mcRun3_2024_realistic_v26-v1/PREMIX"
hlt_menu="HLT:GRun" # HLT:GRun is the default, 2025v13 and 2024v14 are also options. However 2024v14 is deprecated

if $madgraph; then
    prefix=$flavor$mass"to"$quarkDecay"qq_andChi10"$neutralinoMass"_ctau"$ctau"mm_Madgraph_"$conditions
else
    prefix=$flavor$mass"to"$quarkDecay"qq_andChi10"$neutralinoMass"_ctau"$ctau"mm_"$conditions
fi

gensim=true
premix=false
digi=true
hlt=true
reco=true
miniAOD=true

# -------------------------------------

# Create data directory if it does not already exist
dir_name='data/'$prefix
echo "All files will be saved in $dir_name"

if [ ! -d "$dir_name" ]; then
    mkdir -p $dir_name
    echo "creating $dir_name"
fi

genSimRoot="gensim_"$events"Events.root"
premixRoot="premix_"$events"Events.root"
premixOut="premix_"$events"Events.out"
digiRawRoot="digiraw_"$events"Events.root"
digiRawOut="digiraw_"$events"Events.out"
hltRoot="hlt_"$events"Events.root"
hltOut="hlt_"$events"Events.out"
recoRoot="reco_"$events"Events.root"
recoOut="reco_"$events"Events.out"
miniAODRoot="miniAOD_"$events"Events.root"
miniAODOut="miniAOD_"$events"Events.out"

if $gensim; then
    if [ ! -f $dir_name/$genSimRoot ]; then
        echo "Starting step 0: GEN-SIM"  
        if [ "$flavor" = "gluino" ]; then
            echo "Generating $events gluino R-hadrons events with mass $mass GeV and ctau $ctau mm decaying to $quarkDecay quarks"
            if $madgraph; then
                echo "Using MadGraph for event generation"
                cp gensim.py $dir_name/gensim.py
            else
                echo "Using Pythia for event generation"
                cp gensim_noMG.py $dir_name/gensim.py
            fi
            cd $dir_name
            cmsRun gensim.py maxEvents=$events mass=$mass ctau=$ctau quarkDecay=$quarkDecay outputFile=$genSimRoot > "terminalOutput.log"

        elif [ "$flavor" = "stop" ]; then
            echo "Generating $events stop R-hadrons events with mass $mass GeV and ctau $ctau mm decaying to $quarkDecay quarks"
            cmsRun simulate_stopRhadron_decays_Run3.py maxEvents=$events mass=$mass ctau=$ctau quarkDecay=$quarkDecay outputFile=$genSimRoot > "terminalOutput.log"
        else
            echo "Invalid flavor specified. Please use 'gluino' or 'stop'."
            exit 1
        fi
        echo "Step 0 completed"
        else
            cd $dir_name
    fi
    else
        cd $dir_name
fi

if $premix; then
    if [ ! -f $premixRoot ]; then
        echo "Starting step 1: Premixing"
        cmsDriver.py --filein file:$genSimRoot \
            --fileout file:$premixRoot \
            --mc \
            --eventcontent PREMIXRAW \
            --datatier GEN-SIM-DIGI \
            --conditions "$conditions" \
            --geometry DB:Extended \
            --pileup_input "$pileup_filelist" \
            --step DIGI,DATAMIX,L1,DIGI2RAW \
            --python_filename premix.py \
            --procModifiers premix_stage2 \
            --datamix PreMix \
            --era "$era" \
            -n -1 >& $premixOut 
        echo "Step 0.5 completed"
    fi
    digiRawRoot=$premixRoot # For premixing, the premix output is already in DIGI2RAW format. Skip the digi step.
elif $digi; then
    if [ ! -f $digiRawRoot ]; then
        echo "Starting step 1: DIGI-L1-DIGI2RAW"
        cmsDriver.py --filein file:$genSimRoot \
            --fileout file:$digiRawRoot\
            --mc \
            --eventcontent RAWSIM \
            --datatier GEN-SIM-RAW \
            --conditions "$conditions" \
            --geometry DB:Extended \
            --step DIGI,L1,DIGI2RAW \
            --python_filename digi.py \
            --era "$era" \
            -n -1 >& $digiRawOut
        echo "Step 1 completed"
    fi
fi

if $hlt; then
    if [ ! -f $hltRoot ]; then
        echo "Starting step 1.5: HLT"
        cmsDriver.py --filein file:$digiRawRoot \
            --fileout file:$hltRoot \
            --mc \
            --eventcontent RAWSIM \
            --datatier GEN-SIM-RAW \
            --conditions "$conditions" \
            --step $hlt_menu \
            --geometry DB:Extended \
            --python_filename hlt.py \
            --era "$era" \
            -n -1 >& $hltOut
        echo "Step 1.5 completed"
    fi
fi

if $reco; then
    if [ ! -f $recoRoot ]; then
        echo "Starting step 2: RAW2DIGI-L1Reco-RECO"
        cmsDriver.py --filein file:$hltRoot \
            --fileout file:$recoRoot \
            --mc \
            --eventcontent AODSIM \
            --datatier AODSIM \
            --conditions "$conditions" \
            --geometry DB:Extended \
            --step RAW2DIGI,L1Reco,RECO \
            --python_filename reco.py \
            --era "$era" \
            -n -1 >& $recoOut
        echo "Step 2 completed"
    fi
fi

if $miniAOD; then
    echo "Starting step 3: RECO-MINIAOD"
    cmsDriver.py --filein file:$recoRoot \
        --fileout file:$miniAODRoot \
        --mc \
        --eventcontent MINIAODSIM \
        --datatier MINIAODSIM \
        --conditions "$conditions" \
        --geometry DB:Extended \
        --step PAT \
        --python_filename miniAOD.py \
        --era "$era" \
        -n -1 >& $miniAODOut
    echo "Step 3 completed"
fi