import importlib
from IzVerifier.izspecs.verifiers.dependencies import test_verify_all_dependencies
from IzVerifier.izspecs.verifiers.seeker import Seeker
from IzVerifier.izspecs.izproperties import *
from IzVerifier.exceptions.IzVerifierException import IzArgumentsException
from IzVerifier.izspecs.izpaths import IzPaths

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
            'sources': [path1, path2, ...]      # Path(s) to associated source code roots.
        }
        """
        validate_arguments(args)
        self.specifications = ['conditions', 'variables', 'strings']
        self.containers = {}
        self.installer = args.get('installer')
        self.sources = args.get('sources', [])
        self.paths = IzPaths(args['specs_path'], args['resources_path'])
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

        if verbosity > 0:
            report_set(cmissing)

        smissing = undefined(defined, srefs)

        if verbosity > 0:
            report_set(smissing)

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
             'path': self.paths.root,
             'specs': container.properties[REFERENCE_SPEC_FILES],
             'filter_fn': container.has_reference,
             'attributes': container.properties[ATTRIBUTES],
             'transform_fn': container.ref_transformer
        }
        hits = self.seeker.search_specs_for_attributes(args)
        return hits

    def dependency_verification(self):
        """
        Run a conditions dependency graph search.
        """
        test_verify_all_dependencies(self)

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

def report_set(entities):
    """ Human-readable report for a set of unverified entities. """
    template = ' [ {0:.<40}{1:.>40} ] '
    template1 = ' [ {0:.<80} ] '

    for item in sorted(entities):
        if type(item) is tuple:
            print template.format(item[0], item[1])
        else:
            print template1.format(item)

