#!/bin/bash

if test "$#" -ne 1; then
    echo "Usage: ./scripts/prepare_labels_from_txt.sh conf/global_settings.cfg"
    exit 1
fi

if [ ! -f $1 ]; then
    echo "Global config file doesn't exist"
    exit 1
else
    source $1
fi

### tools required
#FESTDIR=${MerlinDir}/tools/festival
FESTDIR=/home/harald/festival/festival

if [ ! -d "${FESTDIR}" ]; then
    echo "Failed to find $FESTDIR"
    echo "Please configure festival path in scripts/prepare_labels_from_txt_promark.sh !!"
    exit 1
fi

### define few variables here
frontend=${MerlinDir}/misc/scripts/frontend
testDir=experiments/${Voice}/test_synthesis

txt_dir=${testDir}/txt
txt_file=${testDir}/utts.data

### create a scheme file with options from: txt directory or utts.data file

if [ -d "${txt_dir}" ]; then
    if [ ! "$(ls -A ${txt_dir})" ]; then
        echo "Please place your new test sentences (files) in: ${txt_dir} !!"
        exit 1
    else
        #in_txt=${txt_dir}
	#HB to be able to have prom annotation in the txt file, copy it to tmp and remove annotation
        in_txt=${txt_dir}/tmp
	mkdir -p ${in_txt}
	rm ${in_txt}/*
	rm ${testDir}/prompt-utt/*
	for f in ${txt_dir}/*.txt;
	do
	    of=$(basename "$f")
	    outfile=$in_txt/$of
	    echo "$f -> $outfile"
	    cat $f | sed 's/:P[a-z0-9=+%|-]*//g' | sed 's/<[^>]*>//g' | sed 's/  */ /g' > ${outfile}
	done
    fi
elif [ -f "${txt_file}" ]; then
    in_txt=${txt_file}
else
    echo "Please give input: either 1 or 2"
    echo "1. ${txt_dir}  -- a text directory containing text files"
    echo "2. ${txt_file} -- a single text file with each sentence in a new line in festival format"
    exit 1
fi

python ${frontend}/utils/genScmFile.py \
                            ${in_txt} \
                            ${testDir}/prompt-utt \
                            ${testDir}/new_test_sentences.scm \
                            ${testDir}/test_id_list.scp 

### generate utt from scheme file
echo "generating utts from scheme file"
#${FESTDIR}/bin/festival "(lex.select 'unilex-rpx)" -b ${testDir}/new_test_sentences.scm 
${FESTDIR}/bin/festival $FESTDIR/lib/dicts/unilex/unilex-rpx.scm "(lex.select 'unilex-rpx)" -b ${testDir}/new_test_sentences.scm
#${FESTDIR}/bin/festival -b ${testDir}/new_test_sentences.scm 

### convert festival utt to lab
echo "converting festival utts to labels..."
${frontend}/festival_utt_to_lab/make_labels \
                            ${testDir}/prompt-lab \
                            ${testDir}/prompt-utt \
                            ${FESTDIR}/examples/dumpfeats \
                            ${frontend}/festival_utt_to_lab

### normalize lab for merlin with options: state_align or phone_align
echo "normalizing label files for merlin..."
python ${frontend}/utils/normalize_lab_for_merlin.py \
                            ${testDir}/prompt-lab/full \
                            ${testDir}/prompt-lab \
                            ${Labels} \
                            ${testDir}/test_id_list.scp

### remove any un-necessary files
rm -rf ${testDir}/prompt-lab/{full,mono,tmp}


### for promark test:
### If text files are in test_synthesis/txt, look for corresponding .prom files
### in the same directory and add prominence values from them
#echo "adding promark prominence values"
#python scripts/addProminenceValues.py ${testDir}/txt ${testDir}/prompt-lab
#python scripts/addProminenceValues_syll_token-per-line.py ${testDir}/txt ${testDir}/prompt-lab

#HB 180327 
#Moved to merlin_synthesis_promark.sh, because it needs to be done after prom_synth step
#python scripts/addProminenceValues_syll_token-per-line.py ${testDir}/txt ${testDir}/gen_prominence-lab

#status_add_prom=$?
#if [ $status_add_prom -eq 1 ]; then
#    echo "Failed to add prominence!!"
#    exit 1
#fi


#echo "Labels are ready in: ${testDir}/prompt-lab !!"

