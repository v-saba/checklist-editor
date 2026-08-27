"""Tests for LaTeX escaping and PDF generation."""
import json
import shutil
import tempfile
from pathlib import Path

import pytest

from latex_generator import compile_pdf, escape_latex, generate_latex

DATA_DIR = Path(__file__).parent / 'data'
CESSNA_FIXTURE = DATA_DIR / 'cessna_f150l_exterior_check.json'


@pytest.mark.parametrize('raw,escaped', [
    ('\\', r'\textbackslash{}'),
    ('&', r'\&'),
    ('%', r'\%'),
    ('$', r'\$'),
    ('#', r'\#'),
    ('_', r'\_'),
    ('{', r'\{'),
    ('}', r'\}'),
    ('~', r'\textasciitilde{}'),
    ('^', r'\textasciicircum{}'),
])
def test_escape_latex_special_chars(raw, escaped):
    assert escape_latex(raw) == escaped


def test_escape_latex_empty_and_none():
    assert escape_latex('') == ''
    assert escape_latex(None) == ''


def test_escape_latex_backslash_before_ampersand():
    # Backslash must be handled first so \& is not mangled into textbackslash + &
    assert escape_latex(r'\&') == r'\textbackslash{}\&'


def test_escape_latex_mixed_string():
    assert escape_latex('A & B_C') == r'A \& B\_C'


def test_cessna_fixture_escapes_ampersand():
    data = json.loads(CESSNA_FIXTURE.read_text())
    tex = generate_latex(data['title'], data['subtitle'], data['phases'])

    assert r'movement \& security' in tex
    assert 'movement & security' not in tex
    assert r'\section*{1. Inside the Cabin}' in tex
    assert 'Cessna F150L Exterior Check' in tex


@pytest.mark.parametrize('field,value,expected_fragment', [
    ('title', 'A & B', r'A \& B'),
    ('subtitle', 'cost $5', r'cost \$5'),
    ('phase', 'Phase_1', r'Phase\_1'),
    ('read', '100%', r'100\%'),
    ('do', 'ON #1', r'ON \#1'),
])
def test_generate_latex_escapes_fields(field, value, expected_fragment):
    title = value if field == 'title' else 'Title'
    subtitle = value if field == 'subtitle' else 'Subtitle'
    phase_name = value if field == 'phase' else 'Phase'
    read = value if field == 'read' else 'Read'
    do = value if field == 'do' else 'DO'

    tex = generate_latex(title, subtitle, [{
        'name': phase_name,
        'checklist_items': [{'read': read, 'do': do}],
    }])
    assert expected_fragment in tex


@pytest.mark.skipif(not shutil.which('xelatex'), reason='xelatex not installed')
def test_cessna_fixture_compiles_to_pdf():
    data = json.loads(CESSNA_FIXTURE.read_text())
    tex = generate_latex(data['title'], data['subtitle'], data['phases'])

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = compile_pdf(tex, temp_dir)
        assert Path(pdf_path).is_file()
        assert Path(pdf_path).stat().st_size > 0
