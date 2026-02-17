"""Setup script for MS365SITT"""

from setuptools import setup, find_packages

setup(
    name="ms365sitt",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "msal>=1.20.0",
        "requests>=2.28.0",
        "python-dotenv>=0.19.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "ms365sitt=ms365sitt.cli:main",
        ],
    },
    python_requires=">=3.8",
)
