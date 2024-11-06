# LINE TMoreCompact

>What is TMoreCompact?\
It is custom thrift by LINE\
It has more powerful compression than TCompact

## When did it appear?

First appeared in LINE 7.X\
And in the current Android version (11.2.2), it is used in /P5 and /C5\
For two func: **fetchOps** and **sendMessage**

## Why?

They have more powerful compression, and the bytes will be greatly reduced, giving it a faster transmission speed.\
In fetchOps, the effect is more obvious\
If the user has many chat messages, he will get 50 or more Ops at the one time, and this will increase the bytes of a single request and affect its response\
and TMoreCompact is to reduce the situation, it will greatly compress its bytes :p

## 主要實現流程

該協議主要增加了全新的Field類型:

- `16`: 該類型用於可轉為數字的字串
  - 例如`53217949545005099`
    - 在原類型`11` 它會是將近18字節以上(長度+內容)
    - 在此類型`16` 它僅9字節(視為數字編碼, *可能更大*)
- `17`: 該類型用於MID(LINE內部識別符)
  - 許多資料會包含MID, 例如User, ChatGroup, OpenChat...
    - 在原類型`11` 它會是33字節(識別符類型+識別符ID)
    - 在此類型`17` 它僅1字節(作為Index, *可能更大*)

而這兩個變化大大改善了原有的緊湊協議, 在協議的架構上也帶來了些許不同  
例如類型`17`使用了數字做為Index, 此舉衍伸了我們必須在`readMessageBegin`中解析MID Table, 這大大改善了MID重用問題  
實際的實現可參考[thrift.py](/CHRLINE/thrift.py)中的`TMoreCompactProtocol`
