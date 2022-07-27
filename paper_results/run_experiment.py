"""This module is an executable standalone python script for data generation.

The script sets up seeds for DAG generation, CPD generation and simulation (data generation).
Afterwards, the created experiment runner runs a specified number of quantitative probing
experiments. The results are stored in a pickle file whose name contains the date of creation.
There is currently a problem with the Java VM after 231 runs, so it is recommendable to generate
less than 231 samples and restart the process for further samples. The results then have to be
merged for the subsequent analysis.

In order to facilitate using a shell script for running multiple iterations of the script with
shifted seeds, it is possible to pass the number of experiments, the seed starting value and the
name of the directory where the result pickle should be stored as
command line arguments. If you want only one run, you can directly give the number of experiments
and seed starting value in the first lines and call the script without arguments. It can also be
helpful to redirect the print output to a separate text file, in order to avoid having to scroll
through the console output. See the examples below for how to use these options in your command line
calls.

Examples:
python run_experiment.py  # run script with fixed parameters
python run_experiment.py 100 1  # run 100 experiments with seed starting value of 1
python run_experiment.py 100 1 pkl_name  # run with custom parameters and save pickle to custom name
python run_experiment.py > runner_log.txt  # redirect standard output to txt file
python run_experiment.py > runner_log.txt 2>&1 # redirect standard and error output to txt file
"""

import sys
from qprobing.experiment_runner import ExperimentRunner
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) == 1:  # name of script is already one argument
        n_experiments = 2
        start_val = 0
        now = datetime.now()
        dt_string = now.strftime("%d-%m_%H-%M-%S")
        pkl_name = f'pkl/{n_experiments}_runs_{dt_string}.pkl'
        print('Using values from the script:')
    else:
        n_experiments = int(sys.argv[1])
        start_val = int(sys.argv[2])
        pkl_name = sys.argv[3]
        print('Using values from the command line:')
    print(f'{n_experiments} experiments and seed starting value of {start_val}.')
    print('--------------------------')

    runner = ExperimentRunner(data_path='data/dag_data.csv')
    seeds_list = [
        {
            'dag_seed': i + 100,
            'cpd_seed': i,
            'simulation_seed': i,
        }
        for i in range(start_val, n_experiments + start_val)
    ]
    data_generation_specs = {
        'n_vars': 7,
        'n_samples': 1000,
        'p_edge': 0.1,
        'seeds': None,  # data generation seeds are already included in seeds_list
        'show': False,
    }
    task_specs = {
        'p_hint': 0.3,
        'p_probe': 0.5,
        'tolerance': 0.1,
    }
    runner.run_experiments(
        n_experiments,
        data_generation_specs,
        seeds_list,
        task_specs,
    )
    print('--------------------------')
    print(f'Successfully ran {n_experiments} experiments with seed starting value of {start_val}.')
    print('--------------------------')

    runner.save_results(pkl_name)
    print(f'Successfully saved the results to {pkl_name}.')
