__author__ = 'fcanas'

from distutils.core import setup

setup(
        name='IzVerifier',
        version='0.0.2',
        author='Francisco Canas',
        author_email='mailfrancisco@gmail.com',
        packages=[
            'IzVerifier',
            'IzVerifier.exceptions',
            'IzVerifier.izspecs',
            'IzVerifier.izspecs.containers',
            'IzVerifier.izspecs.verifiers',
            'IzVerifier.test'
        ],
        url='https://github.com/FranciscoCanas/IzVerifier',
        license='LICENSE.txt',
        description='Static spec file  verification for IzPack installers.',
        long_description=open('README.txt').read(),
        install_requires=[
                "beautifulsoup4 >= 4.3.2"
            ]
        )
