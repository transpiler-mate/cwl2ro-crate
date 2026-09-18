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

# Reference

| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--output` | Path | `ro-crate` | New destination directory. |
| `--run` | Optional path | None | Complete CWLProv directory. |
| `--attach` | Repeatable path | Empty | Local files to include. |
| `--zip` | Flag | False | Also create `<output>.zip`. |

The source is the runtime's positional `SOURCE`, including `#<process-id>`.
The package entry point is `cwl2ro_crate.plugin:cwl2rocrate` in
`transpiler_mate.plugins`. Unknown options are rejected.

## Profile contract

| Mode | Declared profiles | Validator target |
| --- | --- | --- |
| Workflow | RO-Crate 1.1; Workflow RO-Crate 1.0 | `workflow-ro-crate-1.0` |
| Run | Above plus Process/Workflow/Provenance Run Crate 0.5 | `provenance-run-crate-0.5` |

Validation includes inherited profiles at REQUIRED severity using roc-validator
0.11.4. Profile conformance does not assert successful execution: recorded run
facts are retained, and absent execution status is not manufactured.

Workflow metadata maps name, description, software version, license, authors,
contributors, publisher, identifier, creation date, keywords, and help resources.
Nested people, organizations, roles, and resources become linked entities.
Run-mode enrichment fills missing fields, including the converter's unspecified
license placeholder, without replacing recorded actions or data. Workflow identifiers, versions, and
creation dates describe the workflow entity; they are not assigned to the run
crate itself.

::: cwl2ro_crate.plugin
