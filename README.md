## Quantitative Probing in Python
This is a repository for quantitative probing, which is a method of validating
graphical causal models using quantitative domain knowledge.
It contains two main components:
- The ```qprobing``` package provides methods for a statistical evaluation of the
  effectiveness of different quantitative probing variants.
- The Juypter notebooks ```analysis.ipynb``` and ```connected_analysis.ipynb```,
  together with the ```pkl``` files in this repo, can be used to recreate the
  results of a related research paper. They should also be used as a guide for
  performing your own analyses.


## Installation
1. Install Python 3.8. More recent versions should work, too, but the build and
   test pipeline ensures a working state of the package only for Python 3.8 on
   Windows. We recommend using a virtual environment for the installation.
2. Install the ```cause2e``` package for causal end-to-end analysis by following
   [these
   instructions](https://github.com/MLResearchAtOSRAM/cause2e#installation).
3. Need to figure this out myself first #TODO
   Install the rest of the needed dependencies by running
   ```
   pip install -r requirements.txt
   ```

## Citation
If you use the qprobing package in your work, please cite

Daniel Grünbaum (2022). qprobing: A Python package for evaluating the
effectiveness of quantitative probing for causal model validation. https://github.com/MLResearchAtOSRAM/qprobing