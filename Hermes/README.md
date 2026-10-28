# Hermes 工作区模板

本目录提供人格、用户画像与长期记忆的初始模板，不包含 Hermes Cron 配置。

## 目录结构

```text
Hermes/
├── README.md
└── workspace-template/
    ├── SOUL.md
    └── memories/
        ├── USER.md
        └── MEMORY.md
```

## 使用方式

1. 确认目标 Hermes home：默认是 `~/.hermes/`；使用自定义 home 或 profile 时，以目标实例的 `$HERMES_HOME` 为准，不要覆盖其他 profile。
2. 备份目标文件，再按需将 `workspace-template/` 中的文件复制或合并到目标 home，保持相对路径不变。不要直接覆盖已经积累的用户画像和长期记忆。
3. 修改 `SOUL.md` 中的人格与工作区约定，填写 `memories/USER.md` 的名称、称呼、时区等信息；`Asia/Shanghai` 仅为示例时区。`memories/MEMORY.md` 留作长期记忆的初始骨架。
4. 开启新会话，使更新后的文件被加载。

目标路径分别为 `$HERMES_HOME/SOUL.md`、`$HERMES_HOME/memories/USER.md` 和 `$HERMES_HOME/memories/MEMORY.md`。`SOUL.md` 中的 `~/.hermes` 是默认 home 示例，使用其他 home 时请同步调整。

## 文件职责与注意事项

- `SOUL.md`：人格、交流方式与工作区管理约定；其中的目录分类与保留周期是本模板的约定，不代表框架强制要求，也不会自动创建目录或定时任务。
- `memories/USER.md`：用户画像和偏好，发布模板时只保留通用骨架或占位符。
- `memories/MEMORY.md`：长期保留的环境事实与约定，后续可由 Hermes 的 `memory` 工具维护。
- 不要把真实凭据、私人资料、聊天记录或实际运行中的记忆文件提交到公共仓库。
- 本次提供的是文件模板；不需要修改正在运行的 Hermes 配置。

## 官方参考

- [文件职责与加载位置](https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what)
- [持久记忆](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
