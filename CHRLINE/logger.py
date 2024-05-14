import logging
from rich.logging import RichHandler
from typing import List, Optional, Union


class Logger:
    def __init__(self, names: List[str]) -> None:
        self._names = names
        self.__ins: Optional[logging.Logger] = None

    @staticmethod
    def new(name: str):
        return Logger([name])

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
            l = logging.getLogger(self.key_name)
            l.parent = None
            l.name = self.name
            l.setLevel(logging.INFO)
            h = RichHandler(level=logging.NOTSET, show_path=True, rich_tracebacks=True)
            f = logging.Formatter("%(name)s %(message)s")
            f.datefmt = "[%Y/%m/%d %X]"
            h.setFormatter(f)
            l.handlers = [h]
            self.__ins = l
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
