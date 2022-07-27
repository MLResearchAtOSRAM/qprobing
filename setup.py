import os
from setuptools import setup, find_packages
from qprobing import __name__ as _name, __version__ as _version

# import readme file
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as fp:
    readme = fp.read()

setup(
    name=_name.replace('_', '-'),
    version=_version,
    url="https://github.com/MLResearchAtOSRAM/qprobing",
    description="Quantitative probing for causal model validation",
    keywords="quantitative probing",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        'cause2e>=0.2.1',
        'networkx>=2.8.5',
        'numpy>=1.23.1',
        'pgmpy>=0.1.19',
        'matplotlib>=3.5.2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires=">=3.8",
)
