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

# Install

Use Python 3.10 or newer. From the repository:

```console
python -m pip install . transpiler-mate-runtime
transpiler-mate cwl2rocrate --help
```

Use `pip install -e . transpiler-mate-runtime` for an editable development install.
The runtime and plugin must share an environment for entry-point discovery.
The plugin depends on the API contract; the runtime is installed separately.

RO-Crate, CWLProv conversion dependencies, and the profile validator are installed
automatically. Installing the standalone `runcrate` distribution alongside this
plugin is unsupported because its `cwl-utils` pin conflicts with the runtime.
The required conversion modules are included and attributed in `THIRD_PARTY.md`.
