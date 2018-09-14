#!/bin/bash -e

if test "$#" -ne 0; then
    echo "Usage: ./run_demo_promark.sh"
    exit 1
fi

### Step 1: setup directories and the training data files ###
echo "Step 1: setting up experiments directory and the training data files..."
global_config_file=conf/global_settings.cfg

./scripts/setup_promark.sh slt_arctic_demo_promark
./scripts/prepare_config_files.sh $global_config_file
./scripts/prepare_config_files_for_synthesis.sh $global_config_file

if [ ! -f  $global_config_file ]; then
    echo "Global config file doesn't exist"
    exit 1
else
    source $global_config_file
fi

### Step 2: train duration model ###
echo "Step 2: training duration model..."
echo ./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/duration_${Voice}.conf
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/duration_${Voice}.conf

### Step 3: train acoustic model ###
echo "Step 3: training acoustic model..."
echo ./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/acoustic_${Voice}.conf
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/acoustic_${Voice}.conf

### Step 4: synthesize speech   ###
echo "Step 4: synthesizing speech..."
#echo ./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_dur_synth_${Voice}.conf
#./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_dur_synth_${Voice}.conf
#echo ./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_synth_${Voice}.conf
#./scripts/submit.sh ${MerlinDir}/src/run_merlin.py conf/test_synth_${Voice}.conf

echo sh 05_run_merlin_promark.sh test_prom_synth_slt_arctic_demo_promark.conf test_dur_synth_slt_arctic_demo_promark.conf test_synth_slt_arctic_demo_promark.conf
sh 05_run_merlin_promark.sh test_prom_synth_slt_arctic_demo_promark.conf test_dur_synth_slt_arctic_demo_promark.conf test_synth_slt_arctic_demo_promark.conf


### Step 5: delete intermediate synth files ###
echo "Step 5: deleting intermediate synthesis files..."
./scripts/remove_intermediate_files.sh conf/global_settings.cfg

echo "synthesized audio files are in: experiments/${Voice}/test_synthesis/wav"
echo "All successfull!! Your demo voice is ready :)"
