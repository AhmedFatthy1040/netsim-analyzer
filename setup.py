from setuptools import setup, find_packages

setup(
    name="netsim-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'networkx>=2.8.0',
        'scapy>=2.5.0',
        'PyYAML>=6.0',
        'click>=8.0.0',
        'matplotlib>=3.5.0',
    ],
    author="Ahmed Fatthy",
    description="A network simulation tool for analyzing BGP and OSPF protocols",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
    ],
)