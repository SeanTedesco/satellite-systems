import re
from pathlib import Path
import sys
import setuptools
from setuptools.command.develop import develop

long_description = open('README.md', 'r').read()

"""
data_files = [
    ('extra/common', ['extra/common/labscripts.yaml']),
    ('schemas/common', ['schemas/common/conffile.yaml']),
    ('schemas/thermal', [
            'schemas/thermal/profile.yaml',
            'schemas/thermal/configuration.yaml',
            'schemas/thermal/configuration_tcycle.yaml',
        ],
    ),
]


class devel(develop):

    def run(self):
        develop.run(self)
        for elt in data_files:
            dest_dir = Path(sys.exec_prefix) / Path(elt[0])
            self.announce(f'Creating {dest_dir}')
            dest_dir.mkdir(parents=True, exist_ok=True)
            for file in elt[1]:
                source = Path(file)
                dest = dest_dir / source.name

                if dest.exists():
                    dest.unlink()
                self.announce(f'Linking {dest} -> {source.resolve()}')
                dest.symlink_to(source.resolve())
"""

setuptools.setup(
    name='labscripts',
    version='0.0.1',
    description='XSC lab utilies',
    author='Laurier Loiselle',
    author_email='lal@xiphos.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'pyvisa',
        'pyvisa-py',
        'pyserial',
        'pyusb',
        'grabserial @ git+https://github.com/tbird20d/grabserial@master#egg=grabserial',
        'chamberconnectlibrary @ git+https://github.com/liambeguin/chamberconnectlibrary@python3-support#egg=chamberconnectlibrary',
        'uldaq',
        'pandas',
        'matplotlib',
        'jsonschema',
        'ruamel.yaml',
        'influxdb-client',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts':
            [
                'hw-checkout = labscripts.multimeter.hw_checkout:main',
                'tc-cli = labscripts.thermal:main',
                'tc-plot = labscripts.thermal:plotter',
                'log-daq-regulators = labscripts.daq.log_regulators:main',
                'powersupply = labscripts.powersupply:main',
                'daq-relays = labscripts.relays:main',
                'waveform-generator = labscripts.waveform:main',
                'log-pt100 = labscripts.multimeter.log_pt100:main',
                'hw-load = labscripts.load:main',
                'calibrator = labscripts.calibrator:main',
                'cl-sim = labscripts.cameralink:main',
                'decade = labscripts.decade:main',
            ],
    },
    cmdclass={'develop': devel},
    data_files=data_files,
)
