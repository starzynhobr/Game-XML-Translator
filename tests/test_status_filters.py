from unittest.mock import patch

import pytest
from PySide6.QtCore import QCoreApplication, Qt

from core.project import EntryStatus, TranslationEntry
from ui.viewmodel import AppViewModel, TranslationTableModel


@pytest.fixture
def model():
    model = TranslationTableModel()
    model.refresh_all({
        str(i): TranslationEntry(str(i), "Hero " + str(i), "Text", state)
        for i, state in enumerate(EntryStatus)
    })
    return model


@pytest.mark.parametrize("state", list(EntryStatus))
def test_each_status_is_exact_and_counts_are_session_wide(model, state):
    assert model.set_status_filter(state)
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0), Qt.DisplayRole) == list(EntryStatus).index(state) + 1
    assert sum(model.state_counts.values()) == 5
    assert model.state_counts[state] == 1


def test_search_intersection_reset_and_invalid_status(model):
    model.set_status_filter("confirmed")
    model.set_filter("Hero 0")
    assert model.rowCount() == 0
    assert not model.set_status_filter("bad")
    assert model.status_filter == "confirmed"
    model.set_status_filter("all")
    assert model.rowCount() == 1
    model.set_filter("")
    assert model.rowCount() == 5


def test_external_mutation_updates_cached_counts_and_visibility(model):
    model.set_status_filter("pending")
    entry = model._all_index["0"]
    entry.set_translation("Reviewed", "confirmed")
    model.update_entry("0", entry.translation, "confirmed")
    assert model.rowCount() == 0
    assert model.state_counts["pending"] == 0
    assert model.state_counts["confirmed"] == 2
    model.update_entry("0", entry.translation, "confirmed")
    assert model.state_counts["confirmed"] == 2
    model.set_status_filter("error")
    entry.status = EntryStatus.ERROR
    model.update_entry("0", entry.translation, "error")
    assert model.rowCount() == 2
    assert sum(model.state_counts.values()) == 5


@pytest.fixture
def vm(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    monkeypatch.chdir(tmp_path)
    with patch("core.app_controller.AppController._load_config"):
        vm = AppViewModel()
    vm._ctrl.project.entries = {
        "/a": TranslationEntry("/a", "A", "AA", "translated"),
        "/b": TranslationEntry("/b", "B", "BB", "translated"),
        "/c": TranslationEntry("/c", "C", "CC", "confirmed"),
    }
    vm._table.refresh_all(vm._ctrl.project.entries)
    yield vm
    assert app is not None


def test_filter_change_invalidates_hidden_selection(vm):
    vm.selectRow(0)
    vm.setSelectedRows([0, 1])
    vm.setStatusFilter("confirmed")
    assert vm.selectedCount == 0
    assert vm._selected_xpath == ""
    assert vm.filteredEntryCount == 1
    assert vm.stateCounts["all"] == 3
    vm.approveSelectedTranslations()
    assert vm._ctrl.project.entries["/a"].status == "translated"


def test_approve_selection_survives_rows_disappearing(vm):
    vm.setStatusFilter("translated")
    vm.setSelectedRows([0, 1])
    vm.approveSelectedTranslations()
    assert vm.filteredEntryCount == 0
    assert vm.stateCounts["confirmed"] == 3
    assert vm.selectedCount == 0
