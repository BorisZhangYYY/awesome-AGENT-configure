# AI-ProjConf

> 通用项目初始化模板集合，按项目形态分为两类。

## 两类模板

| 目录 | 适用场景 | 特征 |
|------|----------|------|
| `zh_CN/single-repo/` | 独立开发者 / 单仓库项目 | 根目录即 git 仓库；`CLAUDE.md` 等规范文件纳入版本控制 |
| `zh_CN/multi-repo/` | 大型项目 / 微服务工作区 | 根目录不做版本控制，子目录为独立 git 仓库；`CLAUDE.md` 为本机工作台账 |

## 使用方式

将对应目录下的 `*.example` 去掉 `.example` 后缀，放入项目根目录，替换 `{{占位符}}` 后使用。

## 目录结构

```
zh_CN/
├── single-repo/          # 单仓库模板
│   ├── AGENTS.md.example
│   ├── CHANGELOG.md.example
│   ├── CLAUDE.md.example
│   ├── README.md.example
│   ├── TODO.md.example
│   └── .project/.gitkeep
└── multi-repo/           # 微服务工作区模板
    ├── AGENTS.md.example
    ├── CLAUDE.md.example
    ├── .docs/.gitkeep
    └── .project/
        ├── .gitkeep
        └── env/.gitkeep
```
