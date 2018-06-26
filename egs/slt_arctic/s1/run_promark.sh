#!/bin/bash -e


PrintUsage () {
    echo "Usage: ./run_promark.sh <MerlinDir> <Voice> <Labels> (<(-)starting step>)"
    echo "Example to run all steps: ./run_promark.sh ~/git/hb_merlin slt_arctic_demo_promark state_align"
    echo "Example to run from step 5: ./run_promark.sh ~/git/hb_merlin slt_arctic_demo_promark state_align 5"
    echo "Example to run ONLY step 5: ./run_promark.sh ~/git/hb_merlin slt_arctic_demo_promark state_align -5"
}


CheckContinue () {
    echo "run_only_one_step = $run_only_one_step"
    if [ "$run_only_one_step" == "true" ]; then
	echo "run_only_one_step = true! Exiting.."	
	exit 0
    else
	echo "run_only_one_step = false! Continuing.."		
    fi
}

if test "$#" -gt 4; then
    PrintUsage
    exit 1
elif test "$#" -lt 3; then
    PrintUsage
    exit 1
fi

#Allow optional last argument for starting step (int) or only step to run (-int)
if test "$#" -eq 4; then
    step=$4
else
    step=1
fi

if test "$step" -lt 0; then
    step=$(( $step * -1 ))
    run_only_one_step=true
else
    run_only_one_step=false
fi



MerlinDir=$1
Voice=$2
Labels=$3


### Step 1: setup directories and the training data files ###

if test $step -le 1; then
    echo "step $step"
    ./01_setup_promark.sh $Voice $Labels
    CheckContinue
fi




### Step 2: prepare config files for acoustic, duration, prominence models and for synthesis ###
if test $step -le 2; then
    echo "step $step"
    ./02_prepare_conf_files_promark.sh conf/global_settings.cfg
    CheckContinue
fi


### Step 3: train duration model ###
if test $step -le 3; then
    echo "step $step"
    ./03a_train_prominence_model.sh conf/prominence_${Voice}.conf
    CheckContinue
fi



### Step 4: train duration model ###
if test $step -le 4; then
    echo "step $step"
    ./03_train_duration_model.sh conf/duration_${Voice}.conf
    CheckContinue
fi


    
### Step 5: train acoustic model ###
if test $step -le 5; then
    echo "step $step"
    ./04_train_acoustic_model.sh conf/acoustic_${Voice}.conf 
    CheckContinue
fi



### Step 6: synthesize speech ###
if test $step -le 6; then
    echo "step $step"
    set -x
    ./05_run_merlin_promark.sh conf/test_prom_synth_${Voice}.conf conf/test_dur_synth_${Voice}.conf conf/test_synth_${Voice}.conf 
    CheckContinue
fi





### Step 7: synthesize test speech ###
if test $step -le 7; then
    echo "step $step"

    synthesis_dir=experiments/slt_arctic_demo_promark/test_synthesis
    mkdir -p $synthesis_dir/txt
    echo "this is a test." > $synthesis_dir/txt/test_01.txt
    echo "this:P=200 is:P=0 a test:P=0." > $synthesis_dir/txt/test_02.txt
    echo "this:P=0 is:P=0 a test:P=200." > $synthesis_dir/txt/test_03.txt

    #./merlin_synthesis_promark.sh conf/global_settings.cfg
    #HB the global config file is used to get MerlinDir, Voice, Labels
    #./merlin_synthesis_promark.sh conf/global_settings_demo.cfg
    #HB changed to pass the variables directly 
    ./merlin_synthesis_promark.sh $MerlinDir $Voice $Labels

    #wavesurfer experiments/slt_arctic_demo_promark/test_synthesis/wav/test_*.wav
    CheckContinue
fi

#Just for testing...
if test $step -le 8; then
    echo "step $step"
    CheckContinue
fi

