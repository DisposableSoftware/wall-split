import os

import pytest

from wall_split import config
from wall_split.config import Config, commented, create_missing, load, read

EXAMPLE = "# header\n\n[appearance]\n# note\nflavor = mocha\naccent = mauve\nopacity = 0.85\n"


def write(path, text):
    path.write_text(text)
    return path


def test_defaults_without_a_file(tmp_path):
    assert read(tmp_path / "missing.ini") == Config()


def test_reads_every_key(tmp_path):
    f = write(tmp_path / "c.ini", "[appearance]\nflavor=latte\naccent=red\nopacity=0.5\n")
    assert read(f) == Config("latte", "red", 0.5)


def test_gtk_flavor_is_accepted(tmp_path):
    assert read(write(tmp_path / "c.ini", "[appearance]\nflavor=gtk\n")).flavor == "gtk"


@pytest.mark.parametrize("text,expected", [("1.7", 1.0), ("-3", 0.0), ("0.25", 0.25)])
def test_opacity_is_clamped(tmp_path, text, expected):
    assert read(write(tmp_path / "c.ini", f"[appearance]\nopacity={text}\n")).opacity == expected


@pytest.mark.parametrize("text", ["lots", "nan"])
def test_bad_opacity_falls_back(tmp_path, text):
    assert read(write(tmp_path / "c.ini", f"[appearance]\nopacity={text}\n")).opacity == 0.85


def test_bad_values_fall_back_per_key(tmp_path):
    f = write(tmp_path / "c.ini", "[appearance]\nflavor=nord\naccent=beige\nopacity=0.4\n")
    assert read(f) == Config("mocha", "mauve", 0.4)


def test_unparsable_file_gives_defaults(tmp_path):
    assert read(write(tmp_path / "c.ini", "this is not\n[an ini")) == Config()


def test_commented_out_example_changes_nothing(tmp_path):
    text = commented(EXAMPLE)
    assert "# flavor = mocha" in text and "# note" in text
    assert read(write(tmp_path / "c.ini", text)) == Config()
    uncommented = text.replace("# flavor = mocha", "flavor = latte")
    assert read(write(tmp_path / "d.ini", uncommented)).flavor == "latte"


def test_first_run_creates_the_file(tmp_path):
    directory = tmp_path / "xdg" / "wall-split"
    assert load(directory, EXAMPLE) == Config()
    assert (directory / "config.ini").read_text() == commented(EXAMPLE)


def test_real_example_is_created_and_loads_as_defaults(tmp_path):
    assert load(tmp_path / "wall-split") == Config()
    text = (tmp_path / "wall-split" / "config.ini").read_text()
    assert text.startswith("# Created by Wall Split")
    assert "# flavor = mocha" in text


def test_existing_file_is_never_written(tmp_path):
    f = write(tmp_path / "config.ini", "[appearance]\nflavor=latte\n")
    create_missing(tmp_path, EXAMPLE)
    assert f.read_text() == "[appearance]\nflavor=latte\n"


def test_symlinks_are_left_alone(tmp_path):
    target = tmp_path / "elsewhere.ini"
    link = tmp_path / "config.ini"
    os.symlink(target, link)
    create_missing(tmp_path, EXAMPLE)
    assert os.path.islink(link) and not target.exists()
    write(target, "[appearance]\nflavor=frappe\n")
    create_missing(tmp_path, EXAMPLE)
    assert target.read_text() == "[appearance]\nflavor=frappe\n"


def test_unwritable_folder_only_warns(tmp_path, capfd):
    blocker = write(tmp_path / "wall-split", "a file, not a folder")
    assert load(blocker, EXAMPLE) == Config()
    assert "could not create" in capfd.readouterr().err
