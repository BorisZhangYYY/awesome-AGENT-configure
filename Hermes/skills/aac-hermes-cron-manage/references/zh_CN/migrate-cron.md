# 迁移至 Hermes 原生模板

简体中文 | [English](../en_US/migrate-cron.md)

## 保留意图，不照搬外部字段

盘点来源任务的准确身份、触发、时区、prompt、投递、依赖、skills/工具、补跑策略、运行状态和副作用。映射前阅读目标 help 和公共 schema。不得把外部 job 对象直接导入 Hermes 存储，也不直接编辑 `jobs.json`。

| 来源概念 | Hermes 映射 / 边界 |
|---|---|
| 周期或延时提醒 | `schedule`；区分周期 `30m` 与一次性 `in 30m` |
| 目标会话、唤醒主会话 | 编译器无等价字段；Hermes Agent 在新会话运行，不延续当前聊天 |
| 消息/payload | 自包含 `prompt`，skills 按顺序提供支持指令 |
| 通知渠道和收件人 | 明确的 `deliver` 字符串；失败路由另用 `failure_deliver` |
| 模型、思考、回退参数 | 按用户批准映射 CLI `model`/`provider`、`reasoning_effort`；不虚构通用 fallback/timeout 参数 |
| Trigger JavaScript | 如确需前置判断，重写为审阅过的 Hermes 脚本或 monitor；QuickJS trigger 不等于 Hermes trigger |
| 静默 / 显式失败 | Agent `[SILENT]`、首行 `[CRON_FAILURE]`；脚本空 stdout / 非零退出 |
| 持久项目 Loop | 状态文件加自包含提示词，可选 `continuity`；不宣称是持久 Agent 会话 |
| 完成后自动暂停 | 分两阶段绑定真实 ID，显式限定权限；默认人工暂停 |

OpenClaw 的 `--session`、`--wake`、`--message`、`--thinking`、`--timeout-seconds`、`--announce`、`--channel`、`--to`、`--delete-after-run`、`--trigger-script`、`--fallbacks` 不是 Hermes create/edit 参数，不得机械替换 token。OpenClaw 的独立技能为 `aac-openclaw-cron-manage`，不要把它别名到本技能。

## 同框架迁移

同一 Hermes home/profile 的已有任务保留不可变 ID，使用 `--edit JOB_ID`。先记录原暂停状态和全部策略，再更改。显式比较来源/模板默认值与运行值：null 省略更新，不是清空。保留模型选择权和投递，模式切换及列表/字符串清空见 [编辑语义](edit-cron.md)。

跨 home/profile 时，目标有独立任务存储、skills、scripts、凭据和 gateway 上下文。在目标创建新的暂停任务，记录新旧 ID 映射，不承诺跨独立存储保留 ID。依赖需独立审阅复制到目标受限 `scripts/` 树。读取目标真实 ID 后再改 `context_from` 引用。不把凭据复制进模板，也不沿用指向其他 home 的来源脚本绝对路径。

## 避免双重执行的切换

1. 按目标语言建立模板，预览全部带类型字段，根据 [原生覆盖](native-parameters.md) 选择 CLI、工具或 `--plan`。编译是离线输出，不是部署。
2. 经授权后在目标暂停创建（或暂停同 ID 任务后迁移）。实际 ID 读回并由 `--edit` 绑定前，Loop 自动暂停保持关闭。
3. 分别验收脚本字节、依赖、应用访问、权限、输出和明确投递。暂停任务的显式金丝雀 `run` 也可能有真实副作用，必须获准。
4. 在约定切换点暂停旧调度，处理仍在运行的实例（只有获授权才 `cancel`），读回两侧状态后再恢复目标。保留回滚证据，不立即删除来源。
5. 读回准确目标 ID/配置和来源暂停状态，验证下次运行及调度器就绪；手动结果不证明定时运行。报告目前由哪个范围执行，以及如何回滚。

来源要求没有支持的映射时停止并询问，不静默削弱。仓库开发不授权实际迁移、gateway 修改、任务创建或线上配置编辑。
