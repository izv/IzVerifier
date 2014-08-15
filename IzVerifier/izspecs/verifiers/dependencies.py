from IzVerifier.izspecs.containers.constants import *

__author__ = 'fcanas'


class ConditionDependencyGraph():
    compound_conditions = ['or', 'xor', 'and', 'not']

    def __init__(self, verifier, fail_on_undefined_vars=False):
        self.ill_defined = {}
        self.well_defined = set()
        self.crefs = set((ref[0] for ref in verifier.find_code_references('conditions')))
        self.srefs = set((ref[0] for ref in verifier.find_specification_references('conditions')))
        self.conditions = verifier.get_container('conditions')
        self.variables = verifier.get_container('variables')
        self.drefs = self.conditions.get_keys()
        self.fail_on_undefined_vars = fail_on_undefined_vars

    def all_references(self):
        return self.drefs | self.srefs | self.crefs

    def test_verify_all_dependencies(self):
        """
        For the given installer conditions, verify the dependencies for every single one of the conditions
        that are in some way referenced in specs or source.
        """

        for condition in self.all_references():
            result = self.verify_dependencies(condition)

            if result:
                self.ill_defined[condition] = result
            else:
                self.well_defined.add(condition)

        return self.ill_defined

    def test_verify_dependencies(self, cond_id, conditions, variables):
        """
        Verifies that the given condition id is defined, and that its' dependencies and
        their transitive dependencies are all defined and valid.
        """

        if not cond_id in conditions.get_keys():
            return 1
        else:
            result = self.verify_dependencies(cond_id)
        return result

    def verify_dependencies(self, cond_id):
        """
        Performs a depth-first search of a condition's dependencies in order
        to verify that all dependencies and transitive dependencies are defined
        and valid.
        """
        undefined_paths = set()
        self._verify_dependencies(cond_id, undefined_paths, tuple())
        return undefined_paths

    def _verify_dependencies(self, cond_id, undefined_paths, current_path):
        """
        Given the soup for a condition, test that its dependencies are validly
        defined.
        """
        defined_children = True

        # Exception for izpack conditions:
        if cond_id in self.conditions.properties[WHITE_LIST]:
            return True

        # Short-circuit on well-defined conditions:
        if cond_id in self.well_defined:
            return True

        # Short-circuit ill-defined conditions:
        if cond_id in self.ill_defined.keys():
            current_path = current_path + ((cond_id, 'ill-defined condition'),)
            undefined_paths.add(current_path)
            return False

        # Cycle checking:
        tup = (cond_id, 'condition')
        if tup in current_path:
            current_path += ((cond_id, 'cyclic condition reference'),)
            undefined_paths.add(current_path)
            return False

        # Check for undefined condition.
        if not cond_id in self.conditions.get_keys():
            tup = (cond_id, 'undefined condition')
            current_path += (tup,)
            undefined_paths.add(current_path)
            return False

        current_path += (tup,)
        condition = self.conditions.container[cond_id]
        condition_type = condition['type']

        if 'variable' in condition_type:
            var = str(condition.find('name').text)
            if not var in self.variables.get_keys() and self.fail_on_undefined_vars:
                current_path += ((var, 'undefined variable'),)
                undefined_paths.add(current_path)
                return False

        elif 'exists' in condition_type:
            var = str(condition.find('variable').text)
            if not var in self.variables.get_keys() and self.fail_on_undefined_vars:
                current_path += ((var, 'undefined variable'),)
                undefined_paths.add(current_path)
                return False

        elif condition_type in self.compound_conditions:
            dependencies = condition.find_all('condition')
            for dep in dependencies:
                did = str(dep['refid'])
                if not self._verify_dependencies(did, undefined_paths, current_path):
                    defined_children = False

        if defined_children:
            self.well_defined.add(cond_id)

        return defined_children




