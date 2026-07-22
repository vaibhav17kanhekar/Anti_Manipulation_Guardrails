"""
Setup script for Anti-Manipulation Guardrails project
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="anti-manipulation-guardrails",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@university.ac.uk",
    description="Testing defensive prompt engineering against emotional manipulation of LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/anti-manipulation-guardrails",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "ipywidgets>=8.0.0",
        ],
        "analysis": [
            "seaborn>=0.12.0",
            "plotly>=5.0.0",
            "scikit-learn>=1.3.0",
            "statsmodels>=0.14.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "amg-run=run_experiment:main",
            "amg-analyze=src.analysis.cli:main",
        ],
    },
    package_data={
        "anti_manipulation_guardrails": [
            "config/*.yaml",
            "data/raw/*.json",
        ],
    },
    include_package_data=True,
)