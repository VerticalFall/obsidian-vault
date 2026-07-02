# 每日报告(自动同步)

这个文件夹是一个独立的 Git 仓库,与 GitHub 上的 [`VerticalFall/obsidian-vault`](https://github.com/VerticalFall/obsidian-vault) 关联。

## 工作方式

```
公开信息源仓库 ──[GitHub Action 每日抓取]──► obsidian-vault 仓库 ──[本地 git pull]──► 这个文件夹
```

- **内容来源**:由 GitHub 上的定时 Action 每天自动从各信息源仓库抓取当天报告并提交。
- **本地作用**:纯消费端,每天 `git pull` 拉取最新报告到本地 Obsidian 阅读。

## 注意事项

- ⚠️ **不要手动编辑本文件夹里由 Action 生成的报告**,否则下次 `git pull` 可能产生冲突。
- 本文件夹与 vault 里的个人笔记(英硕课程、投资理念等)**完全隔离**——那些内容不在 git 管辖内,不会被上传。
- 如需保留自己的批注,建议在 vault 其他位置另建笔记引用报告,而非直接改动。
