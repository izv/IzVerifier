from IzVerifier.logging.reporter import display_paths
from IzVerifier.izspecs.containers.constants import *

__author__ = 'fcanas'


def depth_first_search(conditions, variables):
    """
    Performs a depth first search of the conditions dependency tree.
    :return: A set of paths leading to undefined condition dependendcies.
    """
    visited = {}
    stack = []
    undefined_paths = []

    for condition_id in conditions.get_keys():
        stack.append(condition_id)

        while stack:
            id = stack.pop()
            undefined_paths = visit_node(id, conditions, variables, stack, visited, undefined_paths, set())
    return undefined_paths


def visit_node(id, conditions, variables, stack, visited, undefined_paths, path):
    """
    Visits a single node.
    """
    if id in visited.keys():
        if visited[id] == 1:
            return undefined_paths
        else:
            undefined_paths.add(path)
            return undefined_paths

    if not conditions.container.has_key(id):
        visited[id] = 0
        undefined_paths.add(path)
        return undefined_paths

    condition = conditions.container[id]
    type = condition['type']

    if 'variable' in type:
        var = str(condition.find('name').text)
        tup = (var, 'variable')
        if not var in variables.get_keys():
            path += (tup,)
            visited[id] = 0
            undefined_paths.add(path)
        else:
            visited[id] = 1
        return undefined_paths

    if 'exists' in type:
        var = str(condition.find('variable').text)
        tup = (var, 'variable')
        if not var in variables.get_keys():
            path += (tup,)
            visited[id] = 0
            undefined_paths.add(path)
        else:
            visited[id] = 1
        return undefined_paths

    elif 'and' in type or 'or' in type or 'not' in type:
        dependencies = condition.find_all('condition')
        for dep in dependencies:
            did = str(dep['refid'])
            tup = (did, 'condition')
            if tup in path:
                path += (tup,)
                display_paths(set([path])) # cycle?
            else:
                stack.append(did)



def test_verify_all_dependencies(verifier, verbosity=0, fail_on_undefined_vars=False):
    """
    For the given installer conditions, verify the dependencies for every single one of the conditions
    that are in some way referenced in specs or source.
    """

    return_value = 0

    crefs = set([ref[0] for ref in verifier.find_code_references('conditions')])
    srefs = set([ref[0] for ref in verifier.find_spec_references('conditions')])

    conditions = verifier.get_container('conditions')
    variables = verifier.get_container('variables')
    drefs = conditions.get_keys()


    for condition in drefs | srefs | crefs:
        result = verify_dependencies(condition, conditions, variables)
        fail = True
        if result:
            last_path = list(result)[-1]
            if 'variable' in last_path[-1]:
                fail = fail_on_undefined_vars
            else:
                return_value += 1 # indicates an undefined condition, so we fail
            if fail and verbosity > 0:
                display_paths(result)
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

    ids = conditions.get_keys()

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




