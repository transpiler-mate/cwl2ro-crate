# Copyright 2026 Transpiler-Mate
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

"""Convert a verified CWLProv bag without changing execution provenance."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import bagit
from cwl_loader import load_cwl_from_location
from cwl_loader.utils import to_index
from rocrate.model.contextentity import ContextEntity
from transpiler_mate.api import PluginFailureError

from ._vendor.runcrate.convert import ProvCrateBuilder
from .bundle import bundle, canonical
from .validation import RUN_PROFILES, WORKFLOW_PROFILE

if TYPE_CHECKING:
    from pathlib import Path


def build_run(context: Any, run: Path, packed: dict[str, Any], directory: Path) -> Any:
    if not run.is_dir():
        raise PluginFailureError(
            "--run must be a CWLProv directory, not output JSON or a ZIP."
        )
    bagit.Bag(str(run)).validate()
    source = run / "workflow" / "packed.cwl"
    if not source.is_file():
        raise PluginFailureError("CWLProv is missing workflow/packed.cwl.")
    loaded = load_cwl_from_location(str(source))
    processes = loaded if isinstance(loaded, list) else [loaded]
    index = to_index(processes)
    if "main" not in index:
        raise PluginFailureError(
            "CWLProv packed workflow must contain the main entrypoint."
        )
    recorded = context.model_copy(update={"document": index, "process_id": "main"})
    if canonical(bundle(recorded, directory)) != canonical(packed):
        raise PluginFailureError(
            "The selected CWL workflow does not match the CWLProv execution definition."
        )
    crate = ProvCrateBuilder(str(run)).build()
    # Adapt declarations only; required-level validation gates actual 0.5 conformance.
    profiles = [WORKFLOW_PROFILE, *RUN_PROFILES]
    crate.root_dataset["conformsTo"] = [
        crate.add(
            ContextEntity(
                crate,
                uri,
                properties={
                    "@type": "CreativeWork",
                    "name": uri.rsplit("/", 2)[-2],
                    "version": uri.rsplit("/", 1)[-1],
                },
            )
        )
        for uri in profiles
    ]
    for kind in ("process", "workflow", "provenance"):
        legacy = crate.get(f"https://w3id.org/ro/wfrun/{kind}/0.1")
        if legacy is not None:
            crate.delete(legacy)
    crate.metadata.profile = "https://w3id.org/ro/crate/1.1"
    crate.metadata["conformsTo"] = {"@id": crate.metadata.profile}
    return crate
