IzVerifier
==========

Static spec file  verification for IzPack installers.

Purpose
-------

IzVerifier is a tool that tests izpack installers for incorrectly defined or undefined conditions, variables, and strings. IzVerifier also parses the source code of any custom classes used by the installer to ensure that no undefined izpack specs are referenced. Finally, IzVerifier can also perform a graph search of the installers' conditions dependency trees to find cycles or missing items.

Compatibility
-------------

IzVerifier is a work-in-progress in its early stages, and currently compatible only with izpack v5 installers.

Installation
------------

Use pip to install:

    $ pip install IzVerifier

Usage
-----

IzVerifier takes a dictionary of arguments in the following form:

    args = {
        'specs_path': path                  # Path to specs folder for installer.
        'resources_path': path              # Path to root resources folder for installer.
        'sources': [path1, path2, ...]      # Path(s) to associated source code roots.
    }

Instantiate the IzVerifier, then call its verification methods:

    >>> from IzVerifier.izverifier import IzVerifier
    >>> izv = IzVerifier(args)
    >>> izv.verify_all(verbosity=1)

Available methods include:

    verify_all(verbosity=0):
        Run verification tests on all installer specs.
        Returns a set of all references that are undefined.

    verify(specification, verbosity=0):
        Run verification tests on the given specification.
        Returns a set of all references for the given spec that are undefined.

    dependency_verification(izv):
        Runs a condition dependencies graph search on all conditions referenced by the specs
        of the installer contained by izv, an instance of IzVerifier.




