# Dummy Protocol

Easy to generate `TField` using a list.

---

## How to write DummyProtocol?

for `fetchOps`, it like:

```py
params = [
    [10, 2, revision],
    [8, 3, count],
    [10, 4, self.globalRev],
    [10, 5, self.individualRev]
]
```

### How do I know the parameters of these requests?

that is very easy if you can decompilation.

![](/examples/assets/2021-08-24_145129.png)

you can see strings and numbers that represent the name, type, and ID, respectively. All of these come from the type `a9.a.b.t.b`, which is an obfuscated `TField`

so `("localRev", (byte) 10, 2)` can be written as `[10, 2, {data}]` for `DummyProtocol`

Type | for waht | example |
---- | -------- | ------- |
| 1-11 | scalar | `[10, 2, {data}]`
| 12 | sturct | `[12, 1, [{DummyProtocol datas}]]`
| 13 | map | `[13, 1, [{MAP Key Type}, {MAP Val Type}, {Dict data}]]`
| 14-15 | sequential | `[15, 1, [{LIST Val Type}, {List data}]]`
