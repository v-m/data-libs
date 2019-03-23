from typing import Dict, Any, Iterable, Callable, List, Optional, Union, Tuple

import json
import logging
from pathlib import Path

from itertools import groupby, chain
from functools import partial

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


class Dicts:
    def __init__(
        self,
        path: Optional[Path] = None,
        dicts: Optional[List[Dict]] = None,
        skip_errors: bool = False,
        load_disabled: bool = False,
        disabled_key: str = "disabled",
    ):
        log.debug(f"Loading dicts from {path}")

        self._skip_errors_ = skip_errors
        self._load_disabled_ = load_disabled
        self._disabled_key_ = disabled_key
        self._dicts_ = dicts

        self.path = path.resolve() if path else None
        self.is_path, self.is_dir = self.classify_path()

        self.items = self.remove_disabled_items() if self._load_disabled_ else self._items_

    def classify_path(self):
        if self.path:
            return (self.path.is_file(), self.path.is_dir())
        else:
            log.debug("No path supplied")
            return (False, False)

    @property
    def _items_(self) -> Iterable[Dict]:

        if self.path and self.is_path:
            log.debug("Loading objects from single paths")
            return Dicts.single_file(self.path)

        elif self.is_dir:
            log.debug("Loading objects from directory")
            return self.directory()

        elif self._dicts_:
            log.debug("Loading supplied objects")
            return chain(self._dicts_)

        e = "No objects found to load"
        log.warning(e)
        raise ValueError(e)

    def remove_disabled_items(self) -> Iterable[Dict]:
        if self._items_:
            n_removed = 0
            for n, item in enumerate(self._items_):
                if not item.get(self._disabled_key_, False):
                    yield item
                else:
                    n_removed += 1
        else:
            log.warning("No items found or supplied to Dicts")
            n = 0

        log.info(f"{n_removed} out of {n} items are enabled")

    @staticmethod
    def single_file(path: Path) -> Iterable[Dict]:
        """
        Load a single yaml or json file as dict.
        Location of path is also stored in the in PATH_KEY
        """
        with path.open() as f:
            full_path = path.as_posix()
            suffix = path.suffix

            if suffix in (".yaml", ".yml"):
                contents = yaml.load_all(f)

            elif suffix == ".json":
                contents = list(json.load(f))

            else:
                log.debug(f"Suffix {suffix} not loadable for path {full_path}")

            if contents:
                for item in contents:
                    # What is going on here
                    if isinstance(item, list):
                        for c in item:
                            c[PATH_KEY] = full_path
                            yield c
                    else:
                        item[PATH_KEY] = full_path
                        yield item

    def directory(self) -> Iterable[Dict]:
        """
        Load all json and yaml files from a directory
        """
        if self.path:
            paths = self.path.iterdir() if self.is_dir else iter([self.path])
        else:
            log.error("Tried to load a directory without a supplied path")

        for path in paths:
            path = path.resolve()

            if not path.is_file():
                log.debug(f"Path is not a file: {path}")
                continue

            try:
                for document in Dicts.single_file(path):
                    yield document

            except Exception as e:
                if not self._skip_errors_:
                    raise e
                log.warning(f"Could not load {path}: {e}")
                log.exception(e)

    def cast_as(self, type_: Callable[[Dict], Any]) -> Iterable[Any]:
        for item in self.items:
            yield type_(item)

    def _grouper_(
        self, key: Union[Callable[[Dict], str], str], default: str
    ) -> Callable[[Dict], str]:
        """Convienience function to convert a string to a dictionary accessor function

        Args:
            key: A grouping function to pass to itertools.groupby 
                 or a dictionary key name that will be converted to an accessor

        Returns:
            A function by which a dictionary can be grouped
        """
        return key if not isinstance(key, str) else lambda d: d.get(key, default)

    def group_by(
        self, key: Union[Callable[[Dict], str], str], default: str, strict: bool
    ) -> Iterable[Tuple[str, List[Any]]]:
        """Group a list of dicts by a function or key name. Choose to die if duplicates
        appear in the list for validation.

        Args:
            key: To be converted to a grouper function
            default: The default grouping if the group function returns None for an 
                     element
            strict: Only allow groups with one element
        
        Returns:
            A dictionary 
        """
        for k, v in groupby(self.items, key=self._grouper_(key, default)):
            items = list(v)
            n = len(items)
            if n > 1:
                head, *_ = items
                msg = f"Group key {head[PATH_KEY]} has {n} elements"
                if strict:
                    log.error(msg)
                    raise ValueError(msg)
                else:
                    log.info(msg)
            yield (k, items)

    def strict_group_by_name(self, key: str, default: str) -> Dict[str, Any]:
        """Groups a list of dicts into key-value pairs of unique key to a
        single element

        Args:
            key: A dictionary key to group by
            default: The default group if the dictionary key does not exist
                     in a dict

        Returns:
            A map of unique values in some config to the config.
            For example, for a directory containing config files {path: config}
        """
        grouped_items = self.group_by(key=key, default=default, strict=True)
        return {k: head for (k, (head, *_)) in grouped_items}

    def group_by_file(self) -> Dict[str, List[Any]]:
        """Groups the supplied dicts by filepath"""
        grouped_items = self.group_by(key=PATH_KEY, default=DEFAULT_PATH_KEY, strict=False)
        return dict(grouped_items)

    @staticmethod
    def from_path(
        path: Path,
        skip_errors: bool = False,
        load_disabled: bool = False,
        disabled_key: str = DISABLED_KEY,
    ):
        return Dicts(
            path=path,
            skip_errors=skip_errors,
            load_disabled=load_disabled,
            disabled_key=disabled_key,
        )

    @staticmethod
    def from_dicts(
        dicts: List[Dict],
        skip_errors: bool = False,
        load_disabled: bool = False,
        disabled_key: str = DISABLED_KEY,
    ):
        return Dicts(
            dicts=dicts,
            skip_errors=skip_errors,
            load_disabled=load_disabled,
            disabled_key=disabled_key,
        )
