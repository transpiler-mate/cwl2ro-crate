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

"""Bundle the selected workflow and compare execution definitions."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from cwl_utils.parser import Workflow, save
from cwltool.context import LoadingContext
from cwltool.pack import pack
from transpiler_mate.api import PluginFailureError

if TYPE_CHECKING:
    from pathlib import Path

    from transpiler_mate.api import TranspilerContext


def bundle(context: TranspilerContext, directory: Path) -> dict[str, Any]:
    process = context.resolved_process
    if not isinstance(process, Workflow):
        raise PluginFailureError("Select a CWL Workflow with #<process-id>.")
    source = directory / "resolved.cwl"
    source.write_text(
        json.dumps(save(list(context.processes), relative_uris=False)), encoding="utf-8"
    )
    return dict(pack(LoadingContext(), f"{source.as_uri()}#{quote(process.id, safe='/')}"))


def canonical(value: Any, *, literal: bool = False) -> Any:
    """Compare executable structure conservatively, ignoring descriptive metadata.

    Packing normalizes the selected entrypoint to #main. Differences that cannot
    be explained by metadata or object order are rejected, not guessed away.
    """
    if isinstance(value, dict):
        return {
            key: canonical(item, literal=literal or key in {"default", "$namespaces"})
            for key, item in value.items()
            if literal
            or (
                key not in {"doc", "label", "$namespaces", "$schemas"}
                and not key.startswith(("https://schema.org/", "http://schema.org/"))
            )
        }
    if isinstance(value, list):
        result = [canonical(item, literal=literal) for item in value]
        if (
            not literal
            and result
            and all(isinstance(item, dict) and "id" in item for item in result)
        ):
            return sorted(result, key=lambda item: item["id"])
        return result
    return value
