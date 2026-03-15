import atexit
import collections
import datetime
import functools
import inspect
import sys

_req_logs = collections.deque(maxlen=50)
_usr_logs = collections.deque(maxlen=10)


def log_request(func):
    sig = inspect.signature(func)

    def _check_user_status(self):
        if self is None:
            return
        now = {
            "ts": datetime.datetime.now(),
            "mid": getattr(self, "mid", None),
            "at": self.authToken,
            "headers": self.server.Headers
        }
        old = _usr_logs[-1] if len(_usr_logs) > 0 else None
        if old is None or old != now:
            _usr_logs.append(now)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        params = bound.arguments

        _self = params.get("self")
        data = params.get("data", None)
        _check_user_status(_self)

        entry = {
            "ts": datetime.datetime.now(),
            "req": data,
            "resp": None,
            "err": None,
        }
        try:
            res = func(*args, **kwargs)
            entry["resp"] = res
        except Exception as e:
            entry["err"] = str(e)
            raise e
        finally:
            _req_logs.append(entry)
        return res

    return wrapper


def dump_logs():
    _all = list(_usr_logs) + list(_req_logs)
    if len(_all) == 0:
        return

    _all.sort(key=lambda x: x["ts"])

    P_USR = "    "
    P_REQ = "        "

    t_uint = _all[0]["ts"].strftime("%Y%m%d%H%M%S")
    with open(f"CHReqLog_{t_uint}.txt", "wb") as f:
        _seq = 0
        for entry in _all:
            if "mid" in entry:
                f.write(b"# ----------------------------------\n")
                f.write(f"{P_USR}Date: {entry['ts'].isoformat()}\n".encode())
                f.write(f"{P_USR}Mid: {entry['mid']}\n".encode())
                f.write(f"{P_USR}AuthToken: {entry['at']}\n".encode())
                f.write(f"{P_USR}Headers: {entry['headers']}\n".encode())
                _seq = 0
            else:
                f.write(f"{P_USR}[{_seq}] ================================\n".encode())
                f.write(f"{P_REQ}Date: {entry['ts'].isoformat()}\n".encode())
                f.write(f"{P_REQ}Request: {entry['req']}\n".encode())
                if entry["resp"] is not None:
                    r = entry["resp"]
                    f.write(f"{P_REQ}Response: {r} {r.headers}\n".encode())
                    f.write(f"{P_REQ}{P_REQ}{r.content.hex()}\n".encode())
                if entry["err"] is not None:
                    f.write(f"{P_REQ}Error: {entry['err']}\n".encode())
                f.write(b"\n")
                _seq += 1


def _on_exception(exc_type, exc_value, exc_tb):
    dump_logs()
    sys.__excepthook__(exc_type, exc_value, exc_tb)


atexit.register(dump_logs)
sys.excepthook = _on_exception
