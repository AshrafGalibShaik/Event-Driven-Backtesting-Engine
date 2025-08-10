from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11

__version__ = "1.0.0"

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "backtesting_engine",
        [
            "pybind11_wrapper.cpp",
            # Add your main C++ source files here
            # "../backtesting_engine.cpp",  # Uncomment when you split header/source
        ],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_include(),
            # Add path to your C++ headers
            "../",  # For including the main header
        ],
        language='c++',
        cxx_std=14,  # C++14 standard
    ),
]

setup(
    name="backtesting_engine",
    version=__version__,
    author="Ashraf Galib Shaik",
    author_email="ashrafgalibshaik@gmail.com",
    url="https://github.com/AshrafGalibShaik/Event-Driven-Backtesting-Engine",
    description="Event-driven backtesting engine for algorithmic trading",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "pybind11>=2.6.0",
        "numpy>=1.19.0",
        "pandas>=1.3.0",
        "matplotlib>=3.3.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering",
    ],
    keywords="backtesting, trading, finance, algorithmic-trading, quantitative-finance",
)
