# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Required-level validation against pinned RO-Crate profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rocrate_validator import services
from transpiler_mate.api import PluginFailureError

WORKFLOW_PROFILE = "https://w3id.org/workflowhub/workflow-ro-crate/1.0"
RUN_PROFILES = [
    f"https://w3id.org/ro/wfrun/{kind}/0.5" for kind in ("process", "workflow", "provenance")
]


if TYPE_CHECKING:
    from pathlib import Path


def validate(directory: Path, *, run: bool) -> None:
    profile = "provenance-run-crate-0.5" if run else "workflow-ro-crate-1.0"
    result = services.validate(
        {
            "rocrate_uri": str(directory),
            "profile_identifier": profile,
            "requirement_severity": "REQUIRED",
        }
    )
    if not result.passed():
        issues = "; ".join(str(issue.message) for issue in result.get_issues())
        raise PluginFailureError(f"RO-Crate failed {profile} validation: {issues}")
