# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List

import libcst as cst
from libcst.metadata import QualifiedName, QualifiedNameProvider, QualifiedNameSource

from fixit import CstLintRule


class NoMissingDocstringOrTestCasesRule(CstLintRule):
    """
    Meta lint rule which checks that all lint rules in repo contain a docstring and test cases.
    """

    MESSAGE = ""
    METADATA_DEPENDENCIES = (QualifiedNameProvider,)

    QUALIFIED_CSTLINTRULE: QualifiedName = QualifiedName(
        name="fixit.CstLintRule", source=QualifiedNameSource.IMPORT
    )
    lint_rule_def_stack: List[str] = []

    # VALID = []
    # INVALID = []

    def should_skip_file(self) -> bool:
        # Skip if we are in a test since sometimes tests use dummy lint rules that don't need test cases or docstring.
        return self.context.in_tests

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        for base_class in node.bases:
            if QualifiedNameProvider.has_name(
                self, base_class.value, self.QUALIFIED_CSTLINTRULE
            ):
                self.lint_rule_def_stack.append(node.name.value)

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:
        if (
            self.lint_rule_def_stack
            and original_node.name.value == self.lint_rule_def_stack[-1]
        ):
            self.lint_rule_def_stack.pop()


# WIP
