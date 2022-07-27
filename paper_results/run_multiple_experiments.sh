#!/bin/sh
#
# This script performs multiple quantitative probing experiments and saves them to pickle files.
#
# It takes two command line arguments:
#  - n_total_experiments: The total number of experiments to be run.
#  - n_experiments per run: The number of experiments to be run in each of the calls to the underlying
#    Python script. Note that this number cannot be higher than 230 due to Java VM restrictions.
#  - seed_shift: Lets us shift the range of seed starting values by a fixed amount for all runs. This
#    is useful if we want to run generate additional data without having to regenerate the old
#    samples.
#
# The results are written to pickle files in the pkl folder and to txt files in the log folder.
# The pickle files can be read in by the qprobing package for evaluation.
# The txt files can be inspected to check the successful completion or to inspect error messages.

# get overall number of experiments
n_total_experiments=$1

# set number of experiments for each run
n_experiments_per_run=$2

# get seed_shift
seed_shift=$3

# get number of runs
n_runs=$((n_total_experiments / n_experiments_per_run))

# create output directory for pkl and log files
date_str=$(date +%d-%m_%H-%M)
info_str="$date_str"__"$n_total_experiments"_runs
pkl_dir=pkl/$info_str
log_dir=log/$info_str
mkdir $pkl_dir
mkdir $log_dir

# run script
for (( i = 0; i < n_runs; i ++ ))
    do
        log_name=$log_dir/$i.txt
        pkl_name=$pkl_dir/$i.pkl
        seed_start_value=$((i * n_experiments_per_run + seed_shift))
        python run_experiment.py $n_experiments_per_run $seed_start_value $pkl_name > $log_name 2>&1
    done

# clean up log files
for expr in "Error in sys.excepthook" "Original exception" "^[[:space:]]*$"
    do
        sed_expr=\/"$expr"\/d
        sed --in-place "$sed_expr" "$log_dir"/*
    done