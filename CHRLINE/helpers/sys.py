# -*- coding: utf-8 -*-
from .base import BaseHelper


class SysHelper(BaseHelper):
    def __init__(self):
        pass

    def getToType(self, mid: str):
        """
        Get mid type.

        USER(0),
        ROOM(1),
        GROUP(2),
        SQUARE(3),
        SQUARE_CHAT(4),
        SQUARE_MEMBER(5),
        BOT(6);
        SQUARE_THREAD(7);
        """
        _u = mid[0]
        if _u == "u":
            return 0
        if _u == "r":
            return 1
        if _u == "c":
            return 2
        if _u == "s":
            return 3
        if _u == "m":
            return 4
        if _u == "p":
            return 5
        if _u == "v":
            return 6
        if _u == "t":
            return 7
        raise ValueError("Mid type not found: {mid}")

    def checkRespIsSuccessWithLpv(self, resp, lpv: int = 1, status_code: int = 200):
        ckStatusCode = lpv != 1
        if lpv == 1:
            if "x-lc" in resp.headers:
                if resp.headers["x-lc"] != str(status_code):
                    return False
            else:
                ckStatusCode = True
        if ckStatusCode:
            if resp.status_code != status_code:
                return False
        return True

    def checkIsVideo(self, filename: str):
        video_suffix = [".mp4", ".mkv", ".webm"]
        for _vs in video_suffix:
            if filename.endswith(_vs):
                return True
        return False

    @staticmethod
    def checkAndGetValue(value, *args):
        for arg in args:
            if type(value) == dict:
                if arg in value:
                    return value[arg]
            else:
                data = getattr(value, str(arg), None)
                if data is not None:
                    return data
                if isinstance(arg, int):
                    data = getattr(value, f"val_{arg}", None)
                    if data is not None:
                        return data
        return None

    @staticmethod
    def checkAndSetValue(value, *args):
        set = args[-1]
        args = args[:-1]
        if not args:
            raise ValueError(f"Invalid arguments: {args}")
        for arg in args:
            if type(value) == dict:
                value[arg] = set
            else:
                setattr(value, str(arg), set)
        return value
