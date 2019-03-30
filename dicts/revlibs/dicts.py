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

        self.skip_errors = skip_errors
        self.load_disabled = load_disabled
        self.disabled_key = disabled_key

        self.path = path.resolve() if path else None
        self.is_path, self.is_dir = self.__classify_path()

        self.__dicts = dicts
        self.__items = self.__load_items()
        self.keyed = False

    @property
    def items(self):
        return self.__items

    def __classify_path(self):
        if self.path:
            return (self.path.is_file(), self.path.is_dir())
        else:
            log.debug("No path supplied")
            return (False, False)

    def __load_items(self) -> Iterable[Dict]:

        if self.path and self.is_path:
            log.debug("Loading objects from single paths")
            items = Dicts.load_file(self.path)

        elif self.is_dir:
            log.debug("Loading objects from directory")
            items = self.load_directory()

        elif self.__dicts:
            log.debug("Loading supplied objects")
            items = chain(self.__dicts)

        else:
            e = "No objects found to load"
            log.warning(e)
            raise ValueError(e)

        return items if self.load_disabled else self.remove_disabled_items(items)

    def remove_disabled_items(self, items) -> Iterable[Dict]:
        if items:
            n = 0
            n_removed = 0
            for n, item in enumerate(items):
                if not item.get(self.disabled_key, False):
                    yield item
                else:
                    n_removed += 1
            else:
                log.info(f"{n_removed} out of {n} items are enabled")
        else:
            log.warning("No items found or supplied to Dicts")

    @staticmethod
    def load_file(path: Path) -> Iterable[Dict]:
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
                contents = [json.load(f)]

            else:
                log.debug(f"Suffix {suffix} not loadable for path {full_path}")

            if contents:
                for item in contents:
                    # Add the source path for a dict to a predefined key
                    if isinstance(item, list):
                        for c in item:
                            c[PATH_KEY] = full_path
                            yield c
                    else:
                        item[PATH_KEY] = full_path
                        yield item

    def load_directory(self) -> Iterable[Dict]:
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
                for document in Dicts.load_file(path):
                    yield document

            except Exception as e:
                if not self.skip_errors:
                    raise e
                log.warning(f"Could not load {path}: {e}")
                log.exception(e)

    def mutate(self, type_: Callable[[Dict], Any]):
        """Transform the Dicts to a class or by a function"""
        self.__items: List[Any] = [type_(item) for item in self.__items]
        return self

    def filter(self, predicate: Callable[[Any], bool]):
        """Filter the Dicts according to some predicate"""
        self.__items: List[Any] = [item for item in self.__items if predicate]
        return self

    def __key(self, key: Union[Callable[[Dict], str], str], default: str) -> Callable[[Dict], str]:
        """Convenience function to convert a string to a dictionary accessor function

        Args:
            key: A grouping function to pass to itertools.groupby
                 or a dictionary key name that will be converted to an accessor

        Returns:
            A function by which a dictionary can be grouped
        """
        return lambda d: d.get(key, default) if isinstance(key, str) else key

    def key_by(
        self, key: Union[Callable[[Dict], str], str], default: str, map: bool
    ) -> Iterable[Tuple[str, List[Any]]]:
        """
        Keys a list of dicts by a function or dictionary key.
        If the key should result in a map (a 1-1 mapping) and does not,
        key_by will throw an error

        Args:
            key: To be converted to a grouper function
            default: The default grouping if the group function returns None
                     for an element
            map: If the key_by should result in a map (i.e., a 1-1 mapping )

        Returns:
            A dictionary
        """
        self.keyed = True
        _key = self.__key(key, default)
        sorted_items = sorted(self.__items, key=_key)
        for k, v in groupby(sorted_items, key=_key):
            items = list(v)
            n = len(items)
            if n > 1:
                head, *_ = items
                msg = f"Key {head[PATH_KEY]} has {n} elements"
                if map:
                    log.error(msg)
                    raise ValueError(msg)
                else:
                    log.info(msg)
            yield (k, items)

    def map_by(self, key: Union[Callable[[Dict], str], str], default: str) -> Dict[str, Any]:
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
        grouped_items = self.key_by(key=key, default=default, map=True)
        return {k: head for (k, (head, *_)) in grouped_items}

    def key_by_file(self) -> Dict[str, List[Any]]:
        """Groups the supplied dicts by filepath"""
        grouped_items = self.key_by(key=PATH_KEY, default=DEFAULT_PATH_KEY, map=False)
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
