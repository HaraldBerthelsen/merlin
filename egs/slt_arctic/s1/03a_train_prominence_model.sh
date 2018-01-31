#!/bin/bash -e

global_config_file=conf/global_settings.cfg
source $global_config_file

if test "$#" -ne 1; then
    echo "################################"
    echo "Usage:"
    echo "./03a_train_prominence_model.sh <path_to__conf_file>"
    echo ""
    echo "Default path to prominence conf file: conf/prominence_${Voice}.conf"
    echo "################################"
    exit 1
fi

prominence_conf_file=$1

### Step 3: train prominence model ###
echo "Step 3:"
echo "training prominence model..."

./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $prominence_conf_file
