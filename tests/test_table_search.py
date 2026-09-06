from PySide6.QtCore import Qt

from core.project import TranslationEntry
from ui.viewmodel import TranslationTableModel


def _entry(
    xpath: str,
    original: str,
    *,
    translation: str = "",
    source_tag: str = "",
    context: dict[str, str] | None = None,
) -> TranslationEntry:
    return TranslationEntry(
        xpath=xpath,
        original=original,
        translation=translation,
        source_tag=source_tag,
        context=context or {},
    )


def test_search_matches_original_translation_tag_and_context():
    model = TranslationTableModel()
    model.refresh_all(
        {
            "/1": _entry("/1", "Iron Man", source_tag="bio", context={"team": "Avengers"}),
            "/2": _entry("/2", "Widow", translation="Viúva", source_tag="name"),
        }
    )

    for query in ("iron", "VIÚVA", "bio", "team", "avengers"):
        model.set_filter(query)
        assert model.rowCount() == 1


def test_search_preserves_original_row_number_and_restores_all_rows():
    model = TranslationTableModel()
    model.refresh_all(
        {
            "/1": _entry("/1", "Alpha"),
            "/2": _entry("/2", "Beta"),
            "/3": _entry("/3", "Gamma"),
        }
    )

    model.set_filter("gamma")
    assert model.data(model.index(0, 0), Qt.DisplayRole) == 3

    model.set_filter("")
    assert model.rowCount() == 3


def test_translation_update_recomputes_active_search_visibility():
    model = TranslationTableModel()
    model.refresh_all({"/1": _entry("/1", "Hello")})
    model.set_filter("olá")
    assert model.rowCount() == 0

    model.update_entry("/1", "Olá", "done")

    assert model.rowCount() == 1
    assert model.data(model.index(0, 2), Qt.DisplayRole) == "Olá"
