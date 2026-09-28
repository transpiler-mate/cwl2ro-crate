<!--
Copyright 2026 Terradue

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

# First steps

From the checkout, install the plugin and runtime:

```console
python -m pip install . transpiler-mate-runtime
```

The example `tests/fixtures/workflow.cwl` contains software metadata, a workflow
with a string input, and an `echo` tool producing a text file.

## Package the definition

```console
transpiler-mate cwl2rocrate --output build/definition --zip \
  'tests/fixtures/workflow.cwl#hello'
```

Inspect `build/definition/ro-crate-metadata.json` and `workflow.cwl`. The crate
identifies the packed workflow as its main entity and describes its authors,
license, and version. `build/definition.zip` is ready to upload separately.

## Capture and package a run

This example only runs the local `echo` command and needs no container:

```console
cwltool --no-container --provenance build/provenance --outdir build/results \
  'tests/fixtures/workflow.cwl#hello'
transpiler-mate cwl2rocrate --run build/provenance \
  --output build/execution --zip 'tests/fixtures/workflow.cwl#hello'
```

The execution crate includes `packed.cwl`, the input document, the recorded
output payload (stored under its content hash), and metadata connecting workflow
and step actions to inputs and outputs. Both commands use the default message.
Run-profile validation is performed before the crate is published locally.

Use fresh output paths when repeating the tutorial. Publishing to WorkflowHub or
an archive is a separate action.
