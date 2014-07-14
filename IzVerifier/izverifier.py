import importlib
from IzVerifier.izspecs.containers.izclasses import IzClasses

from IzVerifier.izspecs.izproperties import IzProperties
from IzVerifier.izspecs.verifiers.dependencies import test_verify_all_dependencies
from IzVerifier.izspecs.verifiers.seeker import Seeker
from IzVerifier.izspecs.containers.constants import *
from IzVerifier.exceptions.IzVerifierException import IzArgumentsException
from IzVerifier.izspecs.izpaths import IzPaths
from IzVerifier.logging.reporter import Reporter


__author__ = 'fcanas'


class IzVerifier():
    """
    Responsible for parsing an IzPack installer's spec files and any user-specified source code,
    and finding inconsistencies with izpack's conditions, variables, strings, process panel jobs,
    etc.
    """

    def __init__(self, args):
        """
        Main entry point for IzVerifier. Args is a dictionary in this form:

        args = {
            'specs_path': path                  # Path to specs folder for installer.
            'resources_path': path              # Path to root resources folder for installer.
            'pom': path                         # Path to pom file, if used for properties.
            'sources': [path1, path2, ...]      # Path(s) to associated source code roots.
        }
        """
        validate_arguments(args)
        self.reporter = Reporter()
        self.specifications = ['conditions', 'variables', 'strings']
        self.containers = {}
        self.sources = args.get('sources', [])

        if args.has_key('pom'):
            self.properties = IzProperties(args['pom'])
        else:
            self.properties = None
        self.paths = IzPaths(args['specs_path'], args['resources_path'], self.properties)
        self.fill_classes()
        self.seeker = Seeker(self.paths)

    def verify_all(self, verbosity=0):
        """
        Runs a verification for all specs.
        """
        missing = set([])

        for specification in self.specifications:
            missing |= self.verify(specification, verbosity)
        return missing


    def verify(self, specification, verbosity=0):
        """
        Runs a verification on the given izpack spec: conditions, strings, variables, etc.
        """

        container = self.get_container(specification)
        defined = container.get_keys()
        crefs = self.find_code_references(specification)
        srefs = self.find_spec_references(specification)

        cmissing = undefined(defined, crefs)
        smissing = undefined(defined, srefs)

        if verbosity > 0:
            self.reporter.report_test('unreferenced {0} in code'.format(specification), cmissing)
            self.reporter.report_test('unreferenced {0} in specs'.format(specification), smissing)

        return cmissing | smissing

    def get_container(self, specification):
        """
        Returns an izpack item container filled with specs gathered from the installer
        specified in the constructor.
        """
        if not self.containers.has_key(specification):
            return self.init_container(specification)
        else:
            return self.containers[specification]

    def init_container(self, specification):
        """
        Initialize a container to be used for verification.
        """
        module = importlib.import_module("IzVerifier.izspecs.containers.iz" + specification)
        class_ = getattr(module, 'Iz' + specification.title())
        instance = class_(self.paths.get_path(specification))
        self.containers[specification] = instance
        return instance

    def find_code_references(self, specification):
        """
        Find all source code references for specs in each container.
        :param specifications: conditions, variables, strings, or other izpack spec
        """
        container = self.get_container(specification)
        hits = self.seeker.find_references_in_source(patterns=container.properties[PATTERNS],
                                                     path_list=self.sources,
                                                     white_list_patterns=container.properties[WHITE_LIST_PATTERNS])

        return hits

    def find_spec_references(self, specification):
        """
        Find all specification xml references for specs in each container.
        :param installer:
        :param specifications:
        """
        container = self.get_container(specification)

        args = {
             'specs': map(self.paths.get_path, container.properties[REFERENCE_SPEC_FILES]),
             'filter_fn': container.has_reference,
             'attributes': container.properties[ATTRIBUTES],
             'transform_fn': container.ref_transformer,
             'white_list_patterns': container.properties[WHITE_LIST_PATTERNS]
        }
        hits = self.seeker.search_specs_for_attributes(args)
        return hits

    def dependency_verification(self, verbosity=0, fail_on_undefined_vars=False):
        """
        Run a conditions dependency graph search.
        """
        results = test_verify_all_dependencies(self, verbosity, fail_on_undefined_vars=fail_on_undefined_vars)
        return results

    def find_references(self, rid, specs=None, verbosity=0):
        """
        Finds all references to the given id in source code and specs file for any of the given specs.
        """
        results = set()

        if not specs:
            specs = self.specifications

        for spec in specs:
            results |= self.find_reference(spec, rid, verbosity)

        return results

    def find_reference(self, spec, rid, verbosity=0):
        """
        Find all references to the given id in source and specs for the given spec.
        Returns a set of tuple results.
        """
        container = self.get_container(spec)

        props = {
            'path': self.paths.root,
            'id': rid,
            'specs': map(self.paths.get_path, container.properties[REFERENCE_SPEC_FILES]),
            'filter_fn': container.has_reference,
            'attributes': container.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': container.properties[PATTERNS],
            'source_paths': self.sources,
            'white_list_patterns': container.properties[WHITE_LIST_PATTERNS]
        }
        results = self.seeker.find_id_references(props)
        if verbosity > 0:
            self.reporter.report_test('references to {0} in {1}'.format(rid, spec), results)
        return results

    def fill_classes(self):
        """
        Fills a 'classes container' with custom class info from source code paths.
        """
        container = IzClasses()

        for path in self.sources:
            container.parse(path)
        self.containers['classes'] = container


def validate_arguments(args):
    """
    Throws exceptions if required args are missing or invalid.
    """
    if not args.has_key('specs_path'):
        raise IzArgumentsException("No Path to Installer Specs Specified")
        exit(1)
    if not args.has_key('resources_path'):
        raise IzArgumentsException("No Path to Installer Resources Specified")
        exit(1)


def undefined(key_set, tup_set):
    """
    Returns the subset of keys from tup_set not present in key_set.
    key_set is a simple set of string keys.
    up_set is a set of tuples: tup[0] is the key of that tuple.
    """
    return set([tup for tup in tup_set if not quote_remover(tup[0]) in key_set])


def unused(key_set, tup_set):
    """
    Returns the subset of key_set not present in tup_set.
    key_set is a simple set of string keys.
    up_set is a set of tuples: tup[0] is the key of that tuple.
    """
    if not tup_set:
        return key_set
    return set([key for key in key_set if not key in zip(*tup_set)[0]])


def quote_remover(key):
    """
    Extracts the actual key of the item passed in.
    TODO: seriously do this minus recursion, idiot.
    """
    if key.startswith('"') and key.endswith('"'):
        return key[1:-1]
    if '=' in key:
        key = quote_remover(''.join(key.split('=')[1:]))
    return key

