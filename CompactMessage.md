# CompactMessage

`CompactMessage` 是一個簡潔的 `Message` 結構, 這被用於 `/CA5` 這種端點.

---

## Compact Message Struct

`CompactMessage` 的結構看起來像這樣:

 Bytes   | Field Name | Description                  | 示例值
---------|------------|------------------------------|-----------
1 bytes  | MID Type   | Message `to` mid type        | 0
1 bytes  | CM Type    | Compact message type         | 2
? bytes  | SEQ        | Request seq                  | 19234
16 bytes | Hex2Bytes  | Message `to` {1:33} to bytes | ff69a9...

接著若是 `TEXT_V2` 則寫入 Message `text`
再來寫入 `EMOTICON_VER` (在我印象中一直都為 `4`)
--- 到這裡則是 `TEXT_V2` 的結尾.

若是 `E2EE_TEXT_V1` 則寫入 Message `chunks` (這是陣列, 照順序寫入即可)
--- 到這裡則是 `E2EE_TEXT_V1` 的結尾.

## Compact Message Type

`CompactMessage` 的類型不同於一般的 `Message` 中的 `contentType`:

CM Type | Type Name           | Description  
--------|---------------------|-------------
-1      | NOT_COMPACT_MESSAGE | 不支援
1       | TEXT_V2             | 用於一般文字訊息
2       | STICKER_V2          |
5       | E2EE_TEXT_V1        | 用於E2EE文字訊息
6       | E2EE_LOCATION_V1    | 用於E2EE位置訊息
