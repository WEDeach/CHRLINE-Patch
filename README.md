# LINE DemoS Bot - CHRLINE API

![logo](/examples/assets/logo.png)

## What's up
Since `CHRLINE` has been archived, I will update it in my own name as `CHRLINE-Patch`

#### What is my original intention?
CHRLINE is supposed to be a library for **debugging**
But as time went by, many users began to ask questions about risk control and API service restrictions, which means it could be used for any business activity.
**Finally**, I decided not to update CHRLINE after 2023/09/19
And archived the library on 11/20 of the same year

#### So why?
This is not `CHRLINE`, this is `CHRLINE-Patch`
So I think I'll keep updating it :)

---
What is CHRLINE?
> It is LINE Chrome API, just for debug

If you can help update this project
Welcome join our [Discord](https://discord.gg/vQrMbjA)

## About Project
This project is for debug only, because it does not use thrift

So I don't recommend you to use this to run the bot, even if it has many functions

## What can it do?
If you have a certain degree of understanding of Line thrift, then you must have heard of **TMoreCompact** \
But for most people, it is difficult to decompile TMoreCompact, even if it has lower confusion in some version \
But if you can use this project to understand the differences in LINE thrift

## v2.6.0 Updates

由於一些原因, 在此版本中已移除所有相關的域名, 敬請悉知

另外, 本庫並非官方API, 使用任何第三方API都會導致帳號封禁風險, 為確保你了解使用本庫將導致你的帳號被封禁, 使用默認參數並不會使你"安全"的使用它, 所以`config.py`並不會再得到任何應用版本上更新

再者, 本庫默認使用部分已預定義的thrift結構, 請參閱 [CHRLINE-Thrift](https://github.com/DeachSword/CHRLINE-Thrift), 但本庫"不會也不應該"同步這些變化, 所以若你想使用它們, 請自行編譯並提供路徑至`genThriftPath`

## 版本變化

此庫通常以一個中間版本來詮釋重點改變(1.0.7 -> 1.1.0)
以一個大版本來詮釋重大改變(1.5.2 -> 2.0.0)

起初本庫是依於LINE Chrome版本反編譯而成, 使用`x-le`以及`x-lcs`來進行請求

後來在[1.4.0](https://github.com/DeachSword/CHRLINE/commit/d7d8430e74417a06c9ad159a5675b7787ec75c54)中實現了`TMoreCompact`協議, 這是LINE在2013(可能更早)導用的專屬thrift緊湊協議, 你可以在[這裡查看那是甚麼](/docs/TMoreCompact.md)
在`2.0.0`中導用了thrift原生庫, 你可以使用`useThrift`來轉換Dict至已定義的thrift類型
在`2.5.0`中實現了`/PUSH`端點的支持, 它類似於SPDY, 用於HTTP2的長輪詢(但它不使用*Server Push* :v)

**在這個時候LINE Chrome有重大改變, 此庫已不完全支持`CHROMEOS`**

---

在`2.6.0`中(*當前版本*) 添加`DummyThrfit`, 它更方便的檢查當前已定義的thrift缺失了哪些Field, 對於LINE版本更新很有幫助. 與此同時, 也同時支持了[E2EE Next](https://github.com/WEDeach/CHRLINE-Patch/commit/b3da065209ee4e7a4f8e00e82c96a8b8245d2465#diff-efc570a8ac227398796cf43d8035cb624fa9d94bc8bfedd01922cddb2f838fa3R2), 如果你不知道那是甚麼, 在[這裡查看](/docs/E2EE_Next.md)它!
> [!CAUTION]
> v2.6.0 移除了 `cube.py` 以及 `timeline.py`, 並將其重寫為 BIZ 服務, 整體架構有大幅度的改變!

## Requirement

- Python 3.6 (v2.6.0 changed to 3.8)
  - pycryptodome
  - xxhash
  - rsa
  - requests
  - httpx[http2]
  - ~~gevent~~  (v2.6.0 removed)
  - python-axolotl-curve25519
  - cryptography
  - thrift
  - qrcode
  - Image
  - rich

## Thanks

This project got their help directly/indirectly, thank them deeply

- [fadhiilrachman](https://github.com/fadhiilrachman)
- [ii64](https://github.com/ii64)
- [ドマオー](https://github.com/Dosugamea)
- [Zero Cool](https://github.com/crash-override404)
- [sakura](https://github.com/sakura-rip)
- [ぐるぐる](https://github.com/f0reachARR)
- LINE *GUILTY CROWN LOST XMAS* & *Hey LINE!* 's group members
- Discord *DemoS*'s group members
- [Modernfarm 🧧](https://github.com/fakefate14)
- [よう](https://github.com/terran-yj4)
- [shion](https://github.com/q0jt)
- **SLOT**
