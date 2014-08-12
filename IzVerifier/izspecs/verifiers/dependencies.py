from IzVerifier.izspecs.containers.constants import *

__author__ = 'fcanas'


def test_verify_all_dependencies(verifier, fail_on_undefined_vars=False):
    """
    For the given installer conditions, verify the dependencies for every single one of the conditions
    that are in some way referenced in specs or source.
    """

    crefs = set([ref[0] for ref in verifier.find_code_references('conditions')])
    srefs = set([ref[0] for ref in verifier.find_specification_references('conditions')])

    conditions = verifier.get_container('conditions')
    variables = verifier.get_container('variables')
    drefs = conditions.get_keys()

    result_dict = dict()
    for condition in drefs | srefs | crefs:
        result = verify_dependencies(condition, conditions, variables)
        fail = True
        if result:
            last_path = list(result)[-1]
            if 'variable' in last_path[-1]:
                fail = fail_on_undefined_vars
            if fail:
                result_dict[condition] = result

    return result_dict


def test_verify_dependencies(cond_id, conditions, variables):
    """
    Verifies that the given condition id is defined, and that its' dependencies and
    their transitive dependencies are all defined and valid.
    """

    if not cond_id in conditions.get_keys():
        return 1
    else:
        result = verify_dependencies(cond_id, conditions, variables)
    return result


def verify_dependencies(cond_id, conditions, variables):
    """
    Performs a breadth-first search of a condition's dependencies in order
    to verify that all dependencies and transitive dependencies are defined
    and valid.
    """
    result = _verify_dependencies(cond_id, conditions, variables, set(), tuple())
    return result


def _verify_dependencies(cond_id, conditions, variables, undefined_paths, current_path):
    """
    Given the soup for a condition, test that its dependencies are validly
    defined.
    """
    tup = (cond_id, 'condition')
    current_path += (tup,)

    # Exception for izpack conditions:
    if cond_id in conditions.properties[WHITE_LIST]:
        return undefined_paths

    if not cond_id in conditions.get_keys():
        undefined_paths.add(current_path)
        return undefined_paths

    condition = conditions.container[cond_id]
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
                current_path += ((did,'cycle'),)
                return undefined_paths.add(current_path)

            _verify_dependencies(did, conditions, variables, undefined_paths, current_path)
    return undefined_paths




