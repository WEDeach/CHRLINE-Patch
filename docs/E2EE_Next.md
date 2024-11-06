# E2EE Next

在2023年年底(可能更早), LINE終於新增了媒體的E2EE加密.  
你可以在[這裡](https://canary.discord.com/channels/466066749440393216/827711705899204699/1184735725166526474)查看我們開發時的討論(**請確保你已經加入伺服器並領取特定身分組!**)  

---

在此之前, LINE的媒體並**不支持**E2EE!  
而E2EE Next則是只應用於媒體: 圖片, 影片, 聲音以及檔案  

主要實現方式是將媒體使用`AES-CTR`進行加密後上傳至OBS(視為`FILE`)  
媒體上傳後, 則將加密時使用的`Key Material`以`E2EE V2`加密後並發送訊息  

## Refs

* [deriveKeyMaterial](https://github.com/WEDeach/CHRLINE-Patch/blob/b3da065209ee4e7a4f8e00e82c96a8b8245d2465/CHRLINE/e2ee.py#L523)
* [encryptByKeyMaterial](https://github.com/WEDeach/CHRLINE-Patch/blob/b3da065209ee4e7a4f8e00e82c96a8b8245d2465/CHRLINE/e2ee.py#L535)
* [encryptByKeyMaterial](https://github.com/WEDeach/CHRLINE-Patch/blob/b3da065209ee4e7a4f8e00e82c96a8b8245d2465/CHRLINE/e2ee.py#L544)
* [uploadMediaByE2EE](https://github.com/WEDeach/CHRLINE-Patch/blob/b3da065209ee4e7a4f8e00e82c96a8b8245d2465/CHRLINE/object.py#L933)

examples: [test_e2ee_img.py](https://github.com/WEDeach/CHRLINE-Patch/blob/b3da065209ee4e7a4f8e00e82c96a8b8245d2465/examples/e2ee_next/test_e2ee_img.py)