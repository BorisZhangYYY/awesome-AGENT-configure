# AAC Cron Trigger 优化计划

> 基于 OpenClaw 2026.7.1 新特性 `trigger`（条件触发）对 AAC 项目的 Cron 模板体系进行优化。
>
> 制定日期：2026-07-14
> 相关版本：OpenClaw 2026.7.1 | AAC 项目未发布版本

---

## 1. 背景

### 1.1 OpenClaw 2026.7.1 新特性

OpenClaw v2026.7.1 引入了 Cron 任务 `trigger`（条件触发）机制：

```json
{
  "trigger": {
    "script": "...",
    "once": false
  }
}
```

- `trigger.script`：在调度时刻**无头运行**的脚本，返回 `{ fire: true }` 时才执行 payload
- `trigger.once`：仅触发一次后自动失效

**核心能力**：Cron 从「固定轮询」升级为「条件触发」——Agent 只在状态变化时被唤醒，大幅降低无意义的 token 消耗。

### 1.2 当前 AAC 的痛点

当前 AAC 模板（如 `template-cron.zh.yaml`）的防护机制：

| 机制 | 实现方式 | 问题 |
|------|----------|------|
| 时间窗口 | Prompt 内 `exec date` 检查 | 仍触发 Agent，只是不执行业务 |
| 去重 | 读写文件记录最后执行时间 | 仍触发 Agent，只是跳过重复 |
| 开机堆叠防护 | 时间窗口 + 去重组合 | 仍触发 Agent，只是过滤掉 |

**本质问题**：只要到时间点，Agent 就会被唤醒，token 消耗不可避免。

---

## 2. 优化目标

1. **将时间窗口和去重从「Prompt 层」下沉到「Trigger 层」**
   - 不在时间窗口内 → trigger 返回 `false` → Agent 不唤醒
   - 已去重 → trigger 返回 `false` → Agent 不唤醒

2. **为特定场景引入状态变化触发**
   - Docker 容器状态变化 → 才触发健康巡检
   - 版本 release 更新 → 才触发版本检查
   - Memos 有新内容 → 才触发邮件通知

3. **模板系统兼容新旧两种模式**
   - 保持向后兼容：无 trigger 的场景继续用传统轮询
   - 渐进升级：支持 `TRIGGER_ENABLED` 开关切换

---

## 3. 方案设计

### 3.1 模板层新增 Trigger 配置区块

在 `template-cron.zh.yaml` 中新增【官方】`trigger` 字段：

```yaml
# 触发器配置【OpenClaw 2026.7.1+ 官方特性】
# 当 trigger 存在时，schedule 到达后先执行 trigger.script，
# 返回 { fire: true } 时才执行 payload，否则跳过本次唤醒。
trigger:
  enabled: "{{TRIGGER_ENABLED}}"      # "true" | "false"
  script: "{{TRIGGER_SCRIPT}}"         # JS 脚本内容，返回 { fire: boolean, reason?: string }
  once: "{{TRIGGER_ONCE}}"             # "true" 时仅触发一次后自动失效
```

### 3.2 内置 Trigger 脚本库

AAC 提供一组常用 trigger 脚本，场景 YAML 通过 `TRIGGER_TYPE` 引用：

| TRIGGER_TYPE | 脚本功能 | 适用场景 |
|-------------|----------|----------|
| `time_window` | 检查当前时间是否在窗口内 + 去重状态检查 | 早安/午安/晚安提醒 |
| `file_changed` | 监控文件/目录修改时间变化 | Memos 有新内容 |
| `docker_status` | 检查 Docker 容器状态是否异常 | Docker 健康巡检 |
| `http_changed` | 对比 URL 响应 hash 是否变化 | URL 监控、版本检查 |
| `git_changed` | 检查 git 仓库是否有新 commit | 项目自动整理 |
| `custom` | 使用用户自定义的 TRIGGER_SCRIPT | 任意自定义逻辑 |

### 3.3 场景模板优化示例

#### 3.3.1 Docker 健康巡检（由轮询 → 事件触发）

```yaml
# docker-check.yaml 优化后
variables:
  SCHEDULE_TYPE: "cron"
  SCHEDULE_EXPR: "*/5 * * * *"
  
  # 新增：Trigger 层
  TRIGGER_ENABLED: "true"
  TRIGGER_TYPE: "docker_status"
  
  # 原有：时间窗口和去重保留作为 fallback
  TIME_WINDOW_ENABLED: "false"  # 已下沉到 trigger，无需重复
  DEDUP_ENABLED: "false"         # 已下沉到 trigger，无需重复
```

**内置 `docker_status` trigger 脚本逻辑**：

```javascript
// 伪代码：检查是否有容器状态变化或异常
const lastState = readFile('/tmp/.aac-docker-last-state');
const currentState = exec('docker ps --format "{{.Names}}:{{.Status}}"');
const currentHash = hash(currentState);

if (currentHash !== lastState.hash) {
  writeFile('/tmp/.aac-docker-last-state', { hash: currentHash, time: now() });
  return { fire: true, reason: 'Container status changed' };
}

// 即使 hash 没变，也检查是否有 unhealthy 状态
const unhealthy = currentState.includes('unhealthy');
if (unhealthy) {
  return { fire: true, reason: 'Unhealthy containers detected' };
}

return { fire: false };
```

#### 3.3.2 Workspace 整理（由定时 → 变化触发）

```yaml
# workspace-check.yaml 优化后
variables:
  SCHEDULE_TYPE: "cron"
  SCHEDULE_EXPR: "0 22 * * *"   # 仍保留定时，但用 trigger 过滤
  
  TRIGGER_ENABLED: "true"
  TRIGGER_TYPE: "git_changed"
  TRIGGER_SCRIPT_GIT_DIR: "{{WORKSPACE}}"
```

**内置 `git_changed` trigger 脚本逻辑**：

```javascript
const lastCommit = readFile('/tmp/.aac-git-last-commit');
const currentCommit = exec('git -C {{GIT_DIR}} rev-parse HEAD');

if (currentCommit !== lastCommit) {
  writeFile('/tmp/.aac-git-last-commit', currentCommit);
  return { fire: true, reason: 'New commits detected' };
}

return { fire: false };
```

#### 3.3.3 Memos 邮件通知（由轮询 → 文件变化触发）

```yaml
# memos-email.yaml 优化后
variables:
  SCHEDULE_TYPE: "every"
  SCHEDULE_EXPR: "60000"         # 每 60 秒检查一次
  
  TRIGGER_ENABLED: "true"
  TRIGGER_TYPE: "file_changed"
  TRIGGER_SCRIPT_FILE: "{{MEMOS_DATA_DIR}}/memos.db"
```

**内置 `file_changed` trigger 脚本逻辑**：

```javascript
const lastMtime = readFile('/tmp/.aac-file-mtime-{{FILE_HASH}}');
const currentMtime = stat('{{FILE}}').mtime;

if (currentMtime > lastMtime) {
  writeFile('/tmp/.aac-file-mtime-{{FILE_HASH}}', currentMtime);
  return { fire: true, reason: 'File modified' };
}

return { fire: false };
```

### 3.4 build-cron.py 脚本改造

`build-cron.py` 需要新增 `TRIGGER` 相关渲染逻辑：

1. **变量展开**：
   - `TRIGGER_ENABLED` → 决定是否渲染 `trigger` 字段
   - `TRIGGER_TYPE` → 从内置脚本库加载对应脚本
   - `TRIGGER_SCRIPT` → 用户自定义脚本直接注入

2. **内置脚本库映射**：
   ```python
   TRIGGER_SCRIPTS = {
       "time_window": load_script("triggers/time_window.js"),
       "file_changed": load_script("triggers/file_changed.js"),
       "docker_status": load_script("triggers/docker_status.js"),
       "http_changed": load_script("triggers/http_changed.js"),
       "git_changed": load_script("triggers/git_changed.js"),
   }
   ```

3. **脚本注入**：
   - 当 `TRIGGER_TYPE` 为内置类型时，从库中加载并替换占位符
   - 当 `TRIGGER_TYPE` 为 `custom` 时，直接使用 `TRIGGER_SCRIPT` 变量

---

## 4. 实施计划

### Phase 1：模板层基础（本周内）

- [ ] 在 `template-cron.zh.yaml` 新增 `trigger` 配置区块
- [ ] 新增 `TRIGGER_ENABLED`、`TRIGGER_TYPE`、`TRIGGER_SCRIPT`、`TRIGGER_ONCE` 变量
- [ ] 修改 `build-cron.py` 支持 trigger 字段渲染
- [ ] 新增 `OpenClaw/triggers/` 目录，存放内置脚本模板
- [ ] 向后兼容：当 `TRIGGER_ENABLED` 为 `false` 或未设置时，不渲染 trigger 字段

### Phase 2：内置脚本库（下周）

- [ ] 实现 `time_window` trigger：将现有时间窗口 + 去重逻辑迁移为 trigger 脚本
- [ ] 实现 `file_changed` trigger：基于文件 mtime 变化检测
- [ ] 实现 `docker_status` trigger：基于容器状态变化检测
- [ ] 实现 `http_changed` trigger：基于响应 hash 变化检测
- [ ] 实现 `git_changed` trigger：基于 git commit hash 变化检测
- [ ] 每个 trigger 脚本附带测试用例

### Phase 3：场景模板升级（再下周）

- [ ] 升级 `reminders/morning.yaml`：使用 `time_window` trigger，移除 Prompt 层时间窗口
- [ ] 升级 `reminders/noon.yaml`：同上
- [ ] 升级 `reminders/evening.yaml`：同上
- [ ] 升级 `checks/docker-check.yaml`：使用 `docker_status` trigger
- [ ] 升级 `checks/workspace-check.yaml`：使用 `git_changed` trigger
- [ ] 升级 `checks/cron-check.yaml`：可选使用 `time_window` trigger
- [ ] 每个场景升级后验证：在 trigger 返回 false 时 Agent 不被唤醒

### Phase 4：文档与技能更新（最后）

- [ ] 更新 `SKILL-GUIDE.md`：说明 trigger 的使用方法
- [ ] 更新 `init-cron/SKILL.md`：新增 trigger 选型指导
- [ ] 更新 `migrate-cron/SKILL.md`：说明如何将传统 cron 升级为 trigger 模式
- [ ] 更新 `README.md`：说明 trigger 优化的价值
- [ ] 更新 `CHANGELOG.md`

---

## 5. 风险与注意事项

| 风险 | 缓解措施 |
|------|----------|
| Trigger 脚本执行失败 | 默认行为：trigger 失败视为 `fire: true`（安全降级），避免遗漏重要任务 |
| 过度依赖 trigger 导致首次延迟 | 对实时性要求高的任务（如 Memos 通知），保留短间隔 schedule + trigger 组合 |
| 脚本库膨胀 | 仅提供 5-6 个通用 trigger，复杂场景用 `custom` 类型让用户自行编写 |
| 向后兼容 | `TRIGGER_ENABLED` 默认为 `false`，现有场景无需改动即可正常工作 |
| OpenClaw 版本兼容性 | 在模板注释中标注「OpenClaw 2026.7.1+ 支持」，旧版本无 trigger 字段不影响运行 |

---

## 6. 预期收益

| 场景 | 传统模式（每 10 分钟） | Trigger 模式（变化时） | 收益 |
|------|----------------------|----------------------|------|
| Docker 巡检 | 144 次/天 × 1000 tokens | 状态变化时（约 5-10 次/天） | **95% token 节省** |
| Memos 通知 | 1440 次/天 × 500 tokens | 有新 Memos 时（约 5-20 次/天） | **98% token 节省** |
| Workspace 整理 | 1 次/天 × 2000 tokens | git 有变化时（约 1-3 次/天） | **50-70% token 节省** |
| 早安/午安/晚安 | 3 次/天 × 800 tokens | 不变（trigger 负责时间窗口） | **30% token 节省**（去掉了 Prompt 层时间窗口检查） |

---

*此计划遵循 AAC 项目 CLAUDE.md 开发规范制定。*
*模板变量命名符合 `[A-Z][A-Z0-9_]*` 规范，无连字符。*
