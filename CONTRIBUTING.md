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

# Contributing

Generated with Copier from `transpiler-mate-plugin-project-template` using
`project_slug=cwl2ro-crate`, `python_package=cwl2ro_crate`, and
`project_name="CWL 2 RO-Crate"`.

```console
hatch run test:test
hatch run dev:typecheck
hatch run dev:ruff check src tests
hatch run dev:ruff format --check src tests
hatch run dev:security
hatch build
python -m pip install -r requirements-docs.txt
mkdocs build --strict
```

Tests generate a real CWLProv bag by running a local `echo` workflow through
cwltool, then convert and validate it. No Docker is needed. Profile validation
may need network access for official vocabularies; the validator manages its
cache. Tests also cover source mismatch, corrupt bags, metadata mapping, ZIPs,
attachments, output protection, and cleanup.

Vendored conversion code retains upstream formatting and is excluded from the
project's strict typing, lint, and security gates. Its behavior is covered by
integration tests. Review `THIRD_PARTY.md` before updating it. Dependency changes
must remain resolvable alongside transpiler-mate-api and runtime.
