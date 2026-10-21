# 编辑 Cron 任务流程

修改已按 AAC 规范创建的定时任务。

## 前提条件

- 任务名带 `【AAC-` 前缀
- 存在对应场景 YAML 文件于 `$AAC_WORKSPACE/cron/<job-name>.yaml`
- 无 YAML 时建议改用迁移流程

## 步骤

- **1. 列出任务**：`openclaw cron list`，优先标识 `【AAC-` 前缀
- **2. 选择任务**：用户指定任务名或 ID
- **3. 查找 YAML**：在 `$AAC_WORKSPACE/cron/` 下搜索
- **4. 展示配置**：读取 YAML 并展示关键字段（名称、schedule、窗口、delivery、thinking、tools）
- **5. 询问修改**：常见修改项：
  - 触发时间 → `SCHEDULE_EXPR`
  - 时间窗口 → `WINDOW_START` / `WINDOW_END`
  - 内容 → `SCENE_NAME` / `EMOJI` / `REMARK`
  - 送达方式 → `DELIVERY_MODE`
  - 模型能力 → `THINKING` / `MODEL` / `TOOLS`
  - 超时 → `TIMEOUT_SECONDS`
- **6. 修改 YAML**：更新对应变量值
- **7. 重新渲染（必须用 `--json`）**：
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<job-name>.yaml" --json
  ```
  输出是 argv 数组（JSON），可直接取出 `--message` 的值。
  ⛔ **不要用默认输出做字符串替换**（见下方「⛔ 禁止做法」）。
- **8. 选择更新方式**：
  - Agent 模式（用 `--message`）：优先 `openclaw cron edit <job-id>`，保留 ID
  - 命令模式（用 `--command`）：不支持 `edit`，只能 `rm` + `create`，ID 会变
- **9. 用户确认**：展示修改前后差异、更新方式、对应命令
- **10. 执行更新**：
  - 方式 A（推荐，最小编辑）：只传 `--message`，其余字段由 live job 原样保留
    ```python
    import json, subprocess
    arr = json.loads(subprocess.run(
        ['python3', f'{AAC_REPO}/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py', yaml, '--json'],
        capture_output=True, text=True).stdout)
    msg = arr[arr.index('--message') + 1]
    subprocess.run(['openclaw', 'cron', 'edit', job_id, '--message', msg])
    ```
  - 方式 A'（需改其他字段时）：从 argv 里取 flag 重建，**每个 flag 只能出现一次**。
    实测 `openclaw cron edit` 支持 `--name` `--description` `--tz` `--session` `--light-context`
    `--announce` `--best-effort-deliver` `--channel` `--to` `--timeout-seconds` `--agent` `--model`
    `--fallbacks` `--thinking` `--tools` `--trigger-script` 等。
    ⚠️ **不要把 create 的位置参数（cron 表达式）带进 edit**——edit 的位置参数是 job id。
  - 方式 B：`openclaw cron rm <job-id>` + `openclaw cron create ...`
- **11. 验证（不可跳过）**：必须核对 live job 的 payload **真的变了**：
  ```bash
  openclaw cron list --json | python3 -c "
  import json,sys
  d=json.load(sys.stdin)
  for j in d['jobs']:
      if j['id']=='<job-id>':
          m=(j.get('payload') or {}).get('message','')
          print(j['id'][:8], j['name'], 'len=', len(m))
          print('含新标记:', 'YOUR_NEW_MARKER' in m)
  "
  ```
  同时确认 job 总数没增加（没有意外 create 出副本）。

## ⛔ 禁止做法（2026-10-21 实测事故）

**禁止**把 `build-cron.py` 的默认输出做字符串替换来拼 edit 命令：

```python
# ❌ 绝对不要这样
edit_cmd = output.replace('openclaw cron create', 'openclaw cron edit <id>', 1)
```

原因（2026-10-19/21 连续踩坑，实测产生 4 个重复 job 并误删带改动的副本）：

1. 默认输出是**反斜杠续行**格式：`openclaw \⏎  cron \⏎  create \⏎  '15 7 * * *' ...`，
   字符串 `'openclaw cron create'` **不匹配**（中间隔着 `\\\n  `），replace 静默失败。
2. 替换失败 → 实际执行的是 `openclaw cron create` → 每执行一次多一个 job。
3. 更糟：随后把「带改动的新 job」当重复副本删掉，留下旧内容 job，改动等于没生效。

**症状识别**：edit 之后 `openclaw cron list` 出现同名 job、且新 job 状态为 `idle`（从未运行）。

**正确做法**：用 `--json` 拿 argv 数组，按上面方式 A 构造 edit。

**另一个坑**：从 argv 拼 flag 时若同一个 flag 出现两次（如 `--agent` 重复），
commander 会把后一个 flag 的值当成多余位置参数，报 `Too many arguments for this command`。
拼接前先按 flag 名去重。实测：`openclaw cron edit <id> --agent --agent main` 必报此错，
`openclaw cron edit <id> --agent main` 正常。

**另一个坑：edit 会真的覆盖，不要拿它做 flag 试验**

`openclaw cron edit <id> --message "x"` 会**立即把 live job 的 message 覆盖成 "x"**。
验证 flag 行为时**不要对生产 job 做实验**——先备份 message：

```python
msg = (job['payload'] or {}).get('message') or ''
open('/tmp/msg-backup.txt','w').write(msg)   # 改完可还原
```

## 安全红线

- 删除旧任务前必须确认（破坏性操作）
- 保留修改后的 YAML 文件于 `$AAC_WORKSPACE/cron/`
- 修改后名称仍保持 AAC 格式
- 优先使用 `edit` 保留 job ID，避免状态丢失
- **edit 后必须验证 payload 真的变了**（步骤 11），不能只看命令返回码
- **删除「重复」job 前先确认内容**：用 `--json` 对比两者 payload，被删的那个可能才是带改动的那份
- 渲染命令一律加 `--json`
