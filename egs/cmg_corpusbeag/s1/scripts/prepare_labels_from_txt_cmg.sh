#!/bin/bash -e

if test "$#" -lt 3; then
    echo "Usage: ./scripts/prepare_labels_from_txt.sh <path_to_text_dir> <path_to_lab_dir> <path_to_global_conf_file>"
    exit 1
fi

### arguments
inp_txt=$1
lab_dir=$2
global_config_file=$3

if [ ! -f $global_config_file ]; then
    echo "Global config file doesn't exist"
    exit 1
else
    source $global_config_file
fi

if test "$#" -eq 3; then
    train=false
else
    train=$4
fi

### tools required
#if [ ! -d "${FESTDIR}" ]; then
#    echo "Please configure festival path in $global_config_file !!"
#    exit 1
#fi

### define few variables here
frontend=${MerlinDir}/misc/scripts/frontend
out_dir=$lab_dir

if [ "$train" = true ]; then
    file_id_scp=file_id_list.scp
    #    scheme_file=train_sentences.scm
else
    file_id_scp=test_id_list.scp
    #    scheme_file=new_test_sentences.scm
fi


#Generate xml files using Abair
echo "Generating abair xml .."
python scripts/genAbairXmlFiles.py $inp_txt ${out_dir}/$file_id_scp ${out_dir}/abair_xml

#convert to htslabel
if [ ! -e ${out_dir}/prompt-lab/full ]; then
    mkdir -p ${out_dir}/prompt-lab/full
fi

echo "Converting to hts lab format .."
python ~/svn/Software/Abair/scripts/convertFiles.py htslabel_data ${out_dir}/prompt-lab/full ${out_dir}/abair_xml/*.xml

echo "Adding dummy durations .."
python scripts/addDummyDurations.py ${out_dir}/prompt-lab/full


### normalize lab for merlin with options: state_align or phone_align
echo "normalizing label files for merlin..."
if [ "$train" = true ]; then
    python ${frontend}/utils/normalize_lab_for_merlin.py \
	   ${out_dir}/prompt-lab/full \
	   ${out_dir}/label_no_align \
	   phone_align \
	   ${out_dir}/$file_id_scp 0
    ### remove any un-necessary files
    rm -rf ${out_dir}/prompt-lab
else
    python ${frontend}/utils/normalize_lab_for_merlin.py \
	   ${out_dir}/prompt-lab/full \
	   ${out_dir}/prompt-lab \
	   ${Labels} \
	   ${out_dir}/$file_id_scp 0
    ### remove any un-necessary files
    #rm -rf ${out_dir}/prompt-lab/{full,mono,tmp}

    echo "Labels are ready in: ${out_dir}/prompt-lab !!"
fi


