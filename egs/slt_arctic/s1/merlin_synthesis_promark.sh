#!/bin/bash -e

if test "$#" -eq 1; then
    global_config_file=$1
    if [ ! -f  $global_config_file ]; then
	echo "Voice config file doesn't exist"
	#PrintUsage
	exit 1
    else
	source $global_config_file
    fi
elif test "$#" -eq 3; then
    MerlinDir=$1
    Voice=$2
    Labels=$3
else
    echo "Usage: ./merlin_synthesis_promark.sh <global_config_file> OR ./merlin_synthesis_promark.sh <MerlinDir> <Voice> <Labels>"
    echo "Example 1: ./merlin_synthesis_promark.sh conf/global_settings.conf"
    echo "Example 2: ./merlin_synthesis_promark.sh ~/git/hb_merlin slt_arctic_demo_promark state_align"
    exit 1
fi

PrintUsage () {
    echo "Please first run either demo voice or full voice!!"
    echo "To run demo voice: ./run_demo_promark.sh"
    echo "To run full voice: ./run_full_voice.sh"
}

#global_config_file=conf/global_settings.cfg

### define few variables here
testDir=experiments/${Voice}/test_synthesis

txt_dir=${testDir}/txt
txt_file=${testDir}/utts.data

if [[ ! -d "${testDir}" ]]; then
    PrintUsage
    exit 1
fi

if [[ ! -d "${txt_dir}" ]] && [[ ! -f "${txt_file}" ]]; then
    echo "Please give input: either 1 or 2"
    echo "1. ${txt_dir}  -- a text directory containing text files"
    echo "2. ${txt_file} -- a single text file with each sentence in a new line in festival format"
    exit 1
fi


### Step 1: create label files from text ###
echo "Step 1: creating label files from text..."
#HB global_config_file used to pass $Voice, $MerlinDir (for $FESTDIR and $frontend), and $Labels (state_align or phone_align, for normalize_lab_for_merlin.py)
#./scripts/prepare_labels_from_txt_promark.sh $global_config_file
#HB changed to pass the variables directly, as read from global_config_file
./scripts/prepare_labels_from_txt_promark.sh $MerlinDir $Voice $Labels

### Step 2: synthesize speech   ###
echo "Step 2: synthesizing speech..."
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_prom_synth_${Voice}.conf

#Modify output prom value if needed..
python scripts/addProminenceValues_ssml.py ${testDir}/txt ${testDir}/gen_prominence-lab


./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_dur_synth_${Voice}.conf
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_synth_${Voice}.conf

### Step 3: delete intermediate synth files ###
echo "Step 3: deleting intermediate synthesis files..."
#HB global_config_file only used to pass $Voice
#./scripts/remove_intermediate_files_promark.sh $global_config_file
#HB changed to pass Voice directly
./scripts/remove_intermediate_files_promark.sh $Voice

echo "synthesized audio files are in: experiments/${Voice}/test_synthesis/wav"

