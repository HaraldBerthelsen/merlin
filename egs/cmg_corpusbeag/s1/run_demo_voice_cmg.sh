#!/bin/bash

setup_data=false
setup_train=false
train_tts=true
run_tts=false

if test "$#" -ne 1; then
    voice_name="cmg_corpusbeag"
else
    voice_name=$1
    setup_data=false # assuming wav and txt in database
fi

# setup directory structure and download data
if [ "$setup_data" = true ]; then
    #cleanup
    rm -rf database
    
    # link data
    mkdir -p database/labels
    ln -s ~/svn/Corpora/ga_MU/cmg/CMGCorpusBeag/wav16_trimmed database/wav
    ln -s ~/svn/Corpora/ga_MU/cmg/CMGCorpusBeag/htslab database/labels/label_phone_align
fi

# setup for train tts system
if [ "$setup_train" = true ]; then
    # step 1: run setup
    ./01_setup.sh $voice_name

    # step 2: prepare labels
    ./02_prepare_labels_cmg.sh database/wav database/labels demo

    # step 3: extract acoustic features
    ./03_prepare_acoustic_features.sh database/wav database/feats

    # step 4: prepare config files for training and testing
    ./04_prepare_conf_files.sh conf/global_settings.cfg
fi

# train tts system
if [ "$train_tts" = true ]; then

    # step 5: train duration model
    ./05_train_duration_model.sh conf/duration_${voice_name}.conf
    
    # step 6: train acoustic model
    ./06_train_acoustic_model.sh conf/acoustic_${voice_name}.conf

fi



# run tts
if [ "$run_tts" = true ]; then

    basename --suffix=.txt -- experiments/${voice_name}/test_synthesis/txt/* > experiments/${voice_name}/test_synthesis/test_id_list.scp

    # step 7: run text to speech
   ./07_run_merlin.sh experiments/${voice_name}/test_synthesis/txt conf/test_dur_synth_${voice_name}.conf conf/test_synth_${voice_name}.conf

fi

echo "done...!"
