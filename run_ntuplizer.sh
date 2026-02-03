sample='gluino1800'
neutralino='chi101300'
ctau='0p1'
decay='light'
year=2023
era='D'
isAOD='False'
isData='False'
data_directory="/eos/user/c/cthompso/crab_projects/crab_miniAOD_"$sample"_"$ctau"mm_"$decay"Decay_10000Events/results/"
outputFile='ntuples/'$sample'_'$neutralino'_'$ctau'mm_'$decay'Decay_130X_mcRun3_2023_realistic_postBPix_v2_noMETTest.root'

# Create a list of all files inside of data_directory to pass to inputFiles
for file in $(ls $data_directory); do
    if [[ $file == *.root ]]; then
        inputFiles+="file:"$data_directory$file","
    fi
done
inputFiles=${inputFiles::-1} # Remove trailing comma

echo "Running ntuplizer on data from $data_directory and saving to $outputFile"
cmsRun ntuplizer_cfg.py inputFiles=$inputFiles outputFile=$outputFile year=$year era=$era isAOD=$isAOD isData=$isData