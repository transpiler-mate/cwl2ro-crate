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

# Changelog

Changes follow Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.1] - 2026-09-28

### Changed

- Improved type annotations and internal code quality by addressing mypy, Ruff, and Bandit findings, without changing public APIs or runtime behavior.

## [0.1.0] - 2026-09-18

### Added

- `cwl2rocrate` Transpiler-Mate plugin, bootstrapped from the project template.
- Workflow RO-Crate 1.0 packaging with selected-entrypoint CWL bundling.
- Optional CWLProv conversion to validated Provenance Run Crate 0.5.
- Bag integrity and conservative executable-workflow matching.
- Optional attachments and ZIP archive, exclusive outputs, and staging cleanup.
- Required-level profile validation, documentation, tests, and CI.

[Unreleased]: https://github.com/Transpiler-Mate/cwl2ro-crate/compare/v0.1.1...develop
[0.1.1]: https://github.com/Transpiler-Mate/cwl2ro-crate/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Transpiler-Mate/cwl2ro-crate/releases/tag/v0.1.0
