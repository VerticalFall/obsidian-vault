# 英国「AI Agent / AI 应用工程师」岗位样张 & 面试考察点

> **信息来源**：LinkedIn Jobs 实时搜索结果（2026-09-01 核实）+ 公司官网 careers 页（Distyl、Edra 已核实）+ 行业通识（面试考察点部分未逐条对应到具体公司，已标注）。
> **诚实声明**：岗位名称/公司/城市**均为实时可核实的真实岗位**；但**单条 JD 的完整技能清单与薪资区间因 LinkedIn 登录墙暂未能逐条抓取**——已如实标注，不编造具体薪资或职责原文。

---

## 一、真实岗位样张（曼彻斯特/西北）

以下均来自 LinkedIn Jobs 实时搜索结果，**公司 + 岗位名 + 城市可信**：

| 岗位名称 | 公司 | 城市/区域 |
|---|---|---|
| Generative AI Engineer | Oscar | 曼城（Actively Hiring） |
| Machine Learning Engineer | ConnexAI | 曼城 |
| Machine Learning Systems Engineer | ConnexAI | 曼城 |
| **Agentic Platform Engineer** | Travel Counsellors | 曼城（专门做 Agent 平台） |
| **AI Engineer – Agentic AI & Automation** | Adria Solutions | 曼城 |
| AI Implementation Engineer | Adria Solutions | 曼城 |
| Senior AI Engineer | CreateFuture | 曼城（另有 Leeds 岗） |
| AI Platform Engineer | The Portfolio Group | 曼城 |
| Senior AI Engineer (GEN-AI) | The Portfolio Group | 曼城 |
| AI Implementation Engineer | Manchester Digital | 曼城 |
| Artificial Intelligence Engineer | RedCompass Labs | 曼城 |
| AWS AI Engineer | Capgemini | 曼城 |
| Machine Learning Engineer | Hiiya | 曼城 |
| **Lead Engineer - AI Productivity Lab** | Lloyds Banking Group | 曼城（银行 AI 实验室，金额亮眼） |
| AI-Enabled Software Engineer | Mark43 | 大曼城 |

### 曼城趋势观察
- **"AI Implementation Engineer" 出现多次**（Adria、Manchester Digital）——就是你说的"AI 应用落地"类岗位，**名头很多样**，但本质都是"把 AI 接进业务跑通"。
- 有 **Agentic / Agent 平台类岗位**（Travel Counsellors 的 Agentic Platform Engineer）——正是你关注的 "AI Agent 开发应用"。
- **Lloyds 银行在曼城设了 AI Productivity Lab，招 Lead Engineer**——大厂也在曼城落地 AI，说明不止小公司。

---

## 二、真实岗位样张（伦敦/大伦敦）

| 岗位名称 | 公司 | 城市/区域 |
|---|---|---|
| **AI Engineer (Agents)** | Oho Group | 伦敦（专门招 Agent 工程师的猎头） |
| **AI Engineer (Agents)** | Arondite | 伦敦 |
| **AI Engineer – Agentic Systems** | DNV | 伦敦（另有 Bristol 岗） |
| AI Engineer | Distyl | 大伦敦（Forward Deployed/Agent 方向） |
| AI Engineer (London) | Edra | 伦敦（红杉投资的 Series A） |
| Forward Deployed AI Engineer | Edra | 伦敦 |
| AI Engineer | Xelix | 伦敦 |
| AI Engineer | Terra API | 伦敦 |
| Applied AI Engineer | Nevis | 伦敦 |
| AI & ML Engineer | Charlotte Tilbury Beauty | 伦敦 |
| AI Engineer | Planet | 伦敦 |
| **Software Engineer, Agents** | Decagon | 伦敦 |
| Applied AI Engineer | Dentons | 伦敦 |
| AI Engineer (UK) | Writer | 伦敦 |
| 多家 Agentic AI Engineer | 猎头等 | 伦敦（Harnham、La Fosse 等已挂出） |

### 伦敦趋势观察
- **"Forward Deployed AI Engineer（前线部署 AI 工程师）" 是伦敦当红新物种**——Distyl、Edra 都在招。这类岗**最贴近你想要的"Ai落地型"**：不是做 demo，而是"把 AI 部署进企业主干业务（金融/医疗/供应链），现场解决客户问题"。
- **Agent 专属岗位扎堆**（Oho、Arondite、DNV、Decagon 的 Software Engineer, Agents）——说明 "AI Agent 开发"确实是当前招聘热点。
- **行业横跨极广**：金融（Pay.UK）、律所（Dentons）、美妆（Charlotte Tilbury）、科技（Writer, Planet）——AI 落地已渗透各行业，不只是科技公司。

---

## 三、🔍 两个已核实到的重点公司（JD 要点）

### Distyl（伦敦，Forward Deployed AI Engineer）
官方 careers 页可核实要点：
- "建立生产级 AI 系统，**不做 demo**"——强调真实落地
- 覆盖金融/医疗/供应链/保险等**企业主干业务**
- 强调 **AI-native mindset**、快速交付（ship）、客户问题导向
- 面试：协作式 live coding、部分 take-home、系统与产品讨论；**AI 工具在所有环节被鼓励使用** ⭐

### Edra（伦敦，AI Engineer / Forward Deployed）
- Series A，红杉（Sequoia）等机构投资，伦敦+纽约
- 主营"专家知识捕获与规模化"
- 明确招聘重点是 AI Engineering 与 Software Engineering

> ⚠️ 两家薪资区间均未公开；Distyl 官网标注 in-office 在 SF/NYC，伦敦岗是否仍开放需进一步核实。

---

## 四、☑️ 面试会考察什么（行业通识，该岗位类通用）

> 以下为该类岗位的**通用行业共识**，不代表某家公司官方标准（未能逐条线上核实题库）。

### 技术面（Technical）
1. **Python 编程 + 算法题**——仍是门槛，但通常没大厂 CV/SWE 那么变态
2. **AI Agent 框架**：LangChain / LlamaIndex / AutoGen / CrewAI——会用什么、各自的取舍
3. **RAG 原理与工程化**：chunking、embedding、检索评估、幻觉（Hallucination）控制
4. **Prompt engineering**：怎么设计提示词、怎么调优
5. **系统设计**：怎么把一个 LLM 产品放上生产——限量、缓存、成本控制、eval、观测
6. **部署/云**：Docker、AWS/GCP——至少知道怎么把应用跑起来

### 行为面（Behavioural）
1. **讲一个你真实做过的 AI 项目**：问题→决策→结果（这是你的主场！）
2. **AI 工具使用方法论**：你怎么用 AI 工作、怎么和 AI 协作落地
3. **客户/产品导向**（Forward Deployed 类尤其看重）：能否把客户业务问题变成一个可交付的产物
4. **变更管理/与业务方沟通**：AI 落地不只是技术，还要推动人接受

---

## 五、对你（洛哥）的针对性结论

结合你的情况（MSc 统计、数据打底、AI 落地项目、代码功底一般、走 SME/中型企路线）：

1. **岗位真实存在且方向完全对口**——曼城和伦敦都有一大批"AI 应用/Agent 落地"岗，尤其 **Forward Deployed AI Engineer** 这个新物种，简直是为"懂业务 + 能落地 + 数据打底"的人量身定做。
2. **你的"代码功底一般"在中型/落地型岗不是死穴**——它们更看重"能不能把 AI 落地解决业务问题"，AI 工具还被鼓励使用，这正好弱化手撕代码的劣势。
3. **曼城 vs 伦敦**：
   - **曼城**：岗位少而实，性价比高，SME 为主，竞争温和，**适合你上手的首选**。有 Lloyds 银行 AI Lab、Adria、ConnexAI 等真实机会。
   - **伦敦**：岗位多、天花板高，但竞争狠、成本高；**Forward Deployed AI Engineer** 是你冲上限的优质目标。
4. **你最大短板要补**：即使不是大厂，**Python 编程 + 至少一个 Agent 框架（LangChain 等）基础**仍会考——这是"AI落地"岗绕不开的门槛，值得花时间补。

---

## 待办/下一步可补全项
- [ ] 登录 LinkedIn/Otta 深挖 3-5 家重点公司（Oscar、ConnexAI、Travel Counsellors、Distyl、Edra、Adria）的**完整 JD + 薪资**
- [ ] 核实 levels.fyi / Glassdoor 英国区 AI Engineer **薪资中位数**（行业通识）
- [ ] 把你两个项目按"Forward Deployed / AI 落地案例"重新包装成简历项目 + 面试讲稿
