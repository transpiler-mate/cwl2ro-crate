"""Regression coverage for the documented security patches to bundled runcrate."""

from __future__ import annotations

import pytest

from cwl2ro_crate._vendor.runcrate.utils import parse_img


@pytest.mark.parametrize(
    ("image", "expected"),
    [
        ("ubuntu", {"registry": "docker.io", "name": "ubuntu"}),
        ("ubuntu:latest", {"registry": "docker.io", "name": "ubuntu", "tag": "latest"}),
        ("ubuntu@sha256:abc", {"registry": "docker.io", "name": "ubuntu", "sha256": "abc"}),
        ("https://example.org/image.tar", "https://example.org/image.tar"),
    ],
)
def test_image_reference_parsing(image: str, expected: dict[str, str] | str) -> None:
    assert parse_img(image) == expected


def test_rejects_unsupported_image_digest() -> None:
    with pytest.raises(ValueError, match="must use sha256"):
        parse_img("ubuntu@sha1:abc")
