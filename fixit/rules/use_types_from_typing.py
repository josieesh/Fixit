# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Set

import libcst
from libcst.metadata import ScopeProvider

from fixit import (
    CstContext,
    CstLintRule,
    InvalidTestCase as Invalid,
    ValidTestCase as Valid,
)


REPLACE_BUILTIN_TYPE_ANNOTATION: str = (
    "You are using builtins.{builtin_type} as a type annotation "
    + "but the type system doesn't recognize it as a valid type."
    + " You should use typing.{correct_type} instead."
)

BUILTINS_TO_REPLACE: Set[str] = {"dict", "list", "set", "tuple"}


class UseTypesFromTypingRule(CstLintRule):
    METADATA_DEPENDENCIES = (ScopeProvider,)
    VALID = [
        Valid(
            """
            def fuction(list: List[str]) -> None:
                pass
            """
        ),
        Valid(
            """
            def function() -> None:
                thing: Dict[str, str] = {}
            """
        ),
        Valid(
            """
            def function() -> None:
                thing: Tuple[str]
            """
        ),
        Valid(
            """
            from typing import Dict, List
            def function() -> bool:
                    return Dict == List
            """
        ),
    ]
    INVALID = [
        Invalid(
            """
            from typing import List
            def whatever(list: list[str]) -> None:
                pass
            """,
            expected_replacement="""
            from typing import List
            def whatever(list: List[str]) -> None:
                pass
            """,
        ),
        Invalid(
            """
            def function(list: list[str]) -> None:
                pass
            """,
        ),
        Invalid(
            """
            def func() -> None:
                thing: dict[str, str] = {}
            """,
        ),
        Invalid(
            """
            def func() -> None:
                thing: tuple[str]
            """,
        ),
        Invalid(
            """
            from typing import Dict
            def func() -> None:
                thing: dict[str, str] = {}
            """,
            expected_replacement="""
            from typing import Dict
            def func() -> None:
                thing: Dict[str, str] = {}
            """,
        ),
    ]

    def __init__(self, context: CstContext) -> None:
        super().__init__(context)
        self.annotation_counter: int = 0

    def visit_Annotation(self, node: libcst.Annotation) -> None:
        self.annotation_counter += 1

    def leave_Annotation(self, original_node: libcst.Annotation) -> None:
        self.annotation_counter -= 1

    def visit_Name(self, node: libcst.Name) -> None:
        if self.annotation_counter > 0 and node.value in BUILTINS_TO_REPLACE:
            correct_type = node.value.title()
            scope = self.get_metadata(ScopeProvider, node)
            replacement = None
            if scope is not None and correct_type in scope:
                replacement = node.with_changes(value=correct_type)
            self.report(
                node,
                REPLACE_BUILTIN_TYPE_ANNOTATION.format(
                    builtin_type=node.value, correct_type=correct_type
                ),
                replacement=replacement,
            )
