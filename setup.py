"""
Ultra-Fast Scalping Trading System
==================================
Setup script for installation and distribution.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ultra-fast-scalping",
    version="2.0.0",
    author="Ultra-Fast Trading Systems",
    author_email="contact@ultrafasttrading.com",
    description="Institutional-grade cryptocurrency scalping system with nanosecond precision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ultrafasttrading/ultra-fast-scalping",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "gpu": ["torch>=1.9.0", "cupy-cuda11x>=11.0.0"],
        "dev": ["pytest>=6.0", "black>=21.0", "isort>=5.0", "mypy>=0.910"],
        "docs": ["sphinx>=4.0", "sphinx-rtd-theme>=1.0"],
    },
    entry_points={
        "console_scripts": [
            "ultra-scalping=src.core.main_trading_system:main",
            "scalping-benchmark=tests.ultimate_benchmark_suite:main",
            "scalping-demo=examples.optimization_demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md"],
    },
    zip_safe=False,
    keywords="trading, scalping, cryptocurrency, high-frequency, ultra-low-latency, binance",
    project_urls={
        "Bug Reports": "https://github.com/ultrafasttrading/ultra-fast-scalping/issues",
        "Source": "https://github.com/ultrafasttrading/ultra-fast-scalping",
        "Documentation": "https://ultrafasttrading.github.io/ultra-fast-scalping/",
    },
)