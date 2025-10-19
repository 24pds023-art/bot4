#!/usr/bin/env python3
"""
Setup script for Ultra-Fast Scalping Trading System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "docs" / "README.md").read_text()

# Read requirements
requirements = []
try:
    with open('requirements.txt', 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = [
        'aiohttp>=3.8.0',
        'websockets>=11.0.0',
        'python-dotenv>=1.0.0',
        'pyyaml>=6.0.0',
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'scikit-learn>=1.0.0'
    ]

setup(
    name="ultra-fast-scalping-system",
    version="2.0.0",
    author="Ultra-Fast Trading Systems",
    author_email="contact@ultrafast-trading.com",
    description="Professional-grade cryptocurrency scalping system with institutional optimizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ultrafast-trading/scalping-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'gpu': ['cupy-cuda11x>=10.0.0'],
        'ml': ['tensorflow>=2.8.0', 'torch>=1.11.0'],
        'dev': ['pytest>=7.0.0', 'black>=22.0.0', 'flake8>=4.0.0'],
        'full': ['cupy-cuda11x>=10.0.0', 'tensorflow>=2.8.0', 'torch>=1.11.0']
    },
    entry_points={
        'console_scripts': [
            'ultra-scalping=main:main',
            'scalping-trade=main:main',
            'scalping-monitor=examples.monitor_only:main',
            'scalping-test=scripts.check_system:main',
        ],
    },
    include_package_data=True,
    package_data={
        'config': ['*.yaml', '*.yml'],
        'docs': ['*.md'],
        'examples': ['*.py'],
    },
    project_urls={
        "Bug Reports": "https://github.com/ultrafast-trading/scalping-system/issues",
        "Source": "https://github.com/ultrafast-trading/scalping-system",
        "Documentation": "https://github.com/ultrafast-trading/scalping-system/docs",
    },
    keywords="trading, scalping, cryptocurrency, binance, algorithmic-trading, high-frequency-trading",
    zip_safe=False,
)