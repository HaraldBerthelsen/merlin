#!/bin/bash -e

global_config_file=conf/global_settings.cfg
source $global_config_file

if test "$#" -ne 3; then
    echo "################################"
    echo "Usage: "
    echo "./05_run_merlin.sh <path_to_test_prom_conf_file> <path_to_test_dur_conf_file> <path_to_test_synth_conf_file>"
    echo ""
    echo "Default path to test duration conf file: conf/test_dur_synth_${Voice}.conf"
    echo "Default path to test synthesis conf file: conf/test_synth_${Voice}.conf"
    echo "################################"
    exit 1
fi

test_prom_config_file=$1
test_dur_config_file=$2
test_synth_config_file=$3


### Step 5: synthesize speech ###
echo "Step 5:" 


#read from prompt-lab, add prominence feature (K) and write in gen_prom-lab
#The K feature is already present in the input files, and another K is added
#Should the K feature not be there in the input, or should it be replaced?
#Changed so that it's added if it doesn't exist, replaced otherwise

echo "synthesizing prominence..."
#./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_prom_config_file
#HB changed submit.sh so it exits on error



#Input file experiments/slt_arctic_demo_promark/test_synthesis/gen_prom-lab/arctic_a0001.lab
#Looks right but gives
#Traceback (most recent call last):
#  File "/home/harald/git/hb_merlin/src/run_merlin.py", line 1241, in <module>
#    main_function(cfg)
#  File "/home/harald/git/hb_merlin/src/run_merlin.py", line 572, in main_function
#    label_normaliser.perform_normalisation(in_label_align_file_list, binary_label_file_list, label_type=cfg.label_type)
#  File "/media/bigdisk/git/hb_merlin/src/frontend/linguistic_base.py", line 68, in perform_normalisation
#    self.extract_linguistic_features(ori_file_list[i], output_file_list[i], label_type)
#  File "/media/bigdisk/git/hb_merlin/src/frontend/label_normalisation.py", line 26, in extract_linguistic_features
#    A = self.load_labels_with_state_alignment(in_file_name)
#  File "/media/bigdisk/git/hb_merlin/src/frontend/label_normalisation.py", line 777, in load_labels_with_state_alignment
#    line = utt_labels[current_index + i + 1].strip()

#Because of this issue with state_aligned labels, I try to switch to phone_align, that's what Zofia wants anyway.
#Then 'synthesising prominence' seems to work, but no K is in the output.
#changed in label_modifier.py, now K is always 10.. Does it work with the final step?
#No. duration _seems_ to work, not sure if it really does.
#acoustic fails, wrong label dimension (426)

#The labels are wrong in prompt-lab, they're state_align still. CHANGED


echo "synthesizing durations..."
#./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_dur_config_file

#exit


echo "synthesizing speech..."
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_synth_config_file

echo "deleting intermediate synthesis files..."
./scripts/remove_intermediate_files.sh $global_config_file

echo "synthesized audio files are in: experiments/${Voice}/test_synthesis/wav"
echo "All successfull!! Your demo voice is ready :)"

