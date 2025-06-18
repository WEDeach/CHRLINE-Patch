# -*- coding: utf-8 -*-
import threading
import traceback
from typing import Optional

from .helper import ChrHelperProtocol


class Poll(ChrHelperProtocol):
    def __init__(self):
        self.subscriptionId: Optional[int] = 0
        self.eventSyncToken: Optional[str] = None
        self.__logger = self.client.get_logger("POLL")

    def __fetchOps(self, count=100):
        fetchOps = self.client.fetchOps
        if self.client.DEVICE_TYPE in self.client.SYNC_SUPPORT:
            fetchOps = self.client.sync
        ops = fetchOps(self.revision, count)
        if isinstance(ops, dict) and "error" in ops:
            raise Exception(ops["error"])
        elif not isinstance(ops, list):
            raise ValueError(f"ops should be list: {ops}")
        for op in ops:
            opType = self.client.checkAndGetValue(op, "type", 3)
            if opType != -1:
                self.setRevision(self.client.checkAndGetValue(op, "revision", 1))
            yield op

    def __fetchMyEvents(self, count: int = 100, initLastSyncToken: bool = False):
        resp = self.client.fetchMyEvents(
            self.subscriptionId, self.eventSyncToken, limit=count
        )
        events = self.client.checkAndGetValue(resp, "events", 2)
        if not isinstance(events, list):
            raise ValueError(f"events should be list: {events}")
        for event in events:
            syncToken = self.client.checkAndGetValue(event, "syncToken", 5)
            self.setEventSyncToken(syncToken)
            yield event
        if initLastSyncToken:
            syncToken = self.client.checkAndGetValue(resp, "syncToken", 3)
            if syncToken is not None and not isinstance(syncToken, str):
                raise ValueError(f"syncToken should be str: {syncToken}")
            self.setEventSyncToken(syncToken)

    def __execute(self, op, func):
        try:
            func(op, self)
        except Exception:
            self.__logger.exception(traceback.format_exc())

    def setRevision(self, revision):
        if revision is None:
            self.__logger.warn("revision is None!!")
            revision = 0
        self.revision = max(revision, self.revision)

    def setEventSyncToken(self, syncToken: Optional[str]):
        if syncToken is None:
            self.__logger.warn("syncToken is None!!")
            syncToken = ""
        if self.eventSyncToken is None:
            self.eventSyncToken = syncToken
        else:
            if syncToken is not None:
                self.eventSyncToken = str(max(int(syncToken), int(self.eventSyncToken)))

    def trace(self, func, isThreading=True):
        while self.client.is_login:
            for op in self.__fetchOps():
                opType = self.client.checkAndGetValue(op, "type", "val_3", 3)
                if opType != 0 and opType != -1:
                    if isThreading:
                        _td = threading.Thread(target=self.__execute, args=(op, func))
                        _td.daemon = True
                        _td.start()
                    else:
                        self.__execute(op, func)
