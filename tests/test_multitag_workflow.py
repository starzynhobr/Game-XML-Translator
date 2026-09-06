import os
import shutil

from lxml import etree

from core.project import TranslationProject

FIXTURE_XML = os.path.join(os.path.dirname(__file__), "fixtures", "sample.xml")


def _element_signature(path) -> list[tuple[str, tuple[tuple[str, str], ...]]]:
    root = etree.parse(str(path)).getroot()
    return [
        (etree.QName(element).localname, tuple(sorted(element.attrib.items())))
        for element in root.iter()
    ]


def _texts(path, tag: str) -> list[str]:
    root = etree.parse(str(path)).getroot()
    return root.xpath(f"//*[local-name()='{tag}']/text()")


def test_multitag_checkpoint_resume_and_export_preserves_context_and_structure(tmp_path):
    source = tmp_path / "source.xml"
    output = tmp_path / "translated.xml"
    checkpoint = tmp_path / "checkpoint.json"
    shutil.copy2(FIXTURE_XML, source)
    original_signature = _element_signature(source)
    original_ids = _texts(source, "id")

    project = TranslationProject()
    success, error = project.load(
        str(source),
        "item",
        ["dispName", "description"],
        ["id"],
    )
    assert success, error
    selected = list(project.entries.values())[:2]
    project.set_translation(selected[0].xpath, "Herói da Luz")
    project.set_translation(selected[1].xpath, "Um guerreiro corajoso.")
    assert project.save_checkpoint(str(checkpoint))

    resumed = TranslationProject()
    success, error = resumed.load(
        str(source),
        "item",
        ["dispName", "description"],
        ["id"],
    )
    assert success, error
    assert resumed.load_checkpoint(str(checkpoint)) == 2
    assert resumed.export_xml(str(output))

    assert _element_signature(output) == original_signature
    assert _texts(output, "id") == original_ids
    assert _texts(output, "dispName")[0] == "Herói da Luz"
    assert _texts(output, "description")[0] == "Um guerreiro corajoso."
    assert _texts(output, "dispName")[1:] == _texts(source, "dispName")[1:]
    assert _texts(output, "description")[1:] == _texts(source, "description")[1:]


def test_save_in_place_on_copy_changes_only_translated_target(tmp_path):
    source = tmp_path / "in-place.xml"
    shutil.copy2(FIXTURE_XML, source)
    original_signature = _element_signature(source)
    original_ids = _texts(source, "id")
    original_descriptions = _texts(source, "description")

    project = TranslationProject()
    success, error = project.load(str(source), "item", ["dispName"], ["id"])
    assert success, error
    first = next(iter(project.entries.values()))
    project.set_translation(first.xpath, "Herói da Luz")

    assert project.export_xml(str(source))

    assert _element_signature(source) == original_signature
    assert _texts(source, "id") == original_ids
    assert _texts(source, "description") == original_descriptions
    assert _texts(source, "dispName")[0] == "Herói da Luz"


def test_reloading_exported_multitag_xml_keeps_every_target_addressable(tmp_path):
    source = tmp_path / "source.xml"
    output = tmp_path / "translated.xml"
    shutil.copy2(FIXTURE_XML, source)
    project = TranslationProject()
    success, error = project.load(
        str(source), "item", ["dispName", "description"], ["id"]
    )
    assert success, error
    for entry in project.entries.values():
        project.set_translation(entry.xpath, f"[PT] {entry.original}")
    assert project.export_xml(str(output))

    reloaded = TranslationProject()
    success, error = reloaded.load(
        str(output), "item", ["dispName", "description"], ["id"]
    )

    assert success, error
    assert len(reloaded.entries) == 6
    assert {entry.source_tag for entry in reloaded.entries.values()} == {
        "dispName",
        "description",
    }
    assert all(entry.original.startswith("[PT] ") for entry in reloaded.entries.values())
    assert [entry.context for entry in reloaded.entries.values()][:2] == [
        {"id": "001"},
        {"id": "001"},
    ]
