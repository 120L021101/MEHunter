# MEHunter

## Getting Start
 
<img src="pics/image.png" width="100%" height="auto">

## Abstract
MEHunter is a Natural Language Processing method based on BERT to comprehensively and accurately detect Mobile Element Insertions and Deletions utilizing third-generation sequencing technologies.


## Installation

Follow the steps.

### Step1: install cuteSV(our modified version)
See https://github.com/tjiangHIT/cuteSV for detailed info of cuteSV's installation.

Only made minor changes to cuteSV, so you can just replace the link in the original cuteSV text with: https://github.com/120L021101/cuteSV

``` shell scripts
#For example
#From
git clone https://github.com/tjiangHIT/cuteSV 
#To
git clone https://github.com/120L021101/cuteSV
```

As potential conflicts may occur, please install cuteSV under an independant conda environment, for example, cuteSVenv.

```
conda create -n cuteSVenv python=3.7
conda activate cuteSVenv
```

### Step2: download our deep learning model
You should download our deep learning model from  [this](https://huggingface.co/ATESTACCOUNTFORFIRSTUSE/MEHunter_DL).

Download the model to the folder named "MEHunter_DL"(Customized folder name is OK).

```
MEHunter_DL/
    model/
        pytorch_model.bin
        ...
        ...
    README.md
    model.pth
```

### Step3: install minimap2
See https://github.com/lh3/minimap2

make sure you can successfully run "minimap2 -h"

you may need to add minimap2 to $PATH

```
$ minimap2 -h
Usage: minimap2 [options] <target.fa>|<target.idx> [query.fa] [...]
Options:
  Indexing:
    -H           use homopolymer-compressed k-mer (preferrable for PacBio)
    -k INT       k-mer size (no larger than 28) [15]
    -w INT       minimizer window size [10]
    -I NUM       split index for every ~NUM input bases [4G]
    ....
```
### Step4: install MEHunter framework

download the codes and 'cd' into it.

Then run

``` shell script
conda create -n MEHunterEnv python=3.7
conda activate MEHunterEnv
pip install Cython
pip install .
```

Note That MEHunter/ME_data/ME.fq will be used later(in the usage example)

## Usage

### An example

``` shell script
#################
# SHARED PARAMS #
#################
export BAMPATH=/mnt/mybook/zzj_data2/HG00731/HIFI/pick_me.bam # alignment file, .bam
export REFPATH=/mnt/mybook/Real_data/hg38.fa  # like hs37d5 or hg38, .fa
export CUTESV_WORKDIR=/home/zzj/temp/cuteWork # workdir of cuteSV, any dir is OK, and I personally recommend add "rm -rf $CUTESV_WORKDIR/*" before running.
export CUTESV_OUTPUT=cuteSV_HiFi.vcf # path of cuteSV's final output, in .vcf format, note that it's acutually a path, not the file name.
export PROCESS_NUM=16 # number of mutil-processing


##########################
# CUTESV'S UNIQUE PARAMS #
##########################
export MIN_SUPPORT=6 # minimal number of supporting reads, for detailed info, see original cuteSV doc.
export cuteSVenvName=cuteSVenv # conda enviroment name of cuteSV, mine is cuteSVenv, same as what's mentioned above.

conda activate $cuteSVenvName
cuteSV $BAMPATH $REFPATH $CUTESV_OUTPUT $CUTESV_WORKDIR --genotype \
          -s $MIN_SUPPORT -t $PROCESS_NUM -L 10000 --report_readid --retain_work_dir --diff_ratio_merging_INS 1.1 --diff_ratio_merging_DEL 1.1 --diff_ratio_filtering_TRA 1.1


############################
# MEHunter'S UNIQUE PARAMS #
############################
export MEHUNTER_WORKDIR=/home/zzj/temp/MEHunterWork # workdir of MEHunter, any dir is OK, and I personally recommend add "rm -rf $MEHUNTER_WORKDIR/*" before running as well.
export MEHUNTER_OUTPUT=./MEHunter_HiFi.vcf # path of MEHunter's final output, in .vcf format
export KNOWN_ME_PATH=/home/zzj/temp/MEHunter/ME_data/ME.fq # See MEHunter/ME_data/ME.fq(at your download path), path of known ME sequences, .fq format
export DL_PATH=/home/zzj/MEHunter/src/MEHunter/pre_classifier/model # See step2, path of the downloaded model.
export DEEPLEARNING_BATCHSIZE=32 # batch size of input, it highly affects memory usage, you may have to use another smaller number.
export MEHunterEnvName=MEHunter_T # conda enviroment name of MEHunter

conda activate $MEHunterEnvName
MEHunter $CUTESV_OUTPUT $BAMPATH \
        $CUTESV_WORKDIR $REFPATH $KNOWN_ME_PATH $MEHUNTER_WORKDIR $MEHUNTER_OUTPUT \
        --DL_module $DL_PATH --retain_work_dir -t $PROCESS_NUM --batch_size 32 --MAX_seqs 10


```
Those exported params are essential and/or frequently changed depending on need. Info of other params of cuteSV/MEHunter, see orginal doc and run MEHunter -h respectively.

## Other info
In case someone tries to install MEHunter in many years and needs to install some dependencies that cannot be directly and automatically installed, I here record my conda environment:

``` shell script
# packages in environment at /home/zzj/anaconda3/envs/MEHunter:
#
# Name                    Version                   Build  Channel
_libgcc_mutex             0.1                 conda_forge    conda-forge
_openmp_mutex             4.5                       2_gnu    conda-forge
attrs                     23.2.0                   pypi_0    pypi
badread                   0.4.0                    pypi_0    pypi
biopython                 1.81                     pypi_0    pypi
ca-certificates           2023.11.17           hbcca054_0    conda-forge
certifi                   2023.11.17               pypi_0    pypi
charset-normalizer        3.3.2                    pypi_0    pypi
cigar                     0.1.3                    pypi_0    pypi
cmake                     3.28.1                   pypi_0    pypi
cython                    3.0.7                    pypi_0    pypi
decorator                 5.1.1                    pypi_0    pypi
edlib                     1.3.9                    pypi_0    pypi
einops                    0.6.1                    pypi_0    pypi
fastjsonschema            2.19.1                   pypi_0    pypi
filelock                  3.12.2                   pypi_0    pypi
fsspec                    2023.1.0                 pypi_0    pypi
huggingface-hub           0.16.4                   pypi_0    pypi
idna                      3.6                      pypi_0    pypi
importlib-metadata        6.7.0                    pypi_0    pypi
importlib-resources       5.12.0                   pypi_0    pypi
joblib                    1.3.2                    pypi_0    pypi
jsonschema                4.17.3                   pypi_0    pypi
jupyter-core              4.12.0                   pypi_0    pypi
ld_impl_linux-64          2.40                 h41732ed_0    conda-forge
libffi                    3.4.2                h7f98852_5    conda-forge
libgcc-ng                 13.2.0               h807b86a_3    conda-forge
libgomp                   13.2.0               h807b86a_3    conda-forge
libnsl                    2.0.1                hd590300_0    conda-forge
libsqlite                 3.44.2               h2797004_0    conda-forge
libstdcxx-ng              13.2.0               h7e041cc_3    conda-forge
libzlib                   1.2.13               hd590300_5    conda-forge
mappy                     2.26                     pypi_0    pypi
mehunter                  1.0.0                    pypi_0    pypi
nbformat                  5.8.0                    pypi_0    pypi
ncurses                   6.4                  h59595ed_2    conda-forge
numpy                     1.21.6                   pypi_0    pypi
nvidia-cublas-cu11        11.10.3.66               pypi_0    pypi
nvidia-cuda-nvrtc-cu11    11.7.99                  pypi_0    pypi
nvidia-cuda-runtime-cu11  11.7.99                  pypi_0    pypi
nvidia-cudnn-cu11         8.5.0.96                 pypi_0    pypi
openssl                   3.2.0                hd590300_1    conda-forge
packaging                 23.2                     pypi_0    pypi
pandas                    1.3.5                    pypi_0    pypi
pip                       23.3.2             pyhd8ed1ab_0    conda-forge
pkgutil-resolve-name      1.3.10                   pypi_0    pypi
plac                      1.4.2                    pypi_0    pypi
plotly                    3.10.0                   pypi_0    pypi
pyabpoa                   1.4.3                    pypi_0    pypi
pybedtools                0.9.1                    pypi_0    pypi
pyfaidx                   0.8.0                    pypi_0    pypi
pyfastx                   2.0.2                    pypi_0    pypi
pyrsistent                0.19.3                   pypi_0    pypi
pysam                     0.22.0                   pypi_0    pypi
python                    3.7.12          hf930737_100_cpython    conda-forge
python-dateutil           2.8.2                    pypi_0    pypi
pytz                      2023.3.post1             pypi_0    pypi
pywgsim                   0.5.2                    pypi_0    pypi
pyyaml                    6.0.1                    pypi_0    pypi
readline                  8.2                  h8228510_1    conda-forge
regex                     2023.12.25               pypi_0    pypi
requests                  2.31.0                   pypi_0    pypi
retrying                  1.3.4                    pypi_0    pypi
safetensors               0.4.1                    pypi_0    pypi
scikit-learn              1.0.2                    pypi_0    pypi
scipy                     1.7.3                    pypi_0    pypi
setuptools                68.2.2             pyhd8ed1ab_0    conda-forge
six                       1.16.0                   pypi_0    pypi
sqlite                    3.44.2               h2c6b66d_0    conda-forge
threadpoolctl             3.1.0                    pypi_0    pypi
tk                        8.6.13          noxft_h4845f30_101    conda-forge
tokenizers                0.13.3                   pypi_0    pypi
torch                     1.13.1                   pypi_0    pypi
tqdm                      4.66.1                   pypi_0    pypi
traitlets                 5.9.0                    pypi_0    pypi
transformers              4.29.0                   pypi_0    pypi
typing-extensions         4.7.1                    pypi_0    pypi
urllib3                   2.0.7                    pypi_0    pypi
visor                     1.1                      pypi_0    pypi
wheel                     0.42.0             pyhd8ed1ab_0    conda-forge
xz                        5.2.6                h166bdaf_0    conda-forge
zipp                      3.15.0                   pypi_0    pypi
```

And 120L021101(in the github path) was my student id when I did my bachelor's degree at Harbin Institute of Technology, China. We had a nice course called Software Construction, I learned the design pattern of Java and created this account. That was 2022.