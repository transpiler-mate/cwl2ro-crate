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

"""Transpiler-Mate plugin for workflow and execution RO-Crates."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any
from zipfile import ZIP_DEFLATED, ZipFile

from pydantic import BaseModel, ConfigDict, Field
from rocrate.model.contextentity import ContextEntity
from rocrate.rocrate import ROCrate
from transpiler_mate.api import (
    PluginError,
    PluginExecutionError,
    PluginFailureError,
    transpiler_plugin,
)

from .bundle import bundle
from .metadata import enrich
from .run import build_run
from .validation import WORKFLOW_PROFILE, validate

if TYPE_CHECKING:
    from transpiler_mate.api import TranspilerContext


class CWL2ROCrateOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    output: Path = Field(default=Path("ro-crate"), description="New output directory")
    run: Path | None = Field(
        default=None, description="CWLProv directory from cwltool --provenance"
    )
    attach: list[Path] = Field(
        default_factory=list, description="Additional local file (repeatable)"
    )
    zip: bool = Field(default=False, description="Also write <output>.zip")


def check_paths(options: CWL2ROCrateOptions) -> None:
    targets = [options.output]
    if options.zip:
        targets.append(Path(f"{options.output}.zip"))
    for target in targets:
        if target.exists() or target.is_symlink():
            raise PluginFailureError(f"Output already exists: {target}")
    names: set[str] = set()
    for path in options.attach:
        if not path.is_file():
            raise PluginFailureError(f"Attachment is not a local file: {path}")
        if path.name.casefold() in names:
            raise PluginFailureError(f"Attachment filename collision: {path.name}")
        names.add(path.name.casefold())


def workflow_crate(
    context: TranspilerContext, packed: dict[str, Any], work: Path
) -> Any:
    source = work / "workflow.cwl"
    source.write_text(json.dumps(packed, indent=2), encoding="utf-8")
    crate = ROCrate(version="1.1")
    crate.add_workflow(
        source, "workflow.cwl", main=True, lang="cwl", lang_version=packed["cwlVersion"]
    )
    profile = crate.add(
        ContextEntity(
            crate,
            WORKFLOW_PROFILE,
            properties={
                "@type": "CreativeWork",
                "name": "Workflow RO-Crate",
                "version": "1.0",
            },
        )
    )
    crate.root_dataset["conformsTo"] = profile
    enrich(crate, context.metadata, run=False)
    return crate


def publish(staged: Path, options: CWL2ROCrateOptions) -> None:
    """Publish validated artifacts with exclusive creation; roll back our own files."""
    created_output = False
    created_zip = False
    archive = Path(f"{options.output}.zip")
    try:
        options.output.mkdir()  # Exclusive reservation, including empty existing directories.
        created_output = True
        shutil.copytree(staged, options.output, dirs_exist_ok=True)
        if options.zip:
            with archive.open("xb") as stream:
                created_zip = True
                with ZipFile(stream, "w", ZIP_DEFLATED) as zipped:
                    for file in sorted(staged.rglob("*")):
                        if file.is_file():
                            zipped.write(file, file.relative_to(staged).as_posix())
    except Exception:
        if created_zip:
            archive.unlink()
        if created_output:
            shutil.rmtree(options.output)
        raise


@transpiler_plugin(
    name="cwl2rocrate",
    description="Package a CWL workflow or CWLProv run as an RO-Crate.",
    options_model=CWL2ROCrateOptions,
)
def cwl2rocrate(context: TranspilerContext, options: CWL2ROCrateOptions) -> None:
    try:
        check_paths(options)
        options.output.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(
            prefix=".cwl2rocrate-", dir=options.output.parent
        ) as temporary:
            work = Path(temporary).resolve()
            packed = bundle(context, work)
            crate = (
                build_run(context, options.run, packed, work)
                if options.run
                else workflow_crate(context, packed, work)
            )
            if options.run:
                enrich(crate, context.metadata, run=True)
            for path in options.attach:
                destination = f"attachments/{path.name}"
                if crate.get(destination) is not None:
                    raise PluginFailureError(
                        f"Attachment collides with crate content: {destination}"
                    )
                crate.add_file(
                    path.resolve(), destination, properties={"name": path.name}
                )
            staged = work / "crate"
            crate.write(staged)
            validate(staged, run=options.run is not None)
            publish(staged, options)
    except PluginError:
        raise
    except Exception as exc:
        raise PluginExecutionError(f"Unable to create RO-Crate: {exc}") from exc
