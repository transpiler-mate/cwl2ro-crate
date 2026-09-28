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

# Architecture

The runtime resolves source locations, validates software metadata, and selects
a process. This plugin uses that context rather than fetching the original source
again. CWL schema references still present may need network access.

## Workflow packing and identity

`cwl_utils.parser.save` serializes the resolved graph. cwltool's Python `pack`
API creates a standalone CWL graph, rewriting the selected workflow to `#main`
and preserving references to included tools and subworkflows. Executing the
workflow is not part of packaging.

For a run, both the selected source and CWLProv's recorded `#main` are normalized
through the same loader and packer. A structural comparison ignores descriptive
labels, documentation, Schema.org metadata, and namespace/schema declarations.
It retains executable settings, input defaults, and order-sensitive lists.
This is a conservative compatibility check, not a proof of semantic equivalence
or a cryptographic assertion of original source identity. Uncertain matches fail.

## CWLProv conversion

The plugin validates BagIt checksums before reading the recorded workflow. It
uses the Apache-licensed conversion subset of runcrate 0.6.2. That release's
package pins cwl-utils 0.40, incompatible with Transpiler-Mate's >=0.43 contract;
the subset is therefore included locally with its copyright headers and notice.
No subprocess invokes runcrate and the plugin never launches the supplied workflow.

The converter builds actions, formal parameters, parameter connections, and data
entities from recorded provenance. Its legacy 0.1 profile declarations are
replaced with 0.5 declarations, then REQUIRED-level validation checks the complete
result against Provenance Run Crate 0.5 and inherited profiles. A conversion that
fails those checks is rejected. The original packed workflow and recorded
payloads are retained; software metadata only enriches missing descriptive fields.

Support is bounded by the converter's CWLProv coverage. Unrecognized types,
missing provenance, or other unsupported structures result in an error instead
of a partially published crate. Failed/partial runs are accepted only if their
recorded structures can be converted and pass validation; no status is inferred.

## Output lifecycle

Preflight rejects existing output paths and attachment collisions. Generation,
attachment copying, and validation happen in staging. Only a validated crate is
copied to a newly reserved output directory. ZIP creation uses exclusive file
creation and puts metadata at the archive root. Ordinary write failures roll back
the output created by this invocation. Parent directories may remain after a
failure; publication is not atomic against process termination.

The official validator resolves JSON-LD vocabulary resources and caches them
using its own configuration. This plugin intentionally has no validation bypass.
