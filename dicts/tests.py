from pathlib import Path
import tempfile
import json
import pytest
from ruamel.yaml import YAML
from revlibs.dicts import PATH_KEY, DEFAULT_PATH_KEY, Dicts

yaml = YAML()


def create_dir(num_files, dict_generator, extensions):
    tmp_dir = tempfile.mkdtemp()
    p = Path(tmp_dir)
    for i in range(0, num_files):
        d = dict_generator(i)
        # last one should cause problems
        for extension, op in extensions:
            f_name = f"file_{i}.{extension}"
            with open(p / f_name, "w") as f:
                op(d, f)
    return p


@pytest.mark.parametrize(
    "generator,num_files,expected_size,extensions",
    [
        pytest.param(
            lambda i: {"a": i},
            5,
            2 * 5,
            [("yaml", yaml.dump), ("json", json.dump), ("txt", json.dump)],
            id="Test loading both json and yaml",
        ),
        pytest.param(
            lambda i: {"a": i},
            0,
            0,
            [("yaml", yaml.dump), ("json", json.dump), ("txt", json.dump)],
            id="Test with empty directory",
        ),
        pytest.param(
            lambda i: [{"a": i}, {"a": i}],
            5,
            4 * 5,
            [("yaml", yaml.dump), ("json", json.dump), ("txt", json.dump)],
            id="Test loading arrays of dicts",
        ),
        pytest.param(
            lambda i: [{"a": i}, {"a": i}],
            5,
            0,
            [("json", yaml.dump), ("txt", json.dump)],
            id="Test loading invalid json",
        ),
        pytest.param(
            lambda i: [{"a": i}, {"a": i}],
            5,
            2 * 5,
            [("yaml", yaml.dump_all)],
            id="Test loading multi part yaml",
        ),
    ],
)
def test_load_dicts(generator, num_files, expected_size, extensions):
    tmp_dir = create_dir(num_files, generator, extensions)
    loader = Dicts.from_path(tmp_dir, skip_errors=True)
    dicts = list(loader.items)
    assert len(dicts) == expected_size, "number of loaded files matches"
    for d in dicts:
        assert isinstance(d, dict)
        assert d, "loaded dict is not empty"
        assert "a" in d, "dict loaded correctly"
        assert d["a"] < num_files
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()


def test_to_dict_simple():
    a = [{"a": 1, PATH_KEY: "x"}]
    loader = Dicts.from_dicts(a)
    out = loader.strict_group_by_name(key="a")
    assert isinstance(out, dict), "to_dict returns a dict"
    assert len(out) == 1
    assert out[a[0]["a"]] == a[0]


def test_to_dict_transform():
    a = [{"a": "aa", "b": "bb", PATH_KEY: "x"}]
    loader = Dicts.from_dicts(a)
    transformator = lambda d: d["b"]
    out = loader.strict_group_by_name(key="a", transformator=transformator)
    assert isinstance(out, dict), "to_dict returns a dict"
    assert len(out) == 1
    assert out[a[0]["a"]] == a[0]["b"]


def test_group_by_unordered():
    a = [{PATH_KEY: "a"}, {PATH_KEY: "c"}, {PATH_KEY: "b"}, {PATH_KEY: "a"}]
    loader = Dicts.from_dicts(a)
    out = loader.group_by_file()
    assert len(out["a"]) == 2


def test_duplicate():
    a = [{"name": 1, PATH_KEY: "x"}, {"name": 1, PATH_KEY: "y"}]
    loader = Dicts.from_dicts(a)
    with pytest.raises(ValueError):
        loader.strict_group_by_name(key="__PATH__", default="_")


def test_duplicate_skip_errors():
    a = [{"name": 1, PATH_KEY: "x"}, {"name": 1, PATH_KEY: "y"}]
    try:
        loader = Dicts.from_dicts(a)
        loader.strict_group_by_name(key="__PATH__", default="_")
    except KeyError:
        pytest.fail("Exception raised despite skip_errors set")
        # raise


def test_group_by_file():
    a = [
        {"name": 1, PATH_KEY: "x"},
        {"name": 1, PATH_KEY: "y"},
        {"name": 2, PATH_KEY: "y"},
        {"name": 2},
    ]
    loader = Dicts.from_dicts(a)
    out = dict(loader.group_by_file())
    assert out == {
        "x": [{"name": 1, PATH_KEY: "x"}],
        "y": [{"name": 1, PATH_KEY: "y"}, {"name": 2, PATH_KEY: "y"}],
        DEFAULT_PATH_KEY: [{"name": 2}],
    }

