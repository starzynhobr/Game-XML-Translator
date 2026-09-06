from pathlib import Path

from core.updater import INSTALLER_TEMPLATE

ROOT = Path(__file__).resolve().parents[1]


def test_inno_installer_uses_stz_labs_and_stable_upgrade_identity():
    installer = (ROOT / "installer.iss").read_text(encoding="utf-8")

    assert '#define AppPublisher "STZ Labs"' in installer
    assert "AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" in installer
    assert "PrivilegesRequired=lowest" in installer
    assert "Source: \"{#SourceDir}\\*\"" in installer
    assert "OutputBaseFilename=STZXMLTranslator-Setup-{#AppVersion}" in installer
    assert INSTALLER_TEMPLATE == "STZXMLTranslator-Setup-{version}.exe"


def test_local_build_enables_inno_without_upx():
    build = (ROOT / "build_nuitka.bat").read_text(encoding="utf-8")

    assert "set BUILD_INSTALLER=1" in build
    assert "set USE_UPX=0" in build
    assert 'if exist "%ProgramFiles(x86)%\\Inno Setup 6\\ISCC.exe"' in build
    assert '"%ISCC_EXE%" installer.iss' in build
    assert "Program Files ^(x86^)" not in build
    assert '> "core\\_build_version.py" echo BUILD_VERSION = "%APP_VERSION%"' in build


def test_release_pipeline_publishes_setup_portable_and_checksums_without_msix():
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert "choco install innosetup" in workflow
    assert "STZXMLTranslator-Setup-$env:VERSION.exe" in workflow
    assert "STZXMLTranslator-Portable-$env:VERSION.zip" in workflow
    assert "Get-FileHash" in workflow
    assert 'core\\_build_version.py' in workflow
    assert "build-msix.ps1" not in workflow
    assert "CERT_PFX_BASE64" not in workflow
