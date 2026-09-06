import json
from unittest.mock import Mock, patch

import pytest

from core.project import TranslationEntry, TranslationProject
from core.translation_errors import ERROR_MESSAGES, classify_error
from core.translation_worker import TranslationWorker


@pytest.mark.parametrize("message,code", [
    ("401 unauthorized", "authentication"), ("403 forbidden", "authentication"),
    ("429 quota exhausted", "rate_limit"), ("503 high demand", "unavailable"),
    ("connection timed out", "network"), ("Empty translation response", "empty_response"),
    ("secret opaque error", "unknown"),
])
def test_classification_is_bounded(message, code):
    assert classify_error(RuntimeError(message)) == code


@pytest.fixture
def project():
    project = TranslationProject()
    project.entries = {"/a": TranslationEntry("/a", "A", "Previous", "translated")}
    return project


def test_checkpoint_roundtrip_and_export_separation(project, tmp_path):
    project.mark_error("/a", "rate_limit")
    path = tmp_path / "checkpoint.json"
    assert project.save_checkpoint(str(path))
    project.reset_translations()
    assert project.load_checkpoint(str(path)) == 1
    entry = project.entries["/a"]
    assert entry.error_code == "rate_limit"
    assert entry.error_message == ERROR_MESSAGES["rate_limit"]
    assert project.get_translations_map() == {"/a": "Previous"}


@pytest.mark.parametrize("action", ["retry", "success", "confirm", "reset"])
def test_error_cleared_on_new_action(project, action):
    project.mark_error("/a", "network")
    if action == "retry":
        project.mark_translating("/a")
    elif action == "success":
        project.set_translation("/a", "New")
    elif action == "confirm":
        project.confirm_translation("/a")
    else:
        project.reset_translations()
    assert project.entries["/a"].error_code == ""
    assert project.entries["/a"].error_message == ""


@pytest.mark.parametrize("code", [None, [], {"secret": "value"}, "api_key=secret"])
def test_old_or_untrusted_checkpoint_error_is_normalized(project, tmp_path, code):
    path = tmp_path / "checkpoint.json"
    path.write_text(json.dumps({"version": 2, "entries": {
        "/a": {"translation": "Previous", "status": "error", "error_code": code}
    }}), encoding="utf-8")
    project.load_checkpoint(str(path))
    assert project.entries["/a"].error_code == "unknown"
    assert "secret" not in project.entries["/a"].error_message


def make_worker(project, tmp_path, logs):
    return TranslationWorker(project, {"service": "Gemini", "checkpoint_dir": str(tmp_path),
                             "selected_xpaths": ["/a"], "include_done": True},
                             lambda *_: None, logs.append, lambda: None)


def test_gemini_exception_is_safe_in_log_and_checkpoint(project, tmp_path):
    logs = []
    worker = make_worker(project, tmp_path, logs)
    with patch("core.translation_worker.get_gemini_model",
               side_effect=RuntimeError("503 api_key=VERY_PRIVATE_KEY full prompt=PRIVATE_TEXT")):
        worker._run()
    assert project.entries["/a"].error_code == "unavailable"
    saved = next(tmp_path.glob("*.json")).read_text(encoding="utf-8")
    for secret in ("VERY_PRIVATE_KEY", "PRIVATE_TEXT"):
        assert secret not in saved
        assert secret not in " ".join(logs)


def test_single_error_then_success_clears_diagnostic(project, tmp_path):
    worker = make_worker(project, tmp_path, [])
    with patch("core.translation_worker.translate_text", side_effect=TimeoutError("private")):
        assert worker.translate_single("/a") == ERROR_MESSAGES["network"]
    with patch("core.translation_worker.translate_text", return_value="Success"):
        assert worker.translate_single("/a") == "Success"
    assert project.entries["/a"].error_code == ""


def test_partial_batch_only_marks_missing_entry(project, tmp_path):
    project.entries["/b"] = TranslationEntry("/b", "B")
    worker = make_worker(project, tmp_path, [])
    worker._config["selected_xpaths"] = ["/a", "/b"]
    with patch.object(worker, "_translate_batch_gemini", return_value={"/a": "Success"}):
        worker._run()
    assert project.entries["/a"].error_code == ""
    assert project.entries["/b"].error_code == "missing_result"


def test_error_roles_exposed_without_affecting_translation(project):
    from ui.viewmodel import TranslationTableModel
    project.mark_error("/a", "rate_limit")
    model = TranslationTableModel()
    model.refresh_all(project.entries)
    index = model.index(0, 2)
    assert model.data(index, model.ErrorCodeRole) == "rate_limit"
    assert model.data(index, model.ErrorMessageRole) == ERROR_MESSAGES["rate_limit"]


def test_reload_preserves_diagnostic(project):
    from core.extrator import ExtractedEntry
    project.mark_error("/a", "network")
    entry = Mock(spec=ExtractedEntry, xpath="/a", original="A", source_tag="bio",
                 container_xpath="/", context={})
    project.load_extracted("example.xml", "item", ["bio"], [], [entry])
    assert project.entries["/a"].error_code == "network"
