import time
from unittest.mock import patch

import pytest
from PySide6.QtCore import QCoreApplication

from core.updater import ReleaseInfo
from ui.viewmodel import AppViewModel


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QCoreApplication.instance() or QCoreApplication([])
    yield app


@pytest.fixture
def vm(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return AppViewModel()


def release(version: str = "1.5.0") -> ReleaseInfo:
    return ReleaseInfo(
        version=version,
        tag_name=f"v{version}",
        notes="Changes",
        page_url=f"https://github.com/StarzynhoBR/STZ-XML-Translator/releases/tag/v{version}",
        installer_name=f"STZXMLTranslator-Setup-{version}.exe",
        download_url=(
            "https://github.com/StarzynhoBR/STZ-XML-Translator/"
            f"releases/download/v{version}/STZXMLTranslator-Setup-{version}.exe"
        ),
        sha256="a" * 64,
        size=10,
    )


def test_automatic_check_runs_at_most_once_per_day(vm):
    with patch.object(vm, "_begin_update_check") as begin:
        vm._ctrl.last_update_check = time.time()
        vm.checkForUpdatesAutomatically()
        begin.assert_not_called()

        vm._ctrl.last_update_check = 0
        vm.checkForUpdatesAutomatically()
        begin.assert_called_once_with(False)


def test_manual_check_can_show_a_previously_skipped_release(vm):
    candidate = release()
    vm._ctrl.skipped_update_version = candidate.version

    vm._finish_update_check(candidate, "", False)
    assert vm.updateStatus == "idle"
    assert vm.updateAvailable is False

    vm._finish_update_check(candidate, "", True)
    assert vm.updateStatus == "available"
    assert vm.updateAvailable is True
    assert vm.updateVersion == "1.5.0"


def test_skip_persists_the_release_version(vm):
    candidate = release()
    vm._update_release = candidate
    vm._update_status = "available"
    with patch.object(vm._ctrl, "save_update_preferences") as save:
        vm.skipUpdate()
    save.assert_called_once_with(skipped_version="1.5.0")
    assert vm.updateStatus == "idle"
    assert vm.updateAvailable is False


def test_install_is_blocked_during_translation(vm):
    vm._update_release = release()
    vm._update_installer_path = "setup.exe"
    vm._update_status = "ready"
    vm._is_translating = True
    with patch("ui.viewmodel.launch_installer") as launch:
        vm.installUpdate()
    launch.assert_not_called()


def test_ready_update_launches_installer_and_quits(vm):
    vm._update_release = release()
    vm._update_installer_path = "setup.exe"
    vm._update_status = "ready"
    vm._is_translating = False
    with (
        patch("ui.viewmodel.launch_installer", return_value=True) as launch,
        patch("ui.viewmodel.QCoreApplication.quit") as quit_app,
    ):
        vm.installUpdate()
    launch.assert_called_once_with("setup.exe")
    quit_app.assert_called_once_with()


def test_manual_network_error_is_visible_but_automatic_error_is_quiet(vm):
    vm._finish_update_check(None, "network", False)
    assert vm.updateStatus == "idle"

    vm._finish_update_check(None, "network", True)
    assert vm.updateStatus == "error"
    assert vm.updateStatusText == vm.strings["update_error_network"]
