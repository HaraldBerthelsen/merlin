#!/bin/bash

if test "$#" -ne 1; then
    echo "Usage: ./scripts/setup.sh <voice_directory_name>"
    exit 1
fi

current_working_dir=$(pwd)
merlin_dir=$(dirname $(dirname $(dirname $current_working_dir)))
experiments_dir=${current_working_dir}/experiments
data_dir=${current_working_dir}/blizzard

voice_name=$1
voice_dir=${experiments_dir}/${voice_name}

acoustic_dir=${voice_dir}/acoustic_model
duration_dir=${voice_dir}/duration_model
prominence_dir=${voice_dir}/prominence_model
synthesis_dir=${voice_dir}/test_synthesis

cp -r ${data_dir} ${experiments_dir}
#mkdir -p ${experiments_dir}
#mkdir -p ${voice_dir}
#mkdir -p ${acoustic_dir}
#mkdir -p ${duration_dir}
mkdir -p ${prominence_dir}

#if [ "$voice_name" == "blizzard" ]
#then
#    data_dir=slt_arctic_demo_data
#elif [ "$voice_name" == "slt_arctic_full" ]
#then
#    data_dir=slt_arctic_full_data
#HB
#elif [ "$voice_name" == "slt_arctic_demo_promark" ]
#then
#    data_dir=slt_arctic_demo_data
#elif [ "$voice_name" == "slt_arctic_full_promark" ]
#then
#    data_dir=slt_arctic_full_data
#END HB
#else
#    echo "The data for voice name ($voice_name) is not available...please use slt_arctic_demo or slt_arctic_full !!"
#    exit 1
#fi

# ZM deleted here the unzip of arctic slt data



cp -r ${duration_dir}/data ${prominence_dir}/data
#cp ${prominence_dir}/data/label_phone_align/arctic_a005[6-9].lab ${synthesis_dir}/prompt-lab/
#cp ${prominence_dir}/data/label_phone_align/arctic_a0060.lab ${synthesis_dir}/prompt-lab/
#echo "data is ready!"



#ZM copy prominence tags to full context labels using alignpromark.tcl 
if [ "$voice_name" == "blizzard" ]
#HB for phone_align	then make demo
	then make blizzard
#elif [ "$voice_name" == "slt_arctic_full_promark" ]
#	then make full
else
	echo "The prominence data for voice name ($voice_name) is not available...please use slt_arctic_demo_promark or slt_arctic_full_promark !!"
    exit 1
fi
#end ZM


global_config_file=conf/global_settings.cfg

### default settings ###
echo "MerlinDir=${merlin_dir}" >  $global_config_file
echo "WorkDir=${current_working_dir}" >>  $global_config_file
echo "Voice=${voice_name}" >> $global_config_file
#HB for phone_align
#HB echo "Labels=state_align" >> $global_config_file
echo "Labels=phone_align" >> $global_config_file
echo "Vocoder=WORLD" >> $global_config_file
echo "SamplingFreq=16000" >> $global_config_file

#HB
if [ "$voice_name" == "blizzard" ]
then
    echo "QuestionFile=questions-unilex_dnn_600.hed" >> $global_config_file
    echo "QuestionFilePromNet=questions-unilex_dnn_601_promark.hed" >> $global_config_file
    echo "FileIDList=file_id_list.scp" >> $global_config_file
    echo "Train=2564" >> $global_config_file 
    echo "Valid=300" >> $global_config_file 
    echo "Test=50" >> $global_config_file 
else
    echo "The data for voice name ($voice_name) is not available...please use slt_arctic_demo or slt_arctic_full !!"
    exit 1
fi

echo "Merlin default voice settings configured in $global_config_file"
echo "setup done...!"

