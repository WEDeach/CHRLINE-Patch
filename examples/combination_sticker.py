# -*- coding: utf-8 -*-
"""
發送組合貼圖.

至多 6 個貼圖, 只要參數有誤都是回應 Code:20737.
輸入 ".csstk" 即可查看效果
截至2024/05/13 WIN版並未支持組合貼圖, 但可以使用API發送
此舉可能導致封禁帳號, 請自行使用可信任device與version.
"""
from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.helpers.bulders.combinations_sticker import CombinationSticker

# login
cl = CHRLINE(device="DESKTOPWIN", version="8.7.0.3302", forceTMCP=True, useThrift=True)

# init hooks
tracer = HooksTracer(
    cl,  # main account
    prefixes=["!", ".", "?", "/"],  # cmd prefixes
    db="DearSakuraBotV2",  # database name, if None will use main account's mid
    accounts=[],  # sub accounts,
    db_type=2,
)


class OpHook(object):
    @tracer.Operation(25)
    def sendMessage(self, op, cl):
        msg = op.message
        self.trace(msg, self.HooksType["Content"], cl)

    @tracer.Operation(26)
    def recvMessage(self, op, cl):
        msg = op.message
        self.trace(msg, self.HooksType["Content"], cl)


class ContentHook(object):
    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        text = msg.text
        hooked = self.trace(msg, self.HooksType["Command"], cl)


class NormalCmd(object):
    @tracer.Command(ignoreCase=True)
    def csstk(self, msg, cl):
        """CSSTK"""
        cs = CombinationSticker.new()
        l1 = cs.new_layout_info(426, 426, 32, 0, 680)
        l2 = cs.new_layout_info(426, 426, 122, 228, 980)
        s1 = cs.new_layout_sticker_info(52002735, 11537, stickerOptions="A")
        s2 = cs.new_layout_sticker_info(52002736, 11537, stickerOptions="A")
        cs.add_sticker_layout(l1, s1)
        cs.add_sticker_layout(l2, s2)
        a = cl.createCombinationSticker(cs)
        cl.replyMessage(msg, None, contentType=7, contentMetadata={"CSSTKID": a.val_1})


# run bot
tracer.run(
    2,
    **{
        'initServices': [5]
    }
)
