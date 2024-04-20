# coding=utf-8


from setuptools import find_packages

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize



LONG_DESCRIPTION = '''Mobile element insertion (MEI) is a major category of structure variations (SVs). \
The rapid development of long read sequencing provides the opportunity to sensitively discover MEIs. \
However, the signals of MEIs implied by noisy long reads are highly complex, due to the repetitiveness \
of mobile elements as well as the serious sequencing errors. Herein, we propose Realignment-based \
Mobile Element insertion detection Tool for Long read (rMETL). rMETL takes advantage of \
its novel chimeric read re-alignment approach to well handle complex MEI signals. \
Benchmarking results on simulated and real datasets demonstrated that rMETL has the ability \
to more sensitivity discover MEIs as well as prevent false positives. \
It is suited to produce high quality MEI callsets in many genomics studies.'''


ext_modules=[
    Extension("MEHunter_pyNFA",
        sources=["./src/MEHunter/Aligner/pyNFA.pyx", "./src/MEHunter/Aligner/NFA_c.cpp"],
        language = "c++",
        extra_compile_args=['-O2', '--std=c++11']
    )
]

setup(
    name = "MEHunter",
    version = "1.0.0",
    description = "deep learning and re-alignment based MEI/MED detection tool for long reads",
    author = "Zhou Zuji",
    author_email = "hitzzj@outlook.com",
    url = "https://github.com/120L021101/MEHunter",
    license = "MIT",
    packages = find_packages("src"),
    package_dir = {"": "src"},
    data_files = [("", ["LICENSE"])],
    scripts=['src/MEHunter/MEHunter'],
    long_description = LONG_DESCRIPTION,
    zip_safe = False,
    install_requires = ['pysam', 'Biopython', 'Cigar'],
    ext_modules = cythonize(ext_modules)
)
