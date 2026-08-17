from scripts.ci.validate_skill_registry import discover, validate_registry


def test_registry_validates_three_standardized_capabilities():
    entries = validate_registry()

    assert {(entry["name"], entry["version"]) for entry in entries} == {
        ("kpgs-audit-verify-govern", "0.1.0"),
        ("kpgs-human-choice-authorship", "0.1.0"),
        ("govern-kpgs-documents", "1.0.0"),
    }


def test_kpgs_dts_is_registered_without_becoming_parallel_runtime_authority():
    [entry] = discover("documents")

    assert entry["name"] == "govern-kpgs-documents"
    assert entry["authority_class"] == "publication-adapter"
    assert entry["package_path"] == "skills/awesome/govern-kpgs-documents"


def test_draft_skills_are_discoverable_but_not_production_loadable():
    entries = validate_registry()

    assert entries
    assert all(entry["state"] == "draft" for entry in entries)
    assert all(entry["production_loadable"] is False for entry in entries)
    assert discover("", production_only=True) == []


def test_discovery_supports_search_metadata():
    names = {entry["name"] for entry in discover("governance")}

    assert "kpgs-audit-verify-govern" in names
    assert "kpgs-human-choice-authorship" in names
    assert "govern-kpgs-documents" in names


def test_discovery_filters_by_declared_runtime_platform():
    names = {entry["name"] for entry in discover("", platform="server")}

    assert "kpgs-audit-verify-govern" in names
    assert "govern-kpgs-documents" in names
    assert "kpgs-human-choice-authorship" not in names
