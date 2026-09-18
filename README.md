<!--
Copyright 2026 Transpiler-Mate

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# CWL 2 RO-Crate

Package a selected CWL workflow as a **Workflow RO-Crate**, or provide a CWLProv
execution directory to create a **Provenance Run Crate**. The plugin runs through
Transpiler-Mate and never executes the supplied workflow.

## Install

From this repository, using Python 3.10 or newer:

```console
python -m pip install . transpiler-mate-runtime
transpiler-mate cwl2rocrate --help
```

Distribution: `cwl2ro-crate`; Python package: `cwl2ro_crate`; plugin command:
`cwl2rocrate`. There is no standalone executable.

## Package a workflow

```console
transpiler-mate cwl2rocrate --output build/crate 'workflow.cwl#main'
```

The runtime requires Schema.org `SoftwareApplication` metadata in the source.
Select an actual `Workflow` with `#<process-id>`. The output contains
`ro-crate-metadata.json` and `workflow.cwl`, packed with the selected entrypoint
renamed to `#main` and its referenced tools/subworkflows included.

Additional files and a ZIP are optional:

```console
transpiler-mate cwl2rocrate --output build/crate --zip \
  --attach inputs.yaml --attach diagram.svg 'workflow.cwl#main'
```

Attachments are copied under `attachments/`. `--zip` additionally writes
`build/crate.zip` with crate files at the archive root.

## Package an execution

First capture provenance during an actual execution, using your normal runner
settings:

```console
cwltool --provenance run.provenance 'workflow.cwl#main' inputs.yaml
transpiler-mate cwl2rocrate --run run.provenance \
  --output build/run-crate --zip 'workflow.cwl#main'
```

`--run` accepts a local CWLProv directory, not cwltool output JSON. The plugin
verifies the BagIt checksums and conservatively compares the selected executable
workflow with `workflow/packed.cwl` before converting the run. Execution records
and recorded payloads come from CWLProv; the supplied software metadata fills
missing descriptive fields. It does not invent execution status or timestamps.

## Profiles and validation

- Base: RO-Crate **1.1**.
- Workflow mode: Workflow RO-Crate **1.0**.
- Run mode: Process, Workflow, and Provenance Run Crate **0.5**, plus Workflow RO-Crate 1.0.

Every result must pass the bundled `roc-validator` profiles at **REQUIRED** level
before it reaches the destination. This is not a claim that every recommended
or optional requirement is met. Validation resolves official JSON-LD contexts
and may require network access; its cache follows the validator's defaults.

Existing destinations (including empty directories and symlinks) are rejected.
Generation and validation use a temporary staging directory; failures clean it
up. The final copy is not an atomic directory transaction, but ordinary copy/ZIP
failures roll back files created by the plugin.

Container images and external data referenced by the CWL are not downloaded.
Run conversion copies the data included in the CWLProv bag, which can be large.
Unsupported CWLProv structures or uncertain workflow matches fail explicitly.

## Development

Bootstrapped with [transpiler-mate-plugin-project-template](https://github.com/Transpiler-Mate/transpiler-mate-plugin-project-template).
See [CONTRIBUTING.md](CONTRIBUTING.md), the [tutorial](docs/tutorials/first-steps.md),
and [architecture](docs/explanation/architecture.md).

The Apache-licensed runcrate conversion subset is included to avoid its released
package's incompatible `cwl-utils==0.40` pin. See [THIRD_PARTY.md](THIRD_PARTY.md).
Licensed under [Apache 2.0](LICENSE).
