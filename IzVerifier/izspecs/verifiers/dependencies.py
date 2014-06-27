__author__ = 'fcanas'
from IzVerifier.izspecs.containers.constants import *


def test_verify_all_dependencies(verifier):
    """
    For the given installer conditions, verify the dependencies for every single one of the conditions
    that are in some way referenced in specs or source.
    """

    return_value = 0

    crefs = verifier.find_code_references('conditions')
    srefs = verifier.find_spec_references('conditions')

    conditions = verifier.get_container('conditions')
    variables = verifier.get_container('variables')
    drefs = conditions.get_keys()


    for condition in drefs | srefs | crefs:

        result = verify_dependencies(condition, conditions, variables)
        fail = True
        if result:
            last_path = list(result)[-1]
            if 'variable' in last_path[-1]:
                fail = False # indicates undefined variable, so we return a warning
            else:
                return_value += 1 # indicates an undefined condition, so we fail

        if result: display_paths(result)
    return return_value



def test_verify_dependencies(id, conditions, variables):
    """
    Verifies that the given condition id is defined, and that its' dependencies and
    their transitive dependencies are all defined and valid.
    """
    result = 0

    if not id in conditions.get_keys():
        return 1
    else:
        result = verify_dependencies(id, conditions, variables)
    return result


def verify_dependencies(id, conditions, variables):
    """
    Performs a breadth-first search of a condition's dependencies in order
    to verify that all dependencies and transitive dependencies are defined
    and valid.
    """
    result = _verify_dependencies(id, conditions, variables, set(), tuple())
    return result


def _verify_dependencies(id, conditions, variables, undefined_paths, current_path):
    """
    Given the soup for a condition, test that its dependencies are validly
    defined.
    """
    tup = (id, 'condition')
    current_path += (tup,)

    # Exception for izpack conditions:
    if id in conditions.properties[WHITE_LIST]:
        return undefined_paths

    if not id in conditions.get_keys():
        undefined_paths.add(current_path)
        return undefined_paths

    condition = conditions.container[id]
    condition_type = condition['type']

    if 'variable' in condition_type:
        var = str(condition.find('name').text)
        tup = (var, 'variable')
        if not var in variables.get_keys():
            current_path += (tup,)
            undefined_paths.add(current_path)
        return undefined_paths

    if 'exists' in condition_type:
        var = str(condition.find('variable').text)
        tup = (var, 'variable')
        if not var in variables.get_keys():
            current_path += (tup,)
            undefined_paths.add(current_path)
        return undefined_paths

    elif 'and' in condition_type or 'or' in condition_type or 'not' in condition_type:
        dependencies = condition.find_all('condition')
        for dep in dependencies:
            did = str(dep['refid'])
            tup = (did, 'condition')
            if tup in current_path:
                current_path += (tup,)
                display_paths(set([current_path]))
                continue

            _verify_dependencies(did, conditions, variables, undefined_paths, current_path)
    return undefined_paths


def display_paths(paths):
    """
    Human readable output for displaying dependency paths.
    """
    def node_printer(node):
        return str(node[0]) + "(" + node[1] + ")"

    for path in paths:
        tab = 0
        for node in path:
            if type(node[0]) is tuple:
                id = node[0][0]
            else:
                id = node[0]

            if tab:
                branch = u'\u02ea\u2192 '
            else:
                branch = ''
            tab += 3

            print " " * tab + branch + str(id) + " : (" + str(node[1]) + ")"
    print

