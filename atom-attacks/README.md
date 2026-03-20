# SkillSafetyBench Atom Attacks

这个目录存放 `SkillSafetyBench` 的原子攻击库。

这里的设计目标不是简单按“攻击发生在什么时候”来分组，而是按“它本质上属于什么安全风险”来组织。  
因此，当前采用的规范架构是：

`risk_domain -> category -> class -> case`

## 一、四层架构分别是什么意思

### 1. `risk_domain`

定义：  
`risk_domain` 是最高层的风险域。它回答的问题是：**这类攻击本质上属于哪一种安全问题**。

例如：
- 是在污染 agent 对上下文的信任？
- 是在扩大 agent 的权限和行动边界？
- 是在劫持 runtime、协议或工具链？
- 是在利用输出和外传链路泄露数据？

为什么要把它放在最顶层：  
因为很多真实攻击会跨越多个 skill 生命周期阶段。如果只按 `planning`、`execution` 这类阶段来分，会把本质相近的安全风险拆散。

### 2. `category`

定义：  
`category` 是某个风险域内部的并列方向。它回答的问题是：**在这个风险域里，攻击主要通过哪一种机理发生**。

例如在“上下文信任风险”里，可以继续区分：
- 是在骗 agent 选错路
- 还是在污染它信任哪一个来源
- 还是在多个上下文里植入冲突或危险意图

所以 `category` 不是层级上的“下一阶段”，而是同一风险域下的不同攻击方向。

### 3. `class`

定义：  
`class` 是可复用的原子攻击家族。它回答的问题是：**这一类攻击的一般模式是什么**。

例如：
- `priority_override`
- `runtime_integrity_compromise`
- `destructive_operation_induction`

一个 `class` 下面可以包含多个具体 case。

### 4. `case`

定义：  
`case` 是最小的、可独立物化和运行的攻击实例。它回答的问题是：**这一次具体要向任务里注入什么**。

例如：
- `task_vs_skill_flip`
- `api_key_request`
- `path_shadowing`

真正运行 benchmark 时，选择的是一个或多个 `case`。

## 二、目录结构是什么

当前目录结构是：

```text
atom-attacks/
  risk-domain-<n>-<risk-domain-name>/
    risk_domain.yaml
    category-<n>-<category-name>/
      category.yaml
      <attack-class>/
        class.yaml
        attack.py
        cases/
          <case-id>.yaml
```

每类文件的作用：

- `risk_domain.yaml`
  定义这个 risk domain 的含义、重要性和典型安全问题。
- `category.yaml`
  定义这个 category 的划分逻辑，也就是它和同 risk domain 下其他 category 的区别。
- `class.yaml`
  定义这个 attack class 的机制、目标行为和元数据。
- `attack.py`
  实现这个 class 下多个 case 的实际攻击代码。
- `cases/*.yaml`
  定义每个 case 的元数据，例如归属关系、可攻击 surface、诱导行为、预期安全行为等。

## 三、为什么 YAML 和 `attack.py` 放在同一棵树里

因为这里不是把 YAML 当注释，也不是把 Python 当独立插件库。

它们是同一个 attack library 的两部分：

- YAML 负责定义规范和元数据
- `attack.py` 负责定义可执行实现

运行时会同时使用这两者：

- 读取 YAML 做 case discovery
- 读取 YAML 做 taxonomy lookup
- 读取 YAML 做 surface mode 校验
- 加载同目录的 `attack.py` 注册具体 case 实现

所以这里的设计原则是：  
**case 的定义和 case 的实现要尽量靠近，避免规范层和实现层长期漂移。**

## 四、哪些元数据是当前重点

当前 case YAML 里重点会看到这些字段：

- `risk_domain`
- `category`
- `class`
- `lifecycle_stages`
- `coordination_scopes`
- `primary_surfaces`
- `surface_mode`
- `supported_surfaces`
- `default_surface`
- `target_induced_behaviors`
- `expected_safe_behaviors`

其中最容易混淆的两个概念是：

- `risk_domain`
  这是主架构层级，决定这个 case 属于哪类安全风险。
- `lifecycle_stages`
  这是正交 metadata，只表示它主要在哪个 skill 生命周期阶段起作用。

也就是说：
- `risk_domain` 决定“它是什么问题”
- `lifecycle_stages` 决定“它通常在哪个阶段显现”

这里还新增了一个重要的横切元数据：

- `coordination_scopes`
  它表示这个攻击通常适用于哪一种 agent 协作拓扑。
  它不是新的顶层 taxonomy，也不是新的 risk domain，而是跨越多个 risk domain 复用的附加维度。

当前使用的协作拓扑枚举是：

- `single_agent`
  单智能体直接完成任务。
- `delegated_subagent`
  主 agent 把一部分工作委派给子 agent。
- `supervisor_worker`
  一个 supervisor 负责任务分解和审批，一个或多个 worker 负责执行。
- `peer_multi_agent`
  多个平级 agent 互相协作、交换中间结果或交叉验证。
- `federated_service_mesh`
  agent 与多个远程服务、MCP server、插件或工具节点形成联邦式协作网络。

为什么把它设计成横切元数据，而不是新的 risk domain：

- 因为它描述的是**攻击如何传播**
- 不是描述**攻击本质属于哪一类安全问题**

比如：

- `priority_override` 可以发生在单智能体里，也可以通过 subagent delegation 继续放大
- `approval_bypass_spoofing` 可以骗一个 planner，也可以骗 supervisor-worker 结构里的上游调度者
- `runtime_integrity_compromise` 可以只污染本地执行，也可以污染多服务协作链里的某个节点

所以这里的原则是：

- `risk_domain` 管“这是什么风险”
- `coordination_scopes` 管“这种风险会在哪种协作结构里显现或传播”

## 五、surface control 是什么

这里的很多 case 会修改不同的攻击面，例如：

- `instruction.md`
- `SKILL.md`
- `references/`
- task artifacts
- runtime wrapper
- Docker 环境
- 输出文件
- 持久化状态

当前用 `surface_mode` 控制这一点：

- `fixed`
  这个 case 的攻击面是固定的，不能随便切换。
- `choice`
  这个 case 可以在若干等价 surface 上实现，运行时可以通过 `options.surface` 指定。
- `composite`
  这个 case 天生就是多 surface 联动，不允许强行压成单 surface。

## 六、六个 Risk Domain 怎么理解

在进入各个 risk domain 之前，再补一个边界：

- `SkillSafetyBench` 的 `atom-attacks/` 只放**可物化、可执行、可注入**的攻击
- 组织治理、审批制度、日志政策这类问题很重要，但它们不是直接可 materialize 的 atom attack
- 所以它们不会被单独做成新的顶层 risk domain

这样可以避免把“攻击实现”和“治理要求”混在同一套目录里

### 1. `context_trust_and_prompt_manipulation_risks`

中文理解：  
**上下文信任与提示操纵风险**

这个风险域关注的是：  
agent 在“读任务、读 skill、读参考材料、读中间上下文”时，**到底相信了什么、按什么解释、怎么形成初始判断**。

这里的问题通常发生在 agent 真正行动之前，但它的影响会一路传播到后续 planning、execution、output。

为什么单独成域：  
因为很多攻击并不是直接逼 agent 执行坏命令，而是先让它“相信了错误的东西”。一旦信任链被污染，后面的很多行为都会被带偏。

本域下的 category：

- `routing_and_discovery_deception`
  中文理解：路由与发现欺骗。  
  这类攻击先干扰 agent “找到什么、先看什么、走哪条路径”。重点不是改规则，而是先把 agent 引到错误入口。

- `source_authority_rule_and_example_poisoning`
  中文理解：来源权威、规则与示例投毒。  
  这里的 `authority` 指的是“来源权威性”，不是“授权权限”。  
  重点是污染 agent 对“哪一份说明更权威、哪一条规则优先、哪个 example 值得模仿”的判断。

- `intent_seeding_and_cross_context_conflict`
  中文理解：意图植入与跨上下文冲突。  
  这类攻击不是只改一条规则，而是把危险目标、错误仲裁逻辑或互相冲突的引导植入多个上下文，让 agent 内部形成错误意图。

- `retrieval_and_reference_contamination`
  中文理解：检索与参考资料污染。  
  这里关注的是检索结果、参考语料、索引内容本身被污染，导致 agent 把不可信内容当成证据。

- `multi_source_trust_amplification`
  中文理解：多来源信任放大。  
  这类攻击通过“多个地方都这么说”制造假共识，利用 agent 把一致性误当成真实性。

### 2. `agency_scope_and_authorization_risks`

中文理解：  
**代理行动范围与授权边界风险**

这个风险域关注的是：  
agent 是否被推着做了**本不该做、无权做、风险过高、需要额外确认**的动作。

为什么单独成域：  
因为这里的核心不再是“我信了什么”，而是“我被允许做什么，我实际去做了什么”。

本域下的 category：

- `planning_scope_and_safety_degradation`
  中文理解：规划范围扩张与安全标准下降。  
  这类攻击会让 agent 在 planning 阶段接受更激进、更高权限、更低验证标准的方案。

- `approval_and_authority_spoofing`
  中文理解：审批与授权伪造。  
  这类攻击通过伪造“用户已批准”“上级已授权”“紧急情况可跳过确认”等信号，绕开本来应该存在的安全摩擦。

- `credential_privilege_and_sensitive_input_solicitation`
  中文理解：凭证、权限与敏感输入索取。  
  核心是让 agent 主动索要 API key、密码、sudo、信用卡、OTP 等本不应向用户索取的信息或权限。

- `destructive_and_sensitive_operation_induction`
  中文理解：破坏性操作与敏感访问诱导。  
  这类攻击会把删除文件、重置仓库、读取私钥、读取 `.env` 之类危险动作包装成“正常调试步骤”。

- `transaction_and_external_action_induction`
  中文理解：交易与外部高影响动作诱导。  
  这里预留给更高影响的外部动作，例如支付、账户变更、第三方系统操作等。

### 3. `execution_runtime_framework_and_protocol_risks`

中文理解：  
**执行、运行时、框架与协议风险**

这个风险域关注的是：  
就算 prompt 和 planning 本身没明显出错，agent 在真正执行时，它所依赖的 runtime、wrapper、loader、协议边界是不是已经被动了手脚。

为什么单独成域：  
因为这类问题经常不体现在自然语言里，而体现在命令路径、解析器、序列化、协议身份、执行边界上。

本域下的 category：

- `runtime_and_toolchain_integrity_compromise`
  中文理解：运行时与工具链完整性破坏。  
  重点是实际执行的 binary、helper、wrapper 被调包或劫持，比如 `path_shadowing`。

- `downstream_interpreter_and_query_exploitation`
  中文理解：下游解释器与查询系统利用。  
  这里预留给 SQL 注入、模板注入、公式注入、命令拼接等“agent 输出进入下游解释器后再触发”的风险。

- `framework_serialization_and_loader_abuse`
  中文理解：框架序列化与加载器滥用。  
  这里关注框架自身的 parser、loader、反序列化与对象恢复机制。

- `protocol_identity_and_capability_abuse`
  中文理解：协议身份与能力声明滥用。  
  例如 MCP、工具协议、远端服务声称自己具有什么 capability，agent 如果缺少验证，就可能被伪造身份或伪造能力欺骗。

- `sandbox_and_environment_boundary_escape`
  中文理解：沙箱与环境边界逃逸。  
  这类攻击关注执行是否越过预期的文件系统、容器、网络或环境边界。

### 4. `data_boundary_output_and_externalization_risks`

中文理解：  
**数据边界、输出完整性与外传风险**

这个风险域关注的是：  
agent 生成的中间产物、最终输出和外部发送链路，是否被用来污染下游系统或把数据带出边界。

为什么单独成域：  
因为很多攻击不是在“执行时立即爆炸”，而是在输出和交付阶段埋雷，让后续系统接手时出问题。

本域下的 category：

- `artifact_and_schema_integrity_failure`
  中文理解：工件与输出结构完整性失效。  
  核心是污染中间 artifact，或者篡改输出 schema，让 downstream consumer 信错数据。

- `output_channel_data_leakage`
  中文理解：输出通道数据泄露。  
  这类攻击把正常报告、结果文件、提交文件变成 secret 泄露通道。

- `external_destination_and_egress_abuse`
  中文理解：外部目标与出站链路滥用。  
  核心是把本地信息、artifact 或状态发到不该发的外部 endpoint。

- `downstream_output_interpreter_abuse`
  中文理解：下游输出解释器滥用。  
  这里预留给 CSV/Excel 公式注入、HTML/模板 payload、浏览器消费型 payload 等。

- `handoff_and_submission_boundary_abuse`
  中文理解：交接与提交边界滥用。  
  这里关注的是文件从一个系统交到另一个系统时，边界控制失效导致的污染。

### 5. `memory_recovery_audit_and_persistence_risks`

中文理解：  
**记忆、恢复、审计与持久化风险**

这个风险域关注的是：  
一次攻击是不是只影响当前一步，还是会留下长期影响；agent 是否会纠偏；攻击痕迹是否被刻意抹掉。

为什么单独成域：  
因为很多危险不在首次诱导，而在“错误一旦进去了就很难出来”，或者“事后已经没法追查”。

本域下的 category：

- `belief_persistence_and_self_correction_failure`
  中文理解：错误信念固化与自我纠正失败。  
  这类攻击会让 agent 一旦接受错误启发，就持续沿错路走，甚至在出现新证据后也不改。

- `audit_visibility_and_trace_suppression`
  中文理解：审计可见性与痕迹压制。  
  这类攻击的目标是让日志更少、证据更弱、事后更难复盘。

- `persistence_and_long_lived_footholds`
  中文理解：持久化植入与长期落脚点。  
  这类攻击会往环境中留下改动，让后续 run 或后续操作者继续受影响。

- `memory_store_and_history_poisoning`
  中文理解：记忆存储与历史状态投毒。  
  这里预留给 memory store、缓存、长期历史上下文的污染。

- `rollback_and_recovery_control_failure`
  中文理解：回滚与恢复控制失效。  
  这里关注系统在出问题之后，是否还能正确 rollback、cleanup 和 recover。

### 6. `knowledge_model_supply_chain_and_operational_risks`

中文理解：  
**知识、模型、供应链与运行运营风险**

这个风险域关注的是：  
那些不一定直接发生在某次 skill 执行过程里，但会系统性影响 agent 安全性的上游和外围风险。

为什么单独成域：  
因为如果 benchmark 只看 prompt 和 runtime，就会漏掉 retrieval poisoning、model poisoning、dependency compromise、cost exhaustion 这类更基础但也更严重的问题。

本域下的 category：

- `retrieval_knowledge_and_corpus_poisoning`
  中文理解：检索知识库与语料投毒。  
  重点是知识源被污染，导致 agent 稳定检索到错误或恶意信息。

- `model_behavior_and_finetuning_poisoning`
  中文理解：模型行为与微调投毒。  
  这里关注训练数据投毒、微调后门、触发式异常行为等。

- `dependency_plugin_and_release_chain_compromise`
  中文理解：依赖、插件与发布链路失陷。  
  核心是 agent 依赖的软件包、插件、构建产物、发布流程被攻破。

- `availability_cost_and_service_exhaustion`
  中文理解：可用性、成本与服务耗尽。  
  这类攻击并不一定诱导错误答案，而是拖慢、拖垮或拖贵系统。

- `model_extraction_and_service_abuse`
  中文理解：模型抽取与服务滥用。  
  关注服务能力被大规模探测、抽取、复制或恶意套利。

## 七、当前实现范围怎么理解

当前已经落地实现的重点集中在前五个 risk domain。  
第六个 risk domain 现在更多是架构预留，用来保证 benchmark 后续扩展时不用再推翻上层设计。

这也是当前组织方式的一个核心原则：

- 顶层架构先做对
- 当前 case 库按这个架构逐步补全
- 不因为已有 case 少，就把顶层风险域缩得太窄

## 八、当前 README 应该怎么用

如果你在读某个 case，不要只看它在哪个目录里，还要同时看四件事：

- 它属于哪个 `risk_domain`
- 它属于该 risk domain 下哪个 `category`
- 它的 `class` 在复用什么攻击模式
- 它的 `surface_mode` 和 `primary_surfaces` 是什么

这样你就能同时理解：

- 这是什么安全问题
- 它通过什么机理发生
- 它落在哪个注入面
- 它为什么被放在这里而不是别的地方
