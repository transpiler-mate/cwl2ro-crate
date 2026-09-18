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

from __future__ import annotations

import json
from importlib.metadata import entry_points
from io import StringIO
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest
from click.testing import CliRunner
from cwltool.main import main as cwl_main
from pydantic import ValidationError
from transpiler_mate.api import PluginError, PluginFailureError
from transpiler_mate.runtime.cli import main
from transpiler_mate.runtime.context_resolver import DefaultTranspilerContextResolver

from cwl2ro_crate.plugin import CWL2ROCrateOptions, cwl2rocrate
from cwl2ro_crate.validation import RUN_PROFILES, WORKFLOW_PROFILE, validate

SOURCE = Path(__file__).parent / "fixtures" / "workflow.cwl"


@pytest.fixture
def context() -> Any:
    return DefaultTranspilerContextResolver().resolve(f"{SOURCE}#hello")


@pytest.fixture(scope="session")
def provenance(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directory = tmp_path_factory.mktemp("execution")
    bag = directory / "provenance"
    result = cwl_main(
        [
            "--no-container",
            "--provenance",
            str(bag),
            "--outdir",
            str(directory / "outputs"),
            f"{SOURCE}#hello",
        ],
        stdout=StringIO(),
    )
    assert result == 0
    return bag


def graph(output: Path) -> dict[str, Any]:
    metadata = json.loads((output / "ro-crate-metadata.json").read_text())
    return {entity["@id"]: entity for entity in metadata["@graph"]}


def test_workflow_cli_zip_and_attachment(tmp_path: Path) -> None:
    attached = tmp_path / "inputs.yaml"
    attached.write_text("message: example")
    output = tmp_path / "crate"
    result = CliRunner().invoke(
        main,
        [
            "cwl2rocrate",
            "--output",
            str(output),
            "--zip",
            "--attach",
            str(attached),
            f"{SOURCE}#hello",
        ],
    )
    assert result.exit_code == 0, result.output
    entities = graph(output)
    assert entities["./"]["mainEntity"] == {"@id": "workflow.cwl"}
    assert entities["./"]["conformsTo"] == {"@id": WORKFLOW_PROFILE}
    workflow = entities["workflow.cwl"]
    assert workflow["name"] == "Hello"
    assert workflow["version"] == "0.1.0"
    assert workflow["license"] == "https://spdx.org/licenses/Apache-2.0"
    assert entities[workflow["author"]["@id"]]["givenName"] == "Example"
    packed = json.loads((output / "workflow.cwl").read_text())
    assert any(item["id"] == "#main" for item in packed["$graph"])
    assert any(item["class"] == "CommandLineTool" for item in packed["$graph"])
    assert (output / "attachments/inputs.yaml").read_text() == attached.read_text()
    assert not any(
        "CreateAction" in entity.get("@type", []) for entity in entities.values()
    )
    with ZipFile(f"{output}.zip") as archive:
        assert "ro-crate-metadata.json" in archive.namelist()
        assert archive.read("attachments/inputs.yaml") == attached.read_bytes()


def test_run_conversion(context: Any, provenance: Path, tmp_path: Path) -> None:
    output = tmp_path / "crate"
    original = (provenance / "workflow/packed.cwl").read_bytes()
    cwl2rocrate.execute(context, CWL2ROCrateOptions(output=output, run=provenance))
    entities = graph(output)
    assert set(RUN_PROFILES).issubset(
        {ref["@id"] for ref in entities["./"]["conformsTo"]}
    )
    actions = [
        entity for entity in entities.values() if entity.get("@type") == "CreateAction"
    ]
    assert actions
    assert entities["./"]["license"] == "https://spdx.org/licenses/Apache-2.0"
    assert "version" not in entities["./"]
    assert "dateCreated" not in entities["./"]
    assert any(action.get("endTime") and action.get("startTime") for action in actions)
    assert (output / "packed.cwl").read_bytes() == original
    assert (provenance / "workflow/packed.cwl").read_bytes() == original
    assert any(
        file.read_text() == "Hello world\n"
        for file in output.iterdir()
        if file.is_file()
    )


@pytest.mark.parametrize("target", ["directory", "file", "zip", "symlink"])
def test_existing_outputs_untouched(context: Any, tmp_path: Path, target: str) -> None:
    output = tmp_path / "crate"
    if target == "directory":
        output.mkdir()
    elif target == "file":
        output.write_text("keep")
    elif target == "zip":
        Path(f"{output}.zip").write_text("keep")
    else:
        output.symlink_to(tmp_path / "missing")
    with pytest.raises(PluginFailureError, match="already exists"):
        cwl2rocrate.execute(context, CWL2ROCrateOptions(output=output, zip=True))
    if target == "zip":
        assert Path(f"{output}.zip").read_text() == "keep"
        assert not output.exists()


def test_attachment_collision(context: Any, tmp_path: Path) -> None:
    first = tmp_path / "input.txt"
    second = tmp_path / "INPUT.txt"
    first.touch()
    second.touch()
    with pytest.raises(PluginFailureError, match="collision"):
        cwl2rocrate.execute(
            context, CWL2ROCrateOptions(output=tmp_path / "out", attach=[first, second])
        )
    assert not (tmp_path / "out").exists()


def test_missing_attachment(context: Any, tmp_path: Path) -> None:
    with pytest.raises(PluginFailureError, match="local file"):
        cwl2rocrate.execute(
            context,
            CWL2ROCrateOptions(output=tmp_path / "out", attach=[tmp_path / "missing"]),
        )


@pytest.mark.parametrize("selection", [None, "missing", "echo"])
def test_requires_workflow_selection(
    context: Any, tmp_path: Path, selection: str | None
) -> None:
    context = context.model_copy(update={"process_id": selection})
    with pytest.raises(PluginError):
        cwl2rocrate.execute(context, CWL2ROCrateOptions(output=tmp_path / "out"))
    assert not (tmp_path / "out").exists()


def test_mismatched_run(provenance: Path, tmp_path: Path) -> None:
    changed = tmp_path / "changed.cwl"
    changed.write_text(
        SOURCE.read_text().replace("baseCommand: echo", "baseCommand: printf")
    )
    context = DefaultTranspilerContextResolver().resolve(f"{changed}#hello")
    with pytest.raises(PluginFailureError, match="does not match"):
        cwl2rocrate.execute(
            context, CWL2ROCrateOptions(output=tmp_path / "out", run=provenance)
        )
    assert not (tmp_path / "out").exists()


def test_invalid_run(context: Any, tmp_path: Path) -> None:
    with pytest.raises(PluginFailureError, match="CWLProv directory"):
        cwl2rocrate.execute(
            context,
            CWL2ROCrateOptions(output=tmp_path / "out", run=tmp_path / "outputs.json"),
        )
    with pytest.raises(PluginError):
        cwl2rocrate.execute(
            context, CWL2ROCrateOptions(output=tmp_path / "out", run=tmp_path)
        )
    assert not (tmp_path / "out").exists()


def test_validation_failure_cleans_staging(
    context: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise PluginFailureError("validation rejected")

    monkeypatch.setattr("cwl2ro_crate.plugin.validate", fail)
    with pytest.raises(PluginFailureError, match="validation rejected"):
        cwl2rocrate.execute(
            context, CWL2ROCrateOptions(output=tmp_path / "out", zip=True)
        )
    assert list(tmp_path.iterdir()) == []


def test_validator_rejects_invalid_crate(tmp_path: Path) -> None:
    (tmp_path / "ro-crate-metadata.json").write_text(
        json.dumps({"@context": "https://w3id.org/ro/crate/1.1/context", "@graph": []})
    )
    with pytest.raises(PluginError):
        validate(tmp_path, run=False)


def test_options_and_registration() -> None:
    options = CWL2ROCrateOptions()
    assert options.output == Path("ro-crate")
    assert options.run is None and options.attach == [] and options.zip is False
    with pytest.raises(ValidationError):
        CWL2ROCrateOptions.model_validate({"unknown": 1})
    assert (
        next(
            iter(entry_points(group="transpiler_mate.plugins", name="cwl2rocrate"))
        ).load()
        is cwl2rocrate
    )


def test_default_values_are_part_of_workflow_identity() -> None:
    from cwl2ro_crate.bundle import canonical

    assert canonical({"default": {"doc": "one"}}) != canonical(
        {"default": {"doc": "two"}}
    )
    assert canonical({"doc": "one"}) == canonical({"doc": "two"})


def test_tampered_bag_rejected(context: Any, provenance: Path, tmp_path: Path) -> None:
    import shutil

    copied = tmp_path / "bag"
    shutil.copytree(provenance, copied)
    payload = next(path for path in (copied / "data").rglob("*") if path.is_file())
    payload.write_text("changed")
    with pytest.raises(PluginError):
        cwl2rocrate.execute(
            context, CWL2ROCrateOptions(output=tmp_path / "out", run=copied)
        )
    assert not (tmp_path / "out").exists()


def test_failed_zip_write_rolls_back(
    context: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from cwl2ro_crate.plugin import publish

    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "file.txt").write_text("data")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("cwl2ro_crate.plugin.ZipFile.write", fail)
    output = tmp_path / "out"
    with pytest.raises(OSError, match="disk full"):
        publish(staging, CWL2ROCrateOptions(output=output, zip=True))
    assert not output.exists()
    assert not Path(f"{output}.zip").exists()
