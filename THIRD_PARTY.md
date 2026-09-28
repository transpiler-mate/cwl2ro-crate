# Third-party code

`src/cwl2ro_crate/_vendor/runcrate` contains the conversion subset (`convert.py`,
`constants.py`, `utils.py`) of runcrate 0.6.2, obtained from its installed PyPI
distribution. Source: https://github.com/ResearchObject/runcrate/tree/0.6.2

Copyright 2022–2026 CRS4; 2023–2026 Michael R. Crusoe; 2024–2026 Senckenberg
Society for Nature Research. Licensed under Apache-2.0 (see LICENSE and retained
file headers). Local security patches mark the SHA-1 content identifier as non-security use
and replace assertion-based validation with explicit exceptions (including
removal of a redundant split-length assertion). Integration adapts profile
declarations externally and validates the resulting crate against version 0.5.

The subset is bundled because released runcrate pins cwl-utils 0.40, conflicting
with Transpiler-Mate API's cwl-utils >=0.43 requirement. Its runtime dependencies
are declared directly. No runcrate CLI is installed. Upgrades must rerun the
real CWLProv conversion tests and profile validation. Upstream source is excluded
from project formatting, lint, and type checks; integration tests exercise it.
Bandit continues to scan the bundled code.
