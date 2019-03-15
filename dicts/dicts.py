from typing import Dict, Any, Iterable, Callable, List, Optional, Union
from pathlib import Path
import json
import logging
from itertools import groupby
from ruamel.yaml import YAML


log = logging.getLogger(__name__)
yaml = YAML()

# Original location of the file.
# To be used to hint the user for file location which contains a potential problem.
# Not mandatory.
PATH_KEY = "__PATH__"
DEFAULT_PATH_KEY = "_"

DISABLED_KEY = "disabled"
DEFAULT_KEY = "name"


class DictLoader:
    def __init__(self, path: Optional[Path] = None, skip_errors: bool = False):
        log.debug("Loading dicts from %s", path)
        self.path = path.resolve() if path else None
        self._skip_errors = skip_errors
        self.items = None

    @staticmethod
    def from_path(
        path: Path,
        skip_errors=False,
        disabled_key: str = "disabled",
        load_disabled: bool = False,
    ):
        loader = DictLoader(path, skip_errors=skip_errors)
        loader.items = list(
            DictLoader.remove_disabled_items(
                loader.directory(), disabled_key, load_disabled
            )
        )
        return loader

    @staticmethod
    def from_dicts(
        dicts: Iterable[Dict],
        skip_errors=False,
        disabled_key: str = DISABLED_KEY,
        load_disabled: bool = False,
    ):
        loader = DictLoader(None, skip_errors=skip_errors)
        loader.items = list(
            DictLoader.remove_disabled_items(dicts, disabled_key, load_disabled)
        )
        return loader

    @staticmethod
    def remove_disabled_items(items: Iterable[Dict], disabled_key: str, load_disabled: bool) -> Iterable[Dict]:
        if load_disabled:
            log.debug("load_disabled_items flag is True")
            return list(items)
        disabled_count = 0
        for n, d in enumerate(items):
            if not d.get(disabled_key, False):
                yield d
            else:
                disabled_count += 1
        else:
            n = 0
        log.info("%d out of %d items are enabled", disabled_count, n)

    @staticmethod
    def single_file(full_path: Path) -> Iterable[Dict]:
        """ Load a single yaml or json file as dict.
            Location of path is also stored in the in PATH_KEY"""
        with full_path.open() as f:
            fname = full_path.as_posix()
            contents = None
            if full_path.suffix in (".yaml", ".yml"):
                contents = yaml.load_all(f)
            elif full_path.suffix == ".json":
                contents = [json.load(f)]
            if contents:
                for item in contents:
                    if isinstance(item, list):
                        for c in item:
                            c[PATH_KEY] = fname
                            yield c
                    else:
                        item[PATH_KEY] = fname
                        yield item

    def directory(self) -> Iterable[Dict]:
        """ Load all files from a directory or file. Both json and yaml files will work """
        if self.path.is_file():
            source = [self.path]
        elif self.path.is_dir():
            source = self.path.iterdir()
        else:
            log.warning("Path is not regular file or dictionary. Skipping it")
            return
        for p in source:
            p = p.resolve()
            if not p.is_file():
                continue
            try:
                for d in DictLoader.single_file(p):
                    yield d
            except Exception as e:
                if not self._skip_errors:
                    raise e
                log.warning("Could not load %s: %s", p, e)
                log.exception(e)

    def _group_by(
        self,
        transformator: Callable[[Dict], Any],
        key: Union[Callable[[Dict], str], str],
        default_group: str,
    ) -> Iterable[Dict[str, List[Any]]]:
        key_func = (lambda d: d.get(key, default_group)) if isinstance(key, str) else key
        transformator_func = transformator or (lambda x: x)
        for k, v in groupby(self.items, key=key_func):
            yield (k, list(map(transformator_func, v)))

    def group_by_key(
        self,
        transformator: Callable[[Dict], Any] = None,
        key: Union[Callable[[Dict], str], str] = DEFAULT_KEY,
        allow_duplicates: bool = False,
    ) -> Dict[str, Any]:
        """
            Load all config files from a path (directory or a file) into a dict using key field.
            Convert them to any other object using transformator
            if load_disabled is set, do not load those who are marked as disabled
            if any error happens, proceed only if skip_errors is True
            This is important if you don't want all your etl fail because of a single duplicate account
        """
        out = {}
        # Group and then deduplicate
        for k, v in self._group_by(transformator, key, "_"):
            if len(v) > 1:
                # duplicate handling
                duplicates = [vv.get(PATH_KEY) for vv in v]
                err_msg = f"Non-unique key {k} found in {len(v)} dicts [{', '.join(duplicates)} ]"
                log.error(err_msg)
                if not allow_duplicates:
                    raise KeyError(err_msg)
            out[k] = v[0]
        return out

    def group_by_file(self, transformator: Callable[[Dict], Any] = None) -> Dict[str, List[Any]]:
        """
            Load all config files from a path (directory or a file) into a dict using key field.
            Convert them to any other object using transformator
            if load_disabled is set, do not load those who are marked as disabled
            if any error happens, proceed only if skip_errors is True
            This is important if you don't want all your etl fail because of a single duplicate account
        """
        return dict(self._group_by(transformator, PATH_KEY, DEFAULT_PATH_KEY))
