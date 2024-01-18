# MEHunter

## Abstract
MEHunter is a Natural Language Processing method based on BERT to comprehensively and accuratly detect Mobile Element Insertions and Deletions utilizing third-generation sequencing technologies.

## Installation

To install MEHunter, run:

``` shell script
conda create -n MEHunterEnv python=3.7
conda activate MEHunterEnv
pip install .
```

## Usage

``` shell script
usage: MEHunter [-h] [--version] [-t THREADS] [--retain_work_dir]
                [--batch_size BATCH_SIZE]
                [VCF] [BAM] cuteSV_workdir reference known_ME work_dir output
```