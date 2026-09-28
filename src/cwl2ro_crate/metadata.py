# Copyright 2026 Terradue
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

"""Translate normalized Schema.org metadata into linked crate entities."""

from __future__ import annotations

from typing import Any

from rocrate.model.contextentity import ContextEntity

SCHEMA = "https://schema.org/"


def add_value(crate: Any, value: Any, identifier: str) -> Any:
    """Add nested metadata objects to the crate and return their linked values."""
    if isinstance(value, list):
        return [add_value(crate, item, f"{identifier}-{index}") for index, item in enumerate(value)]
    if not isinstance(value, dict):
        return value
    properties = {}
    for source_key, item in value.items():
        key = source_key.removeprefix(SCHEMA)
        properties[key] = (
            item.removeprefix(SCHEMA)
            if key == "@type" and isinstance(item, str)
            else add_value(crate, item, f"{identifier}-{key.lstrip('@')}")
        )
    return crate.add(ContextEntity(crate, identifier, properties=properties))


def enrich(crate: Any, metadata: Any, *, run: bool) -> None:
    """Add software metadata, preserving recorded values for execution crates."""
    data = metadata.model_dump(by_alias=True, exclude_none=True)
    workflow = crate.mainEntity
    mapping = {"softwareVersion": "version", "softwareHelp": "subjectOf"}
    for source_key, value in data.items():
        key = source_key.removeprefix(SCHEMA)
        if key not in {
            "name",
            "description",
            "softwareVersion",
            "license",
            "author",
            "contributor",
            "publisher",
            "identifier",
            "dateCreated",
            "keywords",
            "softwareHelp",
        }:
            continue
        target = mapping.get(key, key)
        converted = add_value(crate, value, f"#software-{key}")
        if workflow.get(target) is None or not run:
            workflow[target] = converted
        root_field = key != "softwareHelp" and (
            not run or key in {"license", "author", "contributor", "publisher", "keywords"}
        )
        if root_field and (
            crate.root_dataset.get(target) is None
            or (target == "license" and crate.root_dataset.get(target) == "notspecified")
            or not run
        ):
            crate.root_dataset[target] = converted
