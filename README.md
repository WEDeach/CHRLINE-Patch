# LINE DemoS Bot - CHRLINE API

>What is CHRLINE?\
>It is LINE Chrome API, just for debug

>If you can help update this project, \
Welcome join our [Discord](https://discord.gg/vQrMbjA)

## About Project
This project is for debug only, because it does not use thrift

So I don’t recommend you to use this to run the bot, even if it has many functions

## What can it do?
If you have a certain degree of understanding of Line thrift, then you must have heard of **TMoreCompact** \
But for most people, it is difficult to decompile TMoreCompact, even if it has lower confusion in some version \
But if you can use this project to understand the differences in LINE thrift
\
####  Example
```
from CHRLINE import *

cl = CHRLINE() # login

print('/S3 - len: %s' % len(cl.testTBinary()))
print('/S4 - len: %s' % len(cl.testTCompact()))
print('/S5 - len: %s' % len(cl.testTMoreCompact()))
```
####  Result
```
> /S3 - len: 576
> /S4 - len: 528
> /S5 - len: 496
```
This shows that TMoreCompact has the best compression\
If you want to write TMoreCompact, only need to sniff results and reverse engineer

####  Requirement
- Python 3
    - pycrypto
    - xxhash
    - httpx[http2]

## Function overview
- SQR 
- Services
    - TalkService
        - getEncryptedIdentity
        - getContact
        - getContacts
        - getGroup
        - getGroups
        - getGroupsV2
        - getCompactGroup
        - getChats
        - sendMessage
            - sendContact
            - sendLocation
        - getGroupIdsJoined
        - getGroupIdsInvited
        - getAllContactIds
        - getBlockedContactIds
        - getBlockedRecommendationIds
        - getAllReadMessageOps
        - getLastOpRevision
        - getServerTime
        - getConfigurations
        - fetchOps
        - deleteOtherFromChat
        - cancelChatInvitation
        - acceptChatInvitation
        - getContactsV2
        - acceptChatInvitationByTicket
        - getPreviousMessagesV2WithRequest
        - sendChatChecked
        - unsendMessage
        - findAndAddContactsByMid
        - inviteIntoChat
        - deleteSelfFromChat
        - findChatByTicket
        - updateChat
        - sendPostback
        - wakeUpLongPolling
        - getMessageBoxes
        - getMessageReadRange
        - getChatRoomAnnouncementsBulk
        - removeChatRoomAnnouncement
        - fetchOperations
        - unblockContact
        - blockContact
        - acquireEncryptedAccessToken
        - getCountries
        - createRoomV2
        - createChatRoomAnnouncement
        - getAllChatMids
        - reissueChatTicket
    - ShopService
        - getProduct
        - getProductsByAuthor
        - getStudentInformation
    - LiffService
        - issueLiffView
        - getLiffViewWithoutUserContext
        - sendLiff
    - ObsService
        - forwardObjectMsg
        - trainingImage
    - Others
        - issueChannelToken
        - getChannelInfo
        - returnTicket (test)
        - getModulesV2
        - markAsRead
        - setClovaCredential (test)
        - getCommonDomains
        - acquireCallRoute
        - acquireGroupCallRoute
        - acquireOACallRoute
        - acquireTestCallRoute
        - inviteIntoGroupCall
        - issueRequestTokenWithAuthScheme
        - openSession
        - connectEapAccount
        - verifyEapLogin
        - inviteIntoSquareChat
        - inviteToSquare
        - getJoinedSquares

