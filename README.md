# rime-files

我的 Rime 配置文件和词库。

使用的是 Windows 小狼毫输入法。

文件位于本仓库的 [`files`](./files) 目录。

以下内容将引用两个仓库：

- “Rime 官方五笔输入方案”：[rime/rime-wubi](https://github.com/rime/rime-wubi)。
- “扩展区汉字码表”：[LS-Hower/rime-wubi86-ext](https://github.com/LS-Hower/rime-wubi86-ext)。

## 包含的文件

- `default.custom.yaml`
- `symbols.custom.yaml`
- `weasel.custom.yaml`
- `wubi86.custom.yaml` —— 对 Rime 官方五笔输入方案（见上方引用）的补丁。
- `wubi86.schema.yaml` —— Rime 官方五笔输入方案（见上方引用）。
- `dicts/`
    - `partial-wubi86.custom.yaml` —— 是 Rime 官方五笔（见上方引用）自带词库 `wubi86.dict.yaml` 的副本。除了对文件头部（`...` 之前的部分）作了修改之外，对于字词部分，只对“特性”和“我”、“兔子”和“句子”两对字词做过重排。这里只上传文件头部，不再上传字词部分。
    - `wubi86.109.dict.yaml` —— 其实是扩展区汉字码表项目中 `wubi86.extext.dict.yaml` （各汉字区的扩展部分）的前身。包含了一些曾经打错的外码。
    - `wubi86.hower.dict.yaml` —— 为 Rime 官方五笔（见上方引用）自带词库添加的字词。
    - `wubi86.skana.dict.yaml` —— 一种将日文假名融入五笔词库的思路，将五笔的规则应用在假名的字形上。太抽象了所以没有用。
    - `wubi86.touhou.dict.yaml` —— 东方 Project 相关字词。
    - `wubi86.yijian_ext.dict.yaml` —— 将更多常用字放入一级简码的尝试。
    - `wubi86.zkana.dict.yaml` —— 另一种将日文假名融入五笔词库的思路。 `z` 后跟罗马字，即可输入假名。

## 不包含的文件

以下文件不包含在本仓库中。

- `default.yaml`
- `installation.yaml`
- `symbols.yaml`
- `user.yaml`
- `weasel.yaml`
- 用户输入习惯词库（各种 `userdb` ）。
- `wubi86.dict.yaml` —— Rime 官方五笔输入方案（见上方引用）自带词库。
- `wubi86.hower_private.dict.yaml` —— 明确不打算公开的字词。数量较少。

以下文件包含在另一个仓库中，就是扩展区汉字码表（见上方引用）。

- `wubi86.basiccmpl.dict.yaml`
- `wubi86.extacmpl.dict.yaml`
- `wubi86.extbcmpl.dict.yaml`
- `wubi86.extc.dict.yaml`
- `wubi86.extccmpl.dict.yaml`
- `wubi86.extd.dict.yaml`
- `wubi86.exte.dict.yaml`
- `wubi86.extext.dict.yaml`
- `wubi86.extf.dict.yaml`
- `wubi86.extg.dict.yaml`
- `wubi86.exth.dict.yaml`

它们是仍在更新的扩展区五笔词库。（虽然这个项目已经摆了至少一年半了，2025-12-26 留）
