__author__ = 'fcanas'

from distutils.core import setup

setup(
        name='IzVerifier',
        version='0.0.1',
        author='Francisco Canas',
        author_email='mailfrancisco@gmail.com',
        packages=[
            'IzVerifier',
            'IzVerifier.exceptions',
            'IzVerifier.izspecs',
            'IzVerifier.test'
        ],
        data_files=[('data', ['data/sample_installer_iz5'])],
        url='https://github.com/FranciscoCanas/IzVerifier',
        license='LICENSE.txt',
        description='Static Verification for IzPack Specification Files',
        long_description=open('README.md').read(),
        install_requires=[
                "beautifulsoup4 >= 4.3.2"
            ]
        )
