# AI-ProjConf

> 通用项目初始化模板集合：把 AGENT 协作所需的项目规范、任务跟踪与文档结构一次配好。

简体中文 | [English](README.en.md)

## 两类模板

| 目录 | 适用场景 | 特征 |
|------|----------|------|
| `zh_CN/single-repo/` | 独立开发者 / 单仓库项目 | 根目录即 git 仓库；`CLAUDE.md` 等规范文件纳入版本控制 |
| `zh_CN/multi-repo/` | 大型项目 / 微服务工作区 | 根目录不做版本控制，子目录为独立 git 仓库；`CLAUDE.md` 为本机工作台账 |

英文版位于 `en_US/single-repo/` 与 `en_US/multi-repo/`，结构与中文版一一对应。

## 模板内容

| 文件 | 用途 |
|------|------|
| `CLAUDE.md.example` | 项目规范入口：项目简介、架构规范、环境索引、任务跟踪、开发与提交规范 |
| `AGENTS.md.example` | AGENT 引导文件，指向 `CLAUDE.md` |
| `README.md.example` | 项目 README 骨架（single-repo） |
| `CHANGELOG.md.example` | 变更日志骨架，遵循 Keep a Changelog（single-repo） |
| `TODO.md.example` | 待办索引，正文放 `.project/` |
| `.docs/` | 面向使用者的业务/部署文档 |
| `.project/` | 仓库内部开发细则 |
| `.project/env/` | 按环境拆分的连接信息：`test.md` / `uat.md` / `prd.md` |

## 任务跟踪与环境配置

- 每个任务在 `.project/` 下建 `YYYYMMDD-<主题>/` 目录，正文以主题命名。
- 同一主题的后续任务并入已有目录，用 `01-问题讨论` 等序号子目录区分步骤。
- 根 `TODO.md` 只做索引：「未完成」加一行链接，完成后移入「已完成/归档」并加 `### ✅`。
- 环境连接信息写入 `.project/env/`，并在 `CLAUDE.md` 的「环境索引」中登记。

## 使用方式

将对应目录下的 `*.example` 去掉 `.example` 后缀，放入项目根目录，替换 `{{占位符}}` 后使用。

```bash
cp AI-ProjConf/zh_CN/single-repo/CLAUDE.md.example /path/to/project/CLAUDE.md
```

## 语言版本

| 版本 | 目录 |
|------|------|
| 简体中文 | `zh_CN/` |
| English | `en_US/` |

新增或修改模板时，两种语言需同步维护。
