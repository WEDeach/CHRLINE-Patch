from functools import wraps
from typing import Callable, Dict, Optional


class HookTypes(object):
    def __init__(self):
        super().__init__()
        self.OABotFuncs: Dict[str, Callable[..., None]] = {}
        self.opFuncs = []
        self.contFuncs = []
        self.cmdFuncs = []
        self.beforeFuncs = []
        self.afterFuncs = []

    def Event(self, func):
        setattr(self.eventFuncs, func.__name__, func)
        return func

    def Operation(self, type: int):
        def __wrapper(func):
            @wraps(func)
            def __check(self, *args):
                op = args[0]
                opType = self.cl.checkAndGetValue(op, "type", 3)
                if opType == type:
                    func(self, *args)
                    return True
                return False

            self.opFuncs.append(__check)

        return __wrapper

    def Content(self, type: int):
        def __wrapper(func):
            @wraps(func)
            def __check(self, *args):
                op = args[0]
                contentType = self.cl.checkAndGetValue(op, "contentType", 15)
                if contentType == type:
                    func(self, *args)
                    return True
                return False

            self.contFuncs.append(__check)

        return __wrapper

    def Command(
        self,
        permissions: list = [],
        alt: list = [],
        toType: list = [0, 1, 2],
        ignoreCase: bool = False,
        inpart: bool = False,
        prefixes: bool = True,
        splitchar: Optional[str] = None,
    ):
        """
        - permissions:
            List of permission's name.
            eg. ['admin']
        - alt:
            Sub cmds.
            eg: Command name is "GetOps", and use alt=["ops"], so u can use "GetOps" and "ops" to run the command.
        - toType:
            Only run when receives the command with the specific toType
        - ignoreCase:
            *As the name suggests*
        - inpart:
            If False, match the command that same style.
            If True, match any command that starts with command name.
        - prefixes:
            Match the prefixs.
        - splitchar:
            If not None, match the first value after the command is split by this value
        """

        def __wrapper(func):
            func.prefixes = prefixes
            func.permissions = permissions
            func.toType = toType

            @wraps(func)
            def __check(self, *args):
                def _fname(_name=None):
                    return func.__name__ if _name is None else _name
                msg = args[0]
                sender = self.cl.checkAndGetValue(msg, "_from", 1)
                receiver = self.cl.checkAndGetValue(msg, "to", 2)
                cl = args[1]
                if sender != cl.mid and not self.checkPermissions(sender, permissions):
                    return False
                msgToType = self.cl.checkAndGetValue(msg, "toType", 3)
                msgType = self.cl.checkAndGetValue(msg, "contentType", 15)
                isInpart = inpart
                if msgToType in toType:
                    if msgType == 0:
                        text = self.cl.checkAndGetValue(msg, "text", 10)
                        for __name in [None] + alt:
                            fname = _fname(__name)
                            if ignoreCase:
                                text = text.lower()
                                fname = fname.lower()
                            if splitchar is not None:
                                text = text.split(splitchar)[0]
                                isInpart = False  # force
                            isUsePrefixes = not prefixes
                            if prefixes and len(self.prefixes) > 0:
                                for _prefix in self.prefixes:
                                    if text.startswith(_prefix):
                                        fname = _prefix + fname
                                        isUsePrefixes = True
                                        break
                                if not isUsePrefixes:
                                    return False
                            if text == fname or isInpart and text.startswith(fname):
                                func(self, *args)
                                return True
                    else:
                        raise ValueError(f"wrong content type: {msgType}")
                return False

            self.cmdFuncs.append(__check)

        return __wrapper

    def SquareEvent(self, SquareEventType: int):
        def __wrapper(func):
            @wraps(func)
            def __check(self, *args):
                event = args[0]
                _type = self.cl.checkAndGetValue(event, "type", 3)
                if _type == SquareEventType:
                    if _type == 54:
                        # Thread
                        payload = self.cl.checkAndGetValue(event, "payload", 4)
                        notificationThreadMessage = self.cl.checkAndGetValue(payload, "notificationThreadMessage", 52)
                        threadMid = self.cl.checkAndGetValue(notificationThreadMessage, "threadMid", 1)
                        chatMid = self.cl.checkAndGetValue(notificationThreadMessage, "chatMid", 2)
                        squareMessage = self.cl.checkAndGetValue(notificationThreadMessage, "squareMessage", 3)
                        message = self.cl.checkAndGetValue(squareMessage, "message", 1)
                        self.cl.checkAndSetValue(message, "squareChatMid", chatMid)
                    func(self, *args)
                    return True
                return False

            self.seFuncs.append(__check)

        return __wrapper

    def OABotTyping(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        self.OABotFuncs["typing"] = wrapper
        return wrapper

    def Before(self, type: int):
        def __wrapper(func):
            func.type = type

            @wraps(func)
            def __bf(self, *args):
                func(self, *args)
                return True

            self.beforeFuncs.append(__bf)

        return __wrapper

    def After(self, type):
        def __wrapper(func):
            func.type = type

            @wraps(func)
            def __af(self, *args):
                func(self, *args)
                return True

            self.afterFuncs.append(__af)

        return __wrapper
