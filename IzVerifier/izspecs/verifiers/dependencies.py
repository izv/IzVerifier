from IzVerifier.logging.reporter import display_paths
__author__ = 'fcanas'

invalid_paths = []

def test_verify_all_dependencies(verifier, verbosity=0, fail_on_undefined_vars=False):
    """
    For the given installer conditions, verify the dependencies for every single one of the conditions
    that are in some way referenced in specs or source.
    """
    global invalid_paths
    invalid_paths = []

    crefs = set([ref[0] for ref in verifier.find_code_references('conditions')])
    srefs = set([ref[0] for ref in verifier.find_spec_references('conditions')])

    conditions = verifier.get_container('conditions')
    variables = verifier.get_container('variables')

    drefs = set(conditions.container.keys())

    invalids = depth_first_search(crefs | srefs | drefs, conditions, variables, fail_on_undefined_vars)
    if verbosity > 0:
        display_paths(invalids)

    return invalids


def depth_first_search(references, conditions, variables, fail_on_vars):
    """
    Performs a depth first search of the conditions dependency tree.
    :return: A set of paths leading to undefined condition dependendcies.
    """
    verified = {}

    for condition_id in references:
        path = ((condition_id, 'condition'),)
        _visit_node(condition_id, conditions, variables, verified, path, fail_on_vars)

    return invalid_paths


def _visit_node(cid, conditions, variables, verified, path, fov):
    """
    Visits a single node in the conditions dependency tree.
    """

    # default case: a validly defined condition
    verified[cid] = True

    if not cid in conditions.container:
        verified[cid] = False
        invalid_paths.append(path)
        return False

    condition = conditions.container[cid]
    ctype = condition['type']

    if 'variable' in ctype:
        var = str(condition.find('name').text)
        tup = (var, 'variable')
        path += (tup,)
        if not var in variables.get_keys() and fov:
            verified[cid] = False
            invalid_paths.append(path)
        else:
            verified[cid] = True
        return verified[cid]

    if 'exists' in ctype:
        var = str(condition.find('variable').text)
        tup = (var, 'variable')
        path += (tup,)
        if not var in variables.get_keys():
            verified[cid] = False
            invalid_paths.append(path)
        else:
            verified[cid] = True
        return verified[cid]

    elif 'and' in ctype or 'or' in ctype or 'not' in ctype:
        dependencies = condition.find_all('condition')
        for dep in dependencies:
            did = str(dep['refid'])
            new_path = path + ((did, 'condition'),)
            if not _visit_node(did, conditions, variables, verified, new_path, fov):
                verified[cid] = False

    return verified[cid]