from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

print(dir(Extension))

ext_modules=[
    Extension("rMETL2_pyNFA",
        sources=["pyNFA.pyx", "NFA_c.cpp"],
        language = "c++",
    )
]

setup(
    name = "rMETL2_pyNFA",
    ext_modules = cythonize(ext_modules)
)
