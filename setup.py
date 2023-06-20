from setuptools import setup

setup(
    name='nessupdate',
    version='1',
    description='A utility to update a Nessus installation',
    author='James Conlan',
    url='https://github.com/JamesConlan96/Nessupdate',
    license='GPL-3.0',
    py_modules=[
        'nessupdate'
    ],
    python_requires='>=3.0.0',
    entry_points={
        'console_scripts': [
            'nessupdate = nessupdate:main'
        ]
    }
)