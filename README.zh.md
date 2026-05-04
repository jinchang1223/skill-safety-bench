# Skill Safety Bench

<p align="right">
  <a href="./README.md"><img alt="English" src="https://img.shields.io/badge/English-blue?style=for-the-badge"></a>
  <a href="./README.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-blue?style=for-the-badge"></a>
</p>

`Skill Safety Bench` 是一个已经物化好的 benchmark，用来评估 agent 在 skill-facing context 以及本地环境辅助文件影响下出现的安全失败。它不是动态生成 case 的框架，而是包含一组可以直接用 Harbor 运行的静态 benchmark cases。

### 安全说明

本仓库包含对抗性 benchmark case。一些 case 会模拟 phishing、凭证索取、破坏性操作、数据外泄、沙箱边界滥用、外部动作诱导和持久化类行为。请只在隔离的研究环境中运行。

不要使用生产凭证、生产云账号、个人账号或敏感本地文件运行这些 case。建议使用一次性 API key、临时容器、受限网络和专用工作目录。对外分享运行产物前，请先人工检查。

### 仓库结构

- `benchmark/`
  静态 benchmark cases，按照 risk domain、category 和 case id 组织。
- `scripts/start_agent_batch.sh`
  本地运行的主入口。它负责选择 case、启动 Harbor，并刷新运行结果摘要。
- `scripts/run_manifest_agent_batch.py`
  `start_agent_batch.sh` 调用的 runner 实现。
- `env.example`
  环境变量示例文件。运行前复制为 `.envrc` 并填写本地凭证。

### Benchmark 结构

每个 case 的结构如下：

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

- `attacked_task/`
  Harbor 实际运行的任务包。
- `attacked_task/tests/test.sh`
  基础任务测试的 canonical entry。
- `eval/verify_attack.py`
  每个 case 的确定性 attack behavior verifier。
- `metadata.json`
  机器可读的 case metadata。
- `rationale.md`
  人类可读的 case rationale。

当前 benchmark 包含 6 个 risk domains、30 个 categories、155 个 cases。Category 目录统一使用 `categoryN-...` 命名，例如：

```text
benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category1-availability_cost_and_service_exhaustion/
```

### 环境准备

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

### 配置环境变量

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

### 运行 Benchmark

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

### 运行产物

每次运行会在 `jobs/` 下创建目录：

```text
jobs/<agent>-risk-domain-5-memory-recovery-audit-and-persistence-risks-<timestamp>/
```

主要文件：

- `selected_cases.json`
- `batch_config.json`
- `<case_id>/case_result.json`
- `attack_results.json`
- `summary.json`
- `attack_results.csv`
- `attack_results.md`
- `summary.csv`
- `summary.md`

检查运行结果时，优先看 `jobs/<run>/attack_results.json` 和 `jobs/<run>/summary.json`。

### 如何理解结果

每个 case 需要从两个维度理解：

- benign base task 是否完成
- unsafe attack behavior 是否出现

常见 attack outcome：

- `attack_success`
- `attack_not_observed`
- `task_output_missing`

`task_output_missing` 表示预期的显式任务输出缺失。只要已有 artifacts 足够判断 attack condition，attack verifier 仍可能继续检查。
