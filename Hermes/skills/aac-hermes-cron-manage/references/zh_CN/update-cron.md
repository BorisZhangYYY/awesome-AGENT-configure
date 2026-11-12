# 升级与迁移模板

简体中文 | [English](../en_US/update-cron.md)

模板升级和任务升级是两件事：改仓库文件不动线上任务；动线上任务必须保留 ID 与暂停状态。

## 1. 升级仓库模板

1. 改 `template-cron.yaml` 或场景 YAML，保持顶层三键与变量命名不变。
2. 中英两份一起改，变量集合、占位符集合、`job` 键集合必须一致。
3. 逐个跑校验：

```bash
for f in $(find Hermes/zh_CN/cron-template Hermes/en_US/cron-template -name "*.yaml" \
  ! -name "template-cron.yaml"); do
  python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py "$f" --validate
done
python3 -m unittest discover -s tests/hermes
```

4. 变更若影响所有任务（例如改统一约束的措辞），在提交说明里写清楚影响面。

## 2. 把新模板应用到已有任务

```bash
# 1) 定位任务：ID 才唯一
hermes cron list --all
# 2) 生成更新命令，保留 ID
python3 .../build-cron.py Hermes/zh_CN/cron-template/checks/docker-check/docker-check.yaml \
  --edit <JOB_ID> --preview
# 3) 审阅后执行
env HERMES_HOME=$HOME/.hermes hermes cron edit <JOB_ID> --schedule "0 */6 * * *" --prompt "..."
# 4) 读回
hermes cron runs <JOB_ID> --limit 5
```

要点：

- `edit` 只改传进去的字段，未传的保持原值；要清空就显式传 `''` 或 `[]`（CLI 用 `--clear-skills`）。
- 任务原本是暂停的，`edit` 后仍是暂停；不要在升级过程中顺手 `resume`。
- 一次性任务改成周期任务，或周期改一次性，属于重建范畴：先建新任务、验收后再删旧任务，不要原地改。
- 升级前后各存一份 `list --all` 与 `runs` 输出，作为变更证据。

## 3. 从 OpenClaw 迁移

两者参数不通用，不要照搬字段：

| OpenClaw | Hermes 原生 |
|---|---|
| `trigger.js` 时间窗口与去重 | 无触发器；用 `catch_up` 与 `grace_minutes` |
| `message` 单段文本 | `prompt` + `skills` |
| 场景级 `template` 覆盖 | 场景只覆盖 `variables` 与 `job` |
| 无原生 monitor | `monitor_script` / `monitor_url`（互斥） |

迁移步骤：先在 Hermes 侧用同一业务指令重写场景 → `--validate` 通过 → 建暂停任务 → 手动 `run` 验收 → 恢复并观察一个真实周期 → 再停用 OpenClaw 侧任务，不要两者同时跑。

## 4. 回滚

1. `hermes cron edit <JOB_ID> --prompt "<上一版提示词>"` 回到旧文案；字段级回滚同样只改差异字段。
2. 脚本回滚：把 `$HERMES_HOME/scripts/aac/` 里的文件换回上一版，保持字节一致，再 `run` 一次确认。
3. 模板回滚走 Git：`git revert` 对应提交，重新编译并对比 `--preview` 输出。
4. 回滚后同样读回 ID、字段与运行记录，不凭记忆判断成功。

## 5. 停用与清理

- 暂时不跑：`hermes cron pause <JOB_ID>`，保留历史。
- 确认不再需要：先 `pause`，观察一段时间再 `remove`；删除即丢历史，无法从 `list` 恢复。
- 测试任务（`--test` 生成）必须显式 `run` 才会执行，且不会被自动删除；用完自行 `remove`。
