#!/bin/bash -e

if test "$#" -ne 0; then
    echo "Usage: ./run_full_voice_promark.sh"
    exit 1
fi

### Step 1: setup directories and the training data files ###
./01_setup_promark.sh slt_arctic_full_promark

### Step 2: prepare config files for acoustic, duration, prominence models and for synthesis ###
./02_prepare_conf_files_promark.sh conf/global_settings.cfg

### Step 3a: train duration model ###
./03a_train_prominence_model.sh conf/prominence_slt_arctic_full_promark.conf

### Step 3: train duration model ###
./03_train_duration_model.sh conf/duration_slt_arctic_full_promark.conf

### Step 4: train acoustic model ###
./04_train_acoustic_model.sh conf/acoustic_slt_arctic_full_promark.conf 

### Step 5: synthesize speech ###
./05_run_merlin_promark.sh conf/test_prom_synth_slt_arctic_full_promark.conf conf/test_dur_synth_slt_arctic_full_promark.conf conf/test_synth_slt_arctic_full_promark.conf 


