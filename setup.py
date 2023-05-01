import os
import sys
import re

from App import __version__ as version

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

SETUP_ARGS = dict(
    name='dstatemachine',
    version=version,
    description=(
        'Innio Myplant Statemachine Fleet Debugger'),
    long_description=long_description,
    url='https://github.com/dieterch/dstatemachine',
    author='Dieter Chvatal',
    author_email='dieter.chvatal@gmail.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: CLI Environment',
        'Intended Audience :: INNIO Engineers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9+',
    ],
    py_modules=['dstatemachine', ],
    install_requires=[
        'arrow>=1.2.3',
        'bokeh==2.4.*',
        'cryptography>=40.0.1',
        'ipyfilechooser>=0.6.0',
        'ipykernel>=6.21.3',
        'ipympl>=0.9.3',
        'ipyregulartable>=0.2.1',
        'ipython>=8.11.0',
        'ipython-genutils>=0.2.0',
        'ipywidgets>=8.0.4',
        'jupyter>=1.0.0',
        'jupyterlab>=3.6.1',
        'jupyterlab-widgets>=3.0.5',
        'matplotlib>=3.7.1',
        'matplotlib-inline>=0.1.6',
        'numpy>=1.24.2',
        'pandas>=1.5.3',
        'pyarrow>=11.0.0',
        'pyotp>=2.8.0',
        'python-dateutil>=2.8.2',
        'PyYAML>=6.0',
        'requests>=2.28.2',
        'scipy>=1.10.1',
        'tables>=3.8.0',
        'tabulate>=0.9.0',
        'tqdm>=4.65.0',
        'voila>=0.4.0',
        'wheel>=0.40.0'
    ],
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
