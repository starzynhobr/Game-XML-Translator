import os

import pytest

from core.extrator import ExtractedEntry, extrair_entradas, extrair_textos, get_xpath

FIXTURE_XML = os.path.join(os.path.dirname(__file__), "fixtures", "sample.xml")


class TestExtrairTextos:
    def test_returns_tuple(self):
        sucesso, dados = extrair_textos(FIXTURE_XML, "item", "dispName")
        assert isinstance(sucesso, bool)

    def test_extracts_named_items(self):
        sucesso, dados = extrair_textos(FIXTURE_XML, "item", "dispName")
        assert sucesso is True
        assert len(dados) == 3  # 4th item has empty dispName

    def test_extracted_values_are_strings(self):
        _, dados = extrair_textos(FIXTURE_XML, "item", "dispName")
        for xpath, texto in dados.items():
            assert isinstance(texto, str)
            assert texto.strip() != ""

    def test_xpath_keys_start_with_slash(self):
        _, dados = extrair_textos(FIXTURE_XML, "item", "dispName")
        for xpath in dados:
            assert xpath.startswith("/"), f"XPath should start with '/': {xpath}"

    def test_extraction_without_parent_tag(self):
        sucesso, dados = extrair_textos(FIXTURE_XML, "", "dispName")
        assert sucesso is True
        assert len(dados) == 3

    def test_target_tag_not_found_returns_false(self):
        sucesso, msg = extrair_textos(FIXTURE_XML, "item", "nonexistent_tag")
        assert sucesso is False
        assert isinstance(msg, str)

    def test_invalid_xml_returns_false(self, tmp_path):
        bad_xml = tmp_path / "bad.xml"
        bad_xml.write_text("this is not xml at all <><>", encoding="utf-8")
        sucesso, msg = extrair_textos(str(bad_xml), "item", "dispName")
        assert sucesso is False

    def test_empty_texts_are_excluded(self):
        _, dados = extrair_textos(FIXTURE_XML, "item", "description")
        for texto in dados.values():
            assert texto.strip() != ""

    def test_description_extraction(self):
        sucesso, dados = extrair_textos(FIXTURE_XML, "item", "description")
        assert sucesso is True
        assert any("brave warrior" in v for v in dados.values())


class TestExtrairEntradas:
    def test_extracts_multiple_target_tags_as_independent_entries(self):
        sucesso, entradas = extrair_entradas(
            FIXTURE_XML,
            "item",
            ["dispName", "description"],
            [],
        )

        assert sucesso is True
        assert len(entradas) == 6
        assert all(isinstance(entry, ExtractedEntry) for entry in entradas)
        assert [entry.source_tag for entry in entradas[:2]] == ["dispName", "description"]

    def test_context_is_collected_from_the_same_parent_occurrence(self):
        sucesso, entradas = extrair_entradas(
            FIXTURE_XML,
            "item",
            ["description"],
            ["id", "dispName"],
        )

        assert sucesso is True
        assert entradas[0].context == {"id": "001", "dispName": "Hero of Light"}
        assert entradas[1].context == {"id": "002", "dispName": "Shadow Rogue"}
        assert entradas[0].container_xpath == "/root/item[1]"
        assert entradas[1].container_xpath == "/root/item[2]"

    def test_empty_or_missing_context_does_not_block_target_extraction(self):
        sucesso, entradas = extrair_entradas(
            FIXTURE_XML,
            "item",
            ["description"],
            ["missing", "dispName"],
        )

        assert sucesso is True
        assert len(entradas) == 3
        assert "missing" not in entradas[0].context

    def test_rejects_tag_selected_as_target_and_context(self):
        sucesso, mensagem = extrair_entradas(
            FIXTURE_XML,
            "item",
            ["description"],
            ["description"],
        )

        assert sucesso is False
        assert "alvo e contexto" in mensagem

    def test_requires_at_least_one_target_tag(self):
        sucesso, mensagem = extrair_entradas(FIXTURE_XML, "item", [], ["dispName"])

        assert sucesso is False
        assert "tag alvo" in mensagem.lower()

    def test_deduplicates_requested_tags_without_changing_order(self):
        sucesso, entradas = extrair_entradas(
            FIXTURE_XML,
            "item",
            ["description", "description", "dispName"],
            ["id", "id"],
        )

        assert sucesso is True
        assert [entry.source_tag for entry in entradas[:2]] == ["description", "dispName"]
        assert entradas[0].context == {"id": "001"}

    def test_supports_namespaced_xml_using_local_tag_names(self, tmp_path):
        namespaced_xml = tmp_path / "namespaced.xml"
        namespaced_xml.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<data xmlns="urn:game">
  <item><id>1</id><name>Hero</name><bio>Brave fighter.</bio></item>
  <item><id>2</id><name>Mage</name><bio>Wise caster.</bio></item>
</data>
""",
            encoding="utf-8",
        )

        sucesso, entradas = extrair_entradas(
            str(namespaced_xml),
            "item",
            ["bio"],
            ["name"],
        )

        assert sucesso is True
        assert [entry.original for entry in entradas] == ["Brave fighter.", "Wise caster."]
        assert entradas[0].context == {"name": "Hero"}
        assert "local-name()='bio'" in entradas[0].xpath
