[![Build Status](https://dev.azure.com/OsramDS/qprobing_github/_apis/build/status/MLResearchAtOSRAM.qprobing?branchName=main)](https://dev.azure.com/OsramDS/qprobing_github/_build/latest?definitionId=44&branchName=main)
![Coverage](https://img.shields.io/azure-devops/coverage/OsramDS/qprobing_github/44)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

## Quantitative Probing in Python
Can we validate the quality of a causal analysis (correctly recovered causal
graph and target causal effect) by checking how many previously
known causal effects could be correctly recovered by the model (hit rate)?
Yes, we can!

<img src="https://github.com/MLResearchAtOSRAM/qprobing/blob/main/paper_results/plots/edge_differences.png?raw=True" width="375"/> <img src="https://github.com/MLResearchAtOSRAM/qprobing/blob/main/paper_results/plots/absolute_effect_differences.png?raw=True" width="375"/>

This is a repository for **quantitative probing**, which is a method of validating
graphical causal models using quantitative domain knowledge.
For more info about the method, check out this
[presentation](https://github.com/MLResearchAtOSRAM/qprobing/blob/main/qprobing_cdsm.pdf)
from
[CDSM22](https://www.causalscience.org/meeting/programme/programme-2022/).

The repo contains two main components:
- The ```qprobing``` package provides methods for a statistical evaluation of the
  effectiveness of different quantitative probing variants.
- The Juypter notebooks ```analysis.ipynb``` and ```connected_analysis.ipynb```,
  together with the ```pkl``` files in this repo, can be used to recreate the
  results of a [related research article](https://arxiv.org/abs/2209.03013).
  They should also be used as a guide for performing your own analyses.


## Installation of the ```qprobing``` package
1. Install ```Python 3.8 or 3.9```. More recent versions should work, too, but the build and
   test pipeline ensures a working state only for these versions. We recommend using a virtual environment for the installation.
2. Install the ```cause2e``` package for causal end-to-end analysis by following
   [these
   instructions](https://github.com/MLResearchAtOSRAM/cause2e#installation).
3. Install ```qprobing``` from source by running
   ```
   pip install https://github.com/MLResearchAtOSRAM/qprobing/archive/main.tar.gz
   ```

If you want to clone the repository into a folder for development on your local machine, please navigate to the folder and run:
```
git clone https://github.com/MLResearchAtOSRAM/qprobing
```

## Citation
If you use the ```qprobing``` package in your work, please cite

```
Daniel Grünbaum (2022). qprobing: A Python package for evaluating the
effectiveness of quantitative probing for causal model validation.
https://github.com/MLResearchAtOSRAM/qprobing
```

and the [related research article](https://arxiv.org/abs/2209.03013).