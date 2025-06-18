import logging
import re
from typing import Dict, List, Optional, Tuple, Union

from rich.logging import RichHandler

root = logging.RootLogger(logging.INFO)
h = RichHandler(
    level=logging.NOTSET, show_path=True, rich_tracebacks=True,
)
f = logging.Formatter("%(display_name)s %(message)s")
f.datefmt = "[%Y/%m/%d %X]"
h.setFormatter(f)
root.handlers = [h]


loggers: Dict[str, logging.Logger] = {}

def root_handle(record):
    dn = ""
    for n in record.name.split("."):
        dn += f"[{n.replace(' ', '_')}]"
    record.display_name = dn
    super(logging.RootLogger, root).handle(record)

class Logger:
    def __init__(self, names: List[str]) -> None:
        self._names = names
        self.__ins: Optional[logging.Logger] = None

    @classmethod
    def new(cls, name: str):
        return Logger([name])

    def overload(self, *names: str):
        """Overload logger by sub-names."""
        ns = self._names + list(names)
        return Logger(ns)

    @property
    def key_name(self):
        return ".".join(self._names)

    @property
    def name(self):
        s = ""
        for n in self._names:
            s += f"[{n.replace(' ', '_')}]"
        return s

    @property
    def ins(self):
        if not self.__ins:
            if self.key_name not in loggers:
                r = logging.getLogger(self.key_name)
                r.parent = root
                r.name = self.key_name
                r.handle = root_handle
                loggers[self.key_name] = r
            else:
                r = loggers[self.key_name]
            self.__ins = r

        return self.__ins

    @property
    def debug(self):
        return self.ins.debug

    @property
    def info(self):
        return self.ins.info

    @property
    def warning(self):
        return self.ins.warning

    @property
    def warn(self):
        return self.ins.warn

    @property
    def error(self):
        return self.ins.error

    @property
    def exception(self):
        return self.ins.exception

    @property
    def critical(self):
        return self.ins.critical

    @property
    def log(self):
        return self.ins.log

    def set_level(self, level: Union[str, int]):
        self.ins.setLevel(level)

    def set_root_level(self, level: Union[str, int]):
        """Set root-logger level."""
        root.setLevel(level)

    def add_log_fliters(self, *names: str):
        """Set root-logger level."""
        filter1 = NsFliter(ns=names)
        h.addFilter(filter1)

class NsFliter(logging.Filter):
    def __init__(self, ns: Tuple[str]):
        self.ns = ns

    def filter(self, record):
        for n in self.ns:
            pattern = re.compile(n, re.IGNORECASE)
            if bool(pattern.match(record.name)):
                return True
        return False