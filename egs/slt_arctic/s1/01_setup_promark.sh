#!/bin/bash

if test "$#" -ne 1; then
    echo "Usage: ./scripts/setup.sh <voice_directory_name>"
    exit 1
fi

current_working_dir=$(pwd)
merlin_dir=$(dirname $(dirname $(dirname $current_working_dir)))
experiments_dir=${current_working_dir}/experiments

voice_name=$1
voice_dir=${experiments_dir}/${voice_name}

acoustic_dir=${voice_dir}/acoustic_model
duration_dir=${voice_dir}/duration_model
prominence_dir=${voice_dir}/prominence_model
synthesis_dir=${voice_dir}/test_synthesis

mkdir -p ${experiments_dir}

rm -rf ${voice_dir}
mkdir ${voice_dir}
mkdir -p ${acoustic_dir}
mkdir -p ${duration_dir}
mkdir -p ${prominence_dir}
mkdir -p ${synthesis_dir}

if [ "$voice_name" == "slt_arctic_demo" ]
then
    data_dir=slt_arctic_demo_data
elif [ "$voice_name" == "slt_arctic_full" ]
then
    data_dir=slt_arctic_full_data
#HB
elif [ "$voice_name" == "slt_arctic_demo_promark" ]
then
    data_dir=slt_arctic_demo_data
elif [ "$voice_name" == "slt_arctic_full_promark" ]
then
    data_dir=slt_arctic_full_data
#END HB
else
    echo "The data for voice name ($voice_name) is not available...please use slt_arctic_demo or slt_arctic_full !!"
    exit 1
fi

#HB (start from scratch) if true
#do_unzip=true
do_unzip=false




if [[ ! -f ${data_dir}.zip ]]; then
    echo "downloading data....."
    rm -f ${data_dir}.zip
    data_url=http://104.131.174.95/${data_dir}.zip
    if hash curl 2>/dev/null; then
        curl -O $data_url
    elif hash wget 2>/dev/null; then
        wget $data_url
    else
        echo "please download the data from $data_url"
        exit 1
    fi
    do_unzip=true
fi


if [[ ! -d ${data_dir} ]] || [[ "$do_unzip" = "true" ]]; then
    echo "unzipping files......"
    rm -fr ${data_dir}
    rm -fr ${duration_dir}/data
    rm -fr ${acoustic_dir}/data
    rm -fr ${prominence_dir}/data
    unzip -q ${data_dir}.zip
fi

#copy data files
echo "copying files......"

cp -r ${data_dir}/merlin_baseline_practice/duration_data/ ${duration_dir}/data
cp -r ${duration_dir}/data ${prominence_dir}/data
cp -r ${data_dir}/merlin_baseline_practice/acoustic_data/ ${acoustic_dir}/data
cp -r ${data_dir}/merlin_baseline_practice/test_data/* ${synthesis_dir}


use_phone_align=false
if [[ "$use_phone_align" = "true" ]]; then
    #HB for phone_align
    cp ${prominence_dir}/data/label_phone_align/arctic_a005[6-9].lab ${synthesis_dir}/prompt-lab/
    cp ${prominence_dir}/data/label_phone_align/arctic_a0060.lab ${synthesis_dir}/prompt-lab/
fi
    
echo "data is ready!"




#ZM copy prominence tags to full context labels using alignpromark.tcl 
if [ "$voice_name" == "slt_arctic_demo_promark" ]; then
    if [[ "$use_phone_align" = "true" ]]; then
	#HB for phone_align
	make demo-phone_align
    else
	make demo
    fi
elif [ "$voice_name" == "slt_arctic_full_promark" ]; then
    if [[ "$use_phone_align" = "true" ]]; then
	#HB for phone_align
	make full-phone_align
    else
	make full
    fi
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
#HB select state_align or phone_align
echo "Labels=state_align" >> $global_config_file
#echo "Labels=phone_align" >> $global_config_file
echo "Vocoder=WORLD" >> $global_config_file
echo "SamplingFreq=16000" >> $global_config_file

if [ "$voice_name" == "slt_arctic_demo" ]
then
    echo "QuestionFile=questions-radio_dnn_416.hed" >> $global_config_file
    echo "FileIDList=file_id_list_demo.scp" >> $global_config_file
    echo "Train=50" >> $global_config_file 
    echo "Valid=5" >> $global_config_file 
    echo "Test=5" >> $global_config_file 
#HB
elif [ "$voice_name" == "slt_arctic_demo_promark" ]
then
    echo "QuestionFile=questions-radio_promark_dnn_416.hed" >> $global_config_file
    echo "QuestionFilePromNet=questions-radio_dnn_416.hed" >> $global_config_file
    echo "FileIDList=file_id_list_demo.scp" >> $global_config_file
    echo "Train=50" >> $global_config_file 
    echo "Valid=5" >> $global_config_file 
    echo "Test=5" >> $global_config_file 
elif [ "$voice_name" == "slt_arctic_full_promark" ]
then
    echo "QuestionFile=questions-radio_promark_dnn_416.hed" >> $global_config_file
    echo "QuestionFilePromNet=questions-radio_dnn_416.hed" >> $global_config_file
    echo "FileIDList=file_id_list_full.scp" >> $global_config_file
    echo "Train=1000" >> $global_config_file 
    echo "Valid=66" >> $global_config_file 
    echo "Test=66" >> $global_config_file 
#END HB
elif [ "$voice_name" == "slt_arctic_full" ]
then
    echo "QuestionFile=questions-radio_dnn_416.hed" >> $global_config_file
    echo "FileIDList=file_id_list_full.scp" >> $global_config_file
    echo "Train=1000" >> $global_config_file 
    echo "Valid=66" >> $global_config_file 
    echo "Test=66" >> $global_config_file 
else
    echo "The data for voice name ($voice_name) is not available...please use slt_arctic_demo or slt_arctic_full !!"
    exit 1
fi

echo "Merlin default voice settings configured in $global_config_file"
echo "setup done...!"

