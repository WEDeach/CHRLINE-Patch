# LINE DemoS Bot - CHRLINE API

---

## Login

You can use SQR/AuthToken and Phone number to login.

### By AuthToken

```py
cl = CHRLINE(
  Token,
  device="ANDROID",  # device type name
  version="15.7.1",  # device app version
)
```

### By Phone number

```py
cl = CHRLINE(
  phone=PhoneNumber,  # phone number
  region="TW",        # phone number region with ISO-3166
)
```

### By SQR

```py
cl = CHRLINE()
```

## Run by LongPolling

You can use `HooksTracer` to do long polling.

Let's first look at some simple commands and event registration!

### Register HooksTracer

```py
from CHRLINE.hooks import HooksTracer

tracer = HooksTracer(
    cl,             # CHRLINE client
    prefixes=["!"], # cmd prefixes
)
```

### Register LongPolling Event

```py
@tracer.Operation(26)
def recvMessage(self, op, cl):
    msg = op[20]

    self.trace(msg, self.HooksType["Content"], cl)
```

The only thing worth noting is that the decorator uses an Enum called [OpType](https://github.com/DeachSword/CHRLINE-Thrift/blob/84da2c193fcf613639e1293b7f471e2b0957ebeb/subs/Types.thrift#L611)
In this example, `26` represents `RECEIVE_MESSAGE`, which means that it only receives events where someone else sends a message.

#### All Events

You can use the `Before` and `After` decorators to debugging

```py
@tracer.Before(tracer.HooksType["Operation"])
def __before(self, op, cl):
    # handle all op
    pass

@tracer.After(tracer.HooksType["Operation"])
def __after(self, op, cl):
    # handle not tracked op
    pass
```

### Message Content

Same usage as `Operation`, here it represents [ContentType](https://github.com/DeachSword/CHRLINE-Thrift/blob/84da2c193fcf613639e1293b7f471e2b0957ebeb/subs/Types.thrift#L783)
In this example, `0` represents `TEXT`

```py
@tracer.Content(0)
def TextMessage(self, msg, cl):
  self.trace(msg, self.HooksType["Command"], cl)
```

### Register Commands for Text contents

If you have registered the Text Content tracker, when someone types `hi`, you will reply `Hi!`

```py
@tracer.Command(ignoreCase=True, toType=[0, 2, 4])
def hi(self, msg, cl):
    cl.replyMessage(msg, f"Hi!")
```

And you can also use alt to set command aliases

```py
@tracer.Command(alt=["hello"], ignoreCase=True, toType=[0, 2, 4])
def hi(self, msg, cl):
    cl.replyMessage(msg, f"Hi!")
```

BTW, `toType` is represents [MIDType](https://github.com/DeachSword/CHRLINE-Thrift/blob/84da2c193fcf613639e1293b7f471e2b0957ebeb/subs/Types.thrift#L730C6-L730C14)
It specified that the message where came from

### Run

Once you have set up your tracker, you can start call run!

#### Run by Push

```py
tracer.run(
  2,
  **{
      'initServices': [1, 3, 6, 8, 10]
  },
)
```

`initServices` means the service you will poll, the number represents the `PushType`

If your account does not support `OpenChat(Square)`, just remove `3`

#### Run by normal

Depending on the device you are logged in, you may not be able to use the `PUSH` endpoint for long polling

```py
tracer.run()  # for normal
```
