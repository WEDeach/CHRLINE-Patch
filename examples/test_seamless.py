# -*- coding: utf-8 -*-
# THIS SCRIPT IS REFS TO
#   https://canary.discord.com/channels/466066749440393216/827711705899204699/1261308927530897419
# 簡易轉換*主要令牌*至*二級令牌*

from CHRLINE import CHRLINE

cl = CHRLINE(TOKEN)

cl_sec = CHRLINE(device="WEAROS", noLogin=True)

ses = cl.checkAndGetValue(cl_sec.s_seamless_sec.createSession(), "sessionId", 1)

# 記得打上E2EE補丁在dict :)
token = cl.checkAndGetValue(cl.s_seamless.permitLogin(ses, {}), "oneTimeToken", 1)

res = cl_sec.s_seamless_sec.login(ses, "Wear OS", "Pixel Watch 3", token)

print(res)
