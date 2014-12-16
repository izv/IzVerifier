IzVerifier
==========

Static spec file  verification for IzPack installers.

Purpose
-------

IzVerifier is a tool that tests izpack installers for incorrectly defined or missing specifications. IzVerifier also 
parses the source code of any custom classes used by the installer to ensure that no undefined izpack specifications 
are referenced. Finally, IzVerifier can also perform a graph search of the installers' conditions dependency trees to 
find cycles or missing items. Currently supported speficiation types are conditions, variables, strings, and custom 
classes.

Compatibility
-------------

IzVerifier is a work-in-progress in its early stages, currently compatible with both v4 and v5 Izpack installers. 

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
        'pom': path                         # Path to the installer project's pom.xml file.
        'sources': [path1, path2, ...]      # Path(s) to associated source code roots.
    }

Instantiate the IzVerifier, then call its verification methods:

    >>> from IzVerifier.izverifier import IzVerifier
    >>> izv = IzVerifier(args)
    >>> izv.verify_all(verbosity=1)

IzVerifier methods:

    verify_all(verbosity=0, filter_classes=False):
        Run verification tests on all installer specs.
        Setting filter_classes=true will make IzVerifier filter the results so that only undefined references located in
        source files that were referenced by the specification files or imported explicitly in those files are returned.
        Returns a set of all references that are undefined.

    verify(specification, verbosity=0, filter_classes=False):
        Run verification tests on the given specification.
        Setting filter_classes=true will make IzVerifier filter the results so that only undefined references located in
        source files that were referenced by the specification files or imported explicitly in those files are returned.
        Returns a set of all references for the given spec that are undefined.

    dependency_verification(verbosity=0, filter_classes=False):
        Runs a condition dependencies graph search on all conditions referenced by the specs
        of the installer.
        Setting filter_classes=true will make IzVerifier filter the results so that only undefined references located in
        source files that were referenced by the specification files or imported explicitly in those files are returned.
        Returns a dictionary which maps the condition id to a set of tuples containing paths to missing dependencies.
        The dictionary will be of the form:
        {
            'condition_id1': {
                                ((node1, type),(node2, type)...),
                                ((node1, type),(node2, type)...),
                                ...
                            },
            ...
        }

    get_referenced(specification):
        Returns a mapping for the given specification of all referenced items (defined or undefined) to the files they 
        are referenced in.
        The verify(specification) method must have run prior to calling get_referenced for the mapping to be filled.
        The mapping is in the form:
        {
            'id1': {file1, file2, ...},
            'id2': {filea, fileb, ...},
            ...
        }


IzVerifier is meant to work out of the box for Installers that follow Izpack V5 specification conventions, but its 
classes and containers can be customized for less conventional sets of installation specs. Some use cases:
    
Adding custom methods to IzVerifier's string searches:

    >>> izstrings = izv.get_container('strings')
    >>> izstrings.properties['patterns'].append(('myCustomStringMethod\({0}\)', 'myCustomStringMethod\(({0})\)'))
    >>> izv.verify('strings', verbosity=2)
   
Specifying custom paths to specification files, resource files, or langpacks:
 
    >>> izv = IzVerifier(args)
    >>> izv.paths.langpacks['eng.xml'] = 'path/to/eng.xml'
    >>> izv.verify('strings')


Contributing
------------

Setting up to hack on IzVerifier is fairly simple:

 + Fork your own copy of the repo, then clone it locally.
 + From the root of the IzVerifier repo, pip install the project as an "editable":


    $ pip install -e .

 Now importing and calling IzVerifier as in the Usage guide above will use the version in your repo, so you can modify 
 and immediately see the changes in your code without re-installing or upgrading the package.
 
 Pull requests for tests, improvements, and documentation are welcome.