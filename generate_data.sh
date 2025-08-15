#!/bin/bash

# This is the path where Isaac Sim is installed which contains the python.sh script
ISAAC_SIM_PATH="/home/aisthri/isaac//isaac-sim4.2/isaac-sim-4.2.0/"

## Go to location of the SDG script
cd ../cube_sdg
#SCRIPT_PATH="${PWD}/standalone_palletjack_sdg.py"
SCRIPT_PATH_SDG="${PWD}/cube_sdg.py"
SCRIPT_PATH_JSON="${PWD}/name_json.py"
SCRIPT_PATH_rename="${PWD}/rename.py"


OUTPUT_SDG="${PWD}/data_generated/yellow_sdg"
OUTPUT_SDG2="${PWD}/data_generated/yellow_sdg_part2"
OUTPUT_SDG_test="${PWD}/data_generated/yellow_sdg_test"

OUTPUT_READY="${PWD}/palletjack_data/clean_dataset"


## Go to Isaac Sim location for running with ./python.sh
cd $ISAAC_SIM_PATH

echo "Starting Data Generation"  

#./python.sh $SCRIPT_PATH_SDG --height 720 --width 1280 --num_frames 25000 --distractors additional --data_dir $OUTPUT_SDG
./python.sh $SCRIPT_PATH_SDG --height 720 --width 1280 --num_frames 55000 --distractors additional --data_dir $OUTPUT_SDG2
#./python.sh $SCRIPT_PATH_JSON --data_dir $OUTPUT_SDG 
./python.sh $SCRIPT_PATH_JSON --data_dir $OUTPUT_SDG2
#./python.sh $SCRIPT_PATH_rename --data_dir $OUTPUT_SDG2




