import re
from pathlib import Path
import sys
import setuptools

long_description = open('README.md', 'r').read()


setuptools.setup(
    name='satsystems',
    version='0.0.1',
    description='satellite bus utilites',
    author='Sean Tedesco',
    author_email='stedesco@live.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'wheel',
        'pyserial',
        'argparse',
    ] + (['picamera'] if sys.platform == 'linux' else []),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts':
            [
                'radio = satsystems.radio.radio:main',
                'gps = satsystems.gps.gps:main',
                'camera = satsystems.camera.camera:main',
                'logger = satsystems.logger.logger:main',
            ],
    },
)
