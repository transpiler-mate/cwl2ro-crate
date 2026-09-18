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

# Create a crate

## Workflow only

```console
transpiler-mate cwl2rocrate --output build/workflow-crate 'workflow.cwl#main'
```

The CWL must have the Schema.org software metadata required by the runtime.
Select a workflow explicitly; command-line tools alone are rejected.

## Add files and a ZIP

```console
transpiler-mate cwl2rocrate --output build/workflow-crate --zip \
  --attach inputs.yaml --attach diagram.svg 'workflow.cwl#main'
```

`--attach` is fully optional and repeatable. It accepts files, not directories.
Files are copied to `attachments/<basename>`; duplicate basenames are rejected
case-insensitively. An input template attachment does not imply execution.

## Include a recorded execution

```console
cwltool --provenance run.provenance 'workflow.cwl#main' inputs.yaml
transpiler-mate cwl2rocrate --run run.provenance \
  --output build/run-crate --zip 'workflow.cwl#main'
```

The first command executes the workflow; the second only packages recorded data.
`--run` must point to the complete CWLProv directory with valid BagIt checksums,
its packed workflow, provenance traces, and recorded data. Output JSON alone is
insufficient. Keep the source workflow version used for that execution.

Differences in labels or descriptions do not prevent matching. Differences in
executable structure or defaults do. The comparison is deliberately conservative:
semantically equivalent rewrites can be rejected. Do not substitute a different
workflow merely because its input names match.

## Handle failures

Use a new destination: existing directories, files, ZIPs, and symlinks are never
overwritten. Missing attachments, filename collisions, corrupt bags, workflow
mismatches, conversion errors, and required-level profile failures stop creation.
If vocabulary retrieval fails, restore network access and rerun; validation is
not skipped. Check the nested exception for detailed loader/converter failures.

Crate generation does not publish anything. Upload the ZIP separately to a
compatible registry or repository.
