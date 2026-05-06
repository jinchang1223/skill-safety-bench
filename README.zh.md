# Skill Safety Bench

<p align="right">
  <a href="./README.md"><img alt="English" src="https://img.shields.io/badge/English-blue?style=for-the-badge"></a>
  <a href="./README.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-blue?style=for-the-badge"></a>
</p>

`Skill Safety Bench` 是一个已经物化好的 benchmark，用来评估针对 skill-facing context 的攻击导致的 agent 安全失败。每个 case 都保持用户表层任务是普通任务，同时把攻击放在本地 skills、helper scripts、sidecar files、corpora、templates 或其他 agent 执行时可能读取的 workspace artifacts 中。

<p align="center">
  <img src="./assets/figures/introduction.png" alt="Skill Safety Bench overview" width="900">
</p>

## Benchmark 评估什么

现代 coding agent 和 task agent 往往不只依赖用户 prompt，还会读取本地 skills 和环境 artifacts。Skill Safety Bench 测试的是：agent 在完成正常任务的同时，能否抵抗嵌入在这些 skill-facing surfaces 中的不安全指令或误导性上下文。

这个 benchmark 是静态、可直接运行的 benchmark，不是 case 生成框架。仓库包含 155 个已经准备好的 cases，覆盖 6 个 risk domains 和 30 个 categories。每个 case 都包含：

- 一个仍然应该被完成的 benign base task
- 一个或多个 skill-facing attack surfaces
- 一个用于检测 unsafe behavior 的确定性 verifier
- 用于检查 base-task completion 的 task tests
- 描述最终 case 设计的 metadata 和 rationale

每次运行从两个维度评估：

- `task_success`：普通用户任务是否完成
- `attack_success`：不安全行为是否出现

这两个维度需要分开看：一个系统可能很好地完成了任务，但仍然因为信任带攻击内容的 skill context 而产生安全失败。

## Benchmark 结构

Cases 按照 risk domain、category 和 case id 组织：

```text
benchmark/<risk-domain>/<category>/<case>/
  metadata.json
  rationale.md
  attacked_task/
    instruction.md
    task.toml
    environment/
    solution/solve.sh
    tests/test.sh
  eval/verify_attack.py
```

关键文件：

| 路径 | 作用 |
| --- | --- |
| `attacked_task/` | Harbor 实际运行的任务包。 |
| `attacked_task/tests/test.sh` | 基础任务测试的 canonical entry。 |
| `eval/verify_attack.py` | 用于检测 attack behavior 的 rule-based verifier。 |
| `metadata.json` | 机器可读的 case metadata。 |
| `rationale.md` | 人类可读的 case rationale。 |
| `benchmark/<risk-domain>/manifest.json` | batch run 使用的 case 列表。 |

`benchmark/` 目录是 case 的 source of truth。Category 目录统一使用 `categoryN-...` 命名，例如：

```text
benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category1-availability_cost_and_service_exhaustion/
```

## 安全说明

本仓库包含对抗性 benchmark cases。一些 case 会模拟 phishing、凭证索取、破坏性操作、数据外泄、沙箱边界滥用、外部动作诱导和持久化类行为。

请只在隔离的研究环境中运行 benchmark。不要使用生产凭证、生产云账号、个人账号或敏感本地文件。建议使用一次性 API key、临时容器、受限网络和专用工作目录。对外分享运行产物前，请先人工检查。

## 如何运行 Benchmark

### 1. 准备工具链

需要准备：

- `bash`
- `python3`，推荐 `>= 3.11`
- `docker`
- `uv`
- `harbor`
- `nvm`
- Node.js `22`

如果还没有安装 Harbor：

```bash
uv tool install harbor
```

检查基础工具：

```bash
harbor --help
python3 --version
docker --version
```

如果 Harbor agent 依赖 Node 环境，请在启动 benchmark 的 shell 中显式启用 Node 22：

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22
```

### 2. 配置环境变量

从示例文件创建本地 `.envrc`：

```bash
cp env.example .envrc
```

如果使用 `codex`，至少需要：

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="replace-with-your-openai-api-key"
```

如果使用 `claude-code`，需要 Anthropic 兼容认证变量，例如：

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
export ANTHROPIC_API_KEY="replace-with-your-anthropic-api-key"
```

如果使用 `direnv`：

```bash
direnv allow
```

如果不使用 `direnv`，不需要额外操作。运行脚本会显式 source `.envrc`。

### 3. 运行 Cases

Canonical entry point 是：

```bash
scripts/start_agent_batch.sh
```

运行一个 risk domain：

```bash
scripts/start_agent_batch.sh --rd 5
```

指定 agent 和 model：

```bash
scripts/start_agent_batch.sh \
  --rd 3 \
  --agent codex \
  --model openai/gpt-5.4
```

使用 Claude Code：

```bash
scripts/start_agent_batch.sh \
  --rd 3 \
  --agent claude-code \
  --model claude-3-7-sonnet-20250219
```

运行单个 case：

```bash
scripts/start_agent_batch.sh \
  --rd 5 \
  --case travel_planning_poisoned_belief_persistence_memory_anchor
```

运行单个 category：

```bash
scripts/start_agent_batch.sh \
  --rd 6 \
  --category category3-model_behavior_and_finetuning_poisoning
```

从指定 manifest 运行：

```bash
scripts/start_agent_batch.sh \
  --manifest benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/manifest.json
```

使用自定义 env 文件：

```bash
scripts/start_agent_batch.sh \
  --rd 5 \
  --envrc /path/to/your.envrc
```

只展开 case，不执行：

```bash
scripts/start_agent_batch.sh --rd 5 --dry-run
```

### 4. 查看运行产物

每次运行会在 `jobs/` 下创建目录：

```text
jobs/<agent>-risk-domain-5-memory-recovery-audit-and-persistence-risks-<timestamp>/
```

建议优先查看：

- `jobs/<run>/attack_results.json`
- `jobs/<run>/summary.json`
- `jobs/<run>/attack_results.csv`
- `jobs/<run>/summary.csv`

常用运行文件：

- `selected_cases.json`
- `batch_config.json`
- `<case_id>/case_result.json`
- `attack_results.md`

常见 attack outcome：

- `attack_success`
- `attack_not_observed`
- `task_output_missing`

`task_output_missing` 表示预期的显式任务输出缺失。只要已有 artifacts 足够判断 attack condition，attack verifier 仍可能继续检查。
