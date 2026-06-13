"""
Tests del indexer del Asesor.
"""
import os
import json
import pytest

from app.services.asesor_indexer import _hash, _infer_source_type, _infer_title, list_corpus_files


def test_hash_determinista():
    h1 = _hash("hola mundo")
    h2 = _hash("hola mundo")
    assert h1 == h2
    assert len(h1) == 64


def test_hash_distinto_contenido():
    assert _hash("a") != _hash("b")


def test_infer_source_type_ley():
    assert _infer_source_type("/path/ley_21719.txt") == "ley"
    assert _infer_source_type("C:\\paso\\ley_21719_texto.txt") == "ley"


def test_infer_source_type_manual():
    assert _infer_source_type("/docs/MANUAL_USUARIO.md") == "manual"
    assert _infer_source_type("/path/que_es_rat.md") == "manual"


def test_infer_source_type_casos():
    assert _infer_source_type("/docs/casos_de_uso/CASO_01.md") == "caso_uso"


def test_infer_source_type_otros():
    assert _infer_source_type("/random/file.md") == "otros"


def test_infer_title_desde_h1(tmp_path):
    f = tmp_path / "doc.md"
    f.write_text("# Mi Documento\n\nContenido.", encoding="utf-8")
    title = _infer_title(str(f), f.read_text(encoding="utf-8"))
    assert title == "Mi Documento"


def test_infer_title_sin_heading(tmp_path):
    f = tmp_path / "doc.md"
    f.write_text("Solo contenido sin título.", encoding="utf-8")
    title = _infer_title(str(f), f.read_text(encoding="utf-8"))
    assert title == "doc.md"


def test_list_corpus_files_sin_carpeta():
    assert list_corpus_files("./no_existe_xyz") == []
