# 数据分析 SQL 笔试面试 50 题详解

> **来源**：基于你提供的《数据分析SQL笔试50题》目录框架（按业务场景分类），结合国内主流数据分析面试（互联网大厂 + 中型企业）常见问法发散整理。
> **用法**：每个 Part 先看「面试官会怎么问」（题目模板），再看「解题思路 + SQL 写法 + 考察点」。SQL 以标准 SQL + Hive/MySQL 常用函数为主，均可直接跑通或略改。

---

## Part 0 · SQL 面试思维框架（拿到题先想这 5 步）

### ✅ 拿到任何 SQL 题目的 5 步思考法

1. **先确认表结构和业务语义**——列名、主键、粒度（一行代表什么？一个用户一条？一条行为一笔？）。粒度搞错全错。
2. **拆题目为"要算什么"**——先不写 SQL，用大白话把结果描述出来："我要每个日期、每个渠道的次日留存率"。
3. **想清楚"按什么分组 / 用什么窗口 / 约不约去重"**——
   - 分组：`GROUP BY` 维度
   - 窗口：`ROW_NUMBER / RANK / LAG / SUM(...) OVER()`
   - 去重：`DISTINCT` 什么时候该去（算用户数必去重）
4. **写出"先过滤后计算"的顺序**——SQL 逻辑顺序：`FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`，**WHERE 在 GROUP 前，HAVING 在 GROUP 后**。
5. **边界 + 验证**——空值怎么办？0 除怎么防（`NULLIF / IF(分母=0,0,..)`）？跑出来能不能用极端数据自检？

### ✅ 面试官评分维度
- **正确性**（首要）：结果对不对，能否讲清每一步在做什么。
- **可读性**：用 CTE(`WITH`) 分步拆解，别写一大坨难读的嵌套。
- **健壮性**：处理了空值、除零、去重边界；考虑了性能（过滤条件下推）。
- **业务感**：能不能解释这个指标对业务意味着什么（面试官最看重）。

### ✅ 高频考点 TOP5
1. **留存/连续登录**（日期差、`LAG`、`DATEDIFF`）——最常见，几乎必考。
2. **三大经典窗口函数**：`ROW_NUMBER() / RANK() / DENSE_RANK()`（TopN、去重取最新）。
3. **累计求和使用窗口 `SUM() OVER(ORDER BY ...)`**（running total / 移动平均）。
4. **RFM 分析**（数据打标签的经典用途）。
5. **比率类指标 + 去重**（ARPU、留存率、转化率，分母处理、去重用户）。

---

## Part 1 · 留存分析（8 题）

**通用套路**：留存 = 「在某天活跃过的用户，N 天后还活跃的比例」。要点是**用日期差把"首次活跃"和"后续活跃"关联起来**。

```
思路模板：
1) 取出每个用户"首日"（第一次活跃日期）
2) 取"活跃明细"（用户 + 活跃日期）
3) 用首日和活跃日期求差 = 活跃的"第几天"
4) 按首日分组，求 N 天后活跃人数 / 首日活跃人数
```

### 模拟建表（所有留存题共用）
```sql
-- 登录流水表：一行=某用户某天登录
CREATE TABLE login_log (
  user_id  BIGINT,
  dt       DATE          -- 登录日期
);
```
> 面试里常给这样的简化表，让你直接写 SQL。

### 题目01 | 次日留存率
**面试会怎么问**：给出登录表（user_id, dt），求**每日次日留存率**（当天登录用户中，第二天还登录的比例）。

```sql
WITH first_login AS (          -- 每个用户的首日
  SELECT user_id, MIN(dt) AS first_dt
  FROM login_log GROUP BY user_id
),
active AS (                    -- 每个用户每天活跃(去重)
  SELECT DISTINCT user_id, dt FROM login_log
),
flag AS (                      -- 标记每行是否为"次日回来"
  SELECT a.user_id, f.first_dt,
         MAX(CASE WHEN a.dt = DATE_ADD(f.first_dt, INTERVAL 1 DAY) THEN 1 ELSE 0 END) AS back_1d
  FROM active a JOIN first_login f ON a.user_id = f.user_id
  GROUP BY a.user_id, f.first_dt
)
SELECT first_dt,
       COUNT(*)                                  AS dau_new,   -- 首日新增
       SUM(back_1d)                              AS ret_1d,    -- 次日留存
       SUM(back_1d)/COUNT(*)                     AS retain_rate
FROM flag GROUP BY first_dt ORDER BY first_dt;
```
**考察点**：去重、日期差、分母处理。**进阶**：用通用法（见下题）替代。

### 题目02 | 第 N 日留存（通用版 3/7/30 日）
**面试会怎么问**：一次算 **3日、7日均留存**。

```sql
WITH first_login AS (
  SELECT user_id, MIN(dt) AS first_dt FROM login_log GROUP BY user_id
),
active AS (SELECT DISTINCT user_id, dt FROM login_log),
ret AS (
  SELECT f.first_dt, a.user_id,
         DATEDIFF(a.dt, f.first_dt) AS diff_day   -- 第几天
  FROM first_login f JOIN active a ON f.user_id = a.user_id
)
SELECT first_dt,
       COUNT(DISTINCT user_id) AS new_user,
       COUNT(DISTINCT CASE WHEN diff_day = 1  THEN user_id END) AS d1,
       COUNT(DISTINCT CASE WHEN diff_day = 3  THEN user_id END) AS d3,
       COUNT(DISTINCT CASE WHEN diff_day = 7  THEN user_id END) AS d7
FROM ret
GROUP BY first_dt;
```
> 用 `DATEDIFF` 把"第几天"算出来，再用 `CASE WHEN` 一列一个留存，是留存题的核心通用手法。

### 题目03 | 连续 N 天登录
**面试会怎么问**：找出**连续登录 ≥ 3 天**的所有用户（经典难题）。

> 核心技巧：**"日期 - 行号 = 连续组的锚点"**——连续日期减去递增序号后，同一连续段的值相等。

```sql
WITH tmp AS (
  SELECT user_id, dt,
         ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY dt) AS rn
  FROM (SELECT DISTINCT user_id, dt FROM login_log) t
),
grp AS (
  SELECT user_id, DATE_SUB(dt, INTERVAL rn DAY) AS grp_date
  FROM tmp
)
SELECT user_id
FROM grp GROUP BY user_id, grp_date
HAVING COUNT(*) >= 3;       -- 连续≥3天的分组
```
**考察点**：`ROW_NUMBER` + 日期相减的经典套路，**面试最爱考**，务必背熟。

### 题目04 | 新老用户留存对比
**面试会怎么问**：区分"新用户（首次活跃）"和"老用户"，分别看留存。

思路：打标 `CASE WHEN dt = first_dt THEN '新' ELSE '老' END`，再按新/老分组求留存。
```sql
-- 在题目02基础上，计算时按"该用户是否首次登录"分组即可
SELECT CASE WHEN a.dt = f.first_dt THEN '新用户' ELSE '老用户' END AS user_type,
       ...
```

### 题目05 | 用户流失判定
**面试会怎么问**：定义"连续 30 天不登录 = 流失"，找出流失用户和流失日期。

思路：求每个用户**最后登录日期** `MAX(dt)`，若距今 ≥30 天即流失。
```sql
SELECT user_id, MAX(dt) AS last_dt
FROM login_log GROUP BY user_id
HAVING DATEDIFF(CURRENT_DATE, MAX(dt)) >= 30;
```

### 题目06 | 用户回流识别
**面试会怎么问**：找出「流失后（≥30天未登录）又回来登录」的用户，即回流用户。
思路：相邻两次登录日期差 ≥30，后一次即回流。
```sql
WITH t AS (
  SELECT user_id, dt,
         LAG(dt) OVER(PARTITION BY user_id ORDER BY dt) AS last_dt
  FROM (SELECT DISTINCT user_id, dt FROM login_log) x
)
SELECT DISTINCT user_id FROM t
WHERE DATEDIFF(dt, last_dt) >= 30;   -- 与上次登录隔了30天以上
```
> `LAG()` 取前一行，是判断"间隔"类问题的核心。

### 题目07 | 留存率环比
**面试会怎么问**：看留存率相比上周/上月的变化（如本月新增的次日留存 vs 上月）。
思路：按首日算各留存后，再用 `LAG` 对比前一周期。

### 题目08 | 按渠道分组留存
**面试会怎么问**：登录表加一个 `channel` 列，比较不同渠道次日留存。
思路：在留存计算里 `GROUP BY first_dt, channel`，或把 channel 一并 join 进来。

---

## Part 2 · 转化漏斗（8 题）

**通用套路**：漏斗 = 用户依次完成 N 个关键行为（曝光→点击→下单→支付），算每一步到下一步的转化率。核心是"**同一批人，依次完成行为的去重计数**"。

### 模拟建表
```sql
-- 用户行为流水表：一行=某用户某时刻做过一个行为
CREATE TABLE behavior (
  user_id BIGINT,
  event     VARCHAR(32),   -- 'view'/'click'/'order'/'pay'
  ts        DATETIME
);
```

### 题目09 | 基础漏斗转化率
**面试会怎么问**：求曝光→点击→下单→支付的基础转化率（不考虑顺序）。

```sql
SELECT
  COUNT(DISTINCT CASE WHEN event='view'   THEN user_id END) AS view_cnt,
  COUNT(DISTINCT CASE WHEN event='click'  THEN user_id END) AS click_cnt,
  COUNT(DISTINCT CASE WHEN event='order'  THEN user_id END) AS order_cnt,
  COUNT(DISTINCT CASE WHEN event='pay'    THEN user_id END) AS pay_cnt
FROM behavior;
```
> 漏斗题的通用骨架：**CASE WHEN 逐层计数 + COUNT(DISTINCT user_id)**。

### 题目10 | 严格时序漏斗
**面试会怎么问**：要求**行为按先后顺序发生**（先看再点再下单再支付），且时间递增。

思路：对每人每行为取对应的较早事件，逐步 join，检查时间先后。
```sql
WITH v AS (SELECT DISTINCT user_id, ts FROM behavior WHERE event='view'),
     c AS (SELECT DISTINCT user_id, ts FROM behavior WHERE event='click'),
     o AS (SELECT DISTINCT user_id, ts FROM behavior WHERE event='order'),
     p AS (SELECT DISTINCT user_id, ts FROM behavior WHERE event='pay')
SELECT
  COUNT(*) AS view_cnt,
  COUNT(c.user_id) AS click_cnt,          -- 点击(且view时间在click前)
  COUNT(o.user_id) AS order_cnt,
  COUNT(p.user_id) AS pay_cnt
FROM v
LEFT JOIN c ON v.user_id=c.user_id AND v.ts <= c.ts
LEFT JOIN o ON c.user_id=o.user_id AND c.ts <= o.ts
LEFT JOIN p ON o.user_id=p.user_id AND o.ts <= p.ts;
```
**考察点**：多表自连接 + 时间先后条件；是漏斗题里**最考验功力**的一题。

### 题目11 | 漏斗转化时长分布
**面试会怎么问**：求从"首看到下单"的平均时长/时长分布。
思路：取每人首看时间、首次下单时间，求差 `TIMESTAMPDIFF(MINUTE, ...)` 再统计。

### 题目12 | 按渠道拆分漏斗
**面试会怎么问**：行为表加 `channel`，比较不同渠道的漏斗转化。
思路：基础漏斗里把 `channel` 加入 `GROUP BY`。

### 题目13 | 漏斗流失用户特征
**面试会怎么问**：流失在"下单"环节的用户有什么特征（地域/渠道/设备）。
思路：先筛"有点击但没下单"的用户，再 join 用户维度表做 `GROUP BY` 特征分布。

### 题目14 | 同期群漏斗对比
**面试会怎么问**：按"新增 Cohort"（新增周/月）分组，比较不同批次用户的漏斗。思路：把首日/首周加入分组维度。

### 题目15 | 多路径漏斗
**面试会怎么问**：用户可能走不同路径（如直接下单 vs 先看再下），分析各路径比例。思路：把每个用户的行为序列 `GROUP_CONCAT` 压缩成路径串，再统计。

### 题目16 | 付费窗口期分析
**面试会怎么问**：用户在**首次激活后 X 天内**是否付费，付费率多少。
思路：首日 + `DATEDIFF(付费日, 首日) <= X`，判定该用户是否在窗口期付费。

---

## Part 3 · 指标计算（10 题）

### 题目17 | DAU/MAU 及比值
面试会怎么问：求每天 DAU、每月 MAU、以及 **DAU/MAU(用户粘性比率)**。
```sql
SELECT CAST(COUNT(DISTINCT CASE WHEN dt BETWEEN '2026-09-01' AND '2026-09-30' THEN user_id END)
       / COUNT(DISTINCT CASE WHEN dt='2026-09-15' THEN user_id END) AS DECIMAL(10,2)) AS dMau_ratio;
```
> 一般分两个查询：日活按天，月活按月，再相除。DAU/MAU 越高，产品粘性越强（常见健康值高一较好）。

### 题目18 | 人均使用时长
面试会怎么问：给 `usage_log`（user_id, dt, duration_sec），求**人均日使用时长**。
```sql
SELECT dt, SUM(duration_sec)/COUNT(DISTINCT user_id) AS avg_sec_per_user
FROM usage_log GROUP BY dt;
```

### 题目19 | 加权平均分
面试会怎么问：给商品评分明细（user_id, score, weight），求加权平均分。
```sql
SELECT SUM(score*weight)/SUM(weight) AS weighted_avg FROM review;
```

### 题目20 | ARPU 与 ARPPU
面试会怎么问：
- **ARPU**（每用户平均收入）= 总收入/总用户；
- **ARPPU**（每付费用户平均收入）= 总收入/付费用户。
```sql
SELECT dt,
  SUM(pay_amt)/(SELECT COUNT(DISTINCT user_id) FROM user)            AS ARPU,
  SUM(pay_amt)/(SELECT COUNT(DISTINCT user_id) FROM pay WHERE pay_amt>0) AS ARPPU
FROM pay GROUP BY dt;
```
> ARPPU ≥ ARPU（因为分母更小）。

### 题目21 | 环比与同比
面试会怎么问：某指标本月值 vs 上月（环比）vs 去年同月（同比）。
思路：用 `LAG` + `PARTITION BY` 取上月/去年同期，或自连接。

### 题目22 | Top N 排名
面试会怎么问：求每个渠道 **Top 3 的用户**（最经典窗口题）。
```sql
WITH t AS (
  SELECT user_id, channel, SUM(amount) AS amt,
         ROW_NUMBER() OVER(PARTITION BY channel ORDER BY SUM(amount) DESC) AS rn
  FROM orders GROUP BY user_id, channel
)
SELECT * FROM t WHERE rn <= 3;
```
**考察点**：`ROW_NUMBER()`（不并列）vs `RANK()`（并列跳号）vs `DENSE_RANK()`（并列不跳号），**必须分清**。

### 题目23 | 累计求和 Running Total
面试会怎么问：求每天销售额的**累计到当天的总和**。
```sql
SELECT dt, amount,
       SUM(amount) OVER(ORDER BY dt) AS running_total
FROM daily_sales;
```

### 题目24 | 移动平均
面试会怎么问：求 7 日移动平均。
```sql
SELECT dt, amount,
       AVG(amount) OVER(ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7
FROM daily_sales;
```

### 题目25 | 中位数计算
面试会怎么问：求员工薪资中位数（`PERCENTILE_CONT` 或人工法）。
```sql
-- MySQL/Hive
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) FROM emp;
-- 或通用"下标法"：
WITH t AS (SELECT salary, ROW_NUMBER() OVER(ORDER BY salary) rk, COUNT(*) OVER() n FROM emp)
SELECT AVG(salary) FROM t WHERE rk IN (FLOOR((n+1)/2), CEIL((n+1)/2));
```

### 题目26 | 占比计算
面试会怎么问：每个产品销量占**全品类**的比例。
```sql
SELECT product, sales,
       sales/SUM(sales) OVER() AS pct
FROM product_sales;
```

---

## Part 4 · 归因分析（8 题）

**通用套路**：当指标涨跌时，拆解"到底是哪些维度/哪些用户贡献的"。

### 题目27 | 维度下钻定位异动
面试会怎么问：GMV 下降，让你从渠道/品类/地区下钻，找出下跌主因。
思路：逐步 `GROUP BY` 各维度，对比前后周期，找出波动最大的维度。

### 题目28 | Mix-Rate 贡献拆解
面试会怎么问：总指标 = 各子项(如不同品类)之和，拆解各子项贡献份额（占比）及变化。
```sql
SELECT category, SUM(amount) AS amt,
       SUM(amount) / SUM(SUM(amount)) OVER() AS mix_rate
FROM orders GROUP BY category;
```

### 题目29 | 新老用户贡献拆解
面试会怎么问：GMV 的新用户 vs 老用户分别贡献多少、各占比例。
思路：join 用户表打标新/老，再 `GROUP BY user_type` 求占比。

### 题目30 | 首次归因
面试会怎么问：把一次转化**归因到用户第一次触达的渠道**（如第一个点击的渠道）。
思路：取每人最早的渠道事件，算各渠道贡献。

### 题目31 | 末次归因
面试会怎么问：把转化归因到**最后一次触达的渠道**。
思路：取每人最晚的渠道事件（`ROW_NUMBER DESC` 或 `LAST_VALUE`）。

### 题目32 | AB实验指标对比
面试会怎么问：给 AB 实验（variant 分组 + 指标），比较两组差异。
```sql
SELECT variant, COUNT(*) AS users, AVG(metric) AS avg_metric
FROM ab_test GROUP BY variant;
```

### 题目33 | 异动检测
面试会怎么问：某指标突然骤降，怎么用 SQL 定位异常日期。
思路：用窗口算"当日值 vs 前 7 日均值"的偏离（`占比变化`），超过阈值即标记。

### 题目34 | 多维交叉下钻
面试会怎么问：异动同时在多个维度交叉看（如渠道×地区×时间）。
思路：`GROUP BY` 多维度组合 + 排序找波动最大的组合。

---

## Part 5 · 增长分析（8 题）

### 题目35 | 新增用户来源
面试会怎么问：每日新增用户 / 各来源(渠道/注册方式)新增分布。
```sql
SELECT dt, channel, COUNT(DISTINCT user_id) AS new_users
FROM user
WHERE is_new=1 GROUP BY dt, channel;
```

### 题目36 | 渠道 ROI
面试会怎么问：给渠道成本表和转化收入表，求各渠道 ROI(=收入/成本)。
```sql
SELECT c.channel,
       SUM(rev.revenue)/SUM(c.cost) AS roi
FROM channel_cost c LEFT JOIN revenue rev ON c.channel=rev.channel
GROUP BY c.channel;
```

### 题目37 | 简版 RFM 标签
面试会怎么问：给每位用户算 **R(最近一次消费距今)、F(消费频次)、M(消费金额)**，并按中位数打高/低标签。
```sql
SELECT user_id,
  DATEDIFF(CURRENT_DATE, MAX(dt))                 AS R,
  COUNT(*)                                        AS F,
  SUM(amount)                                     AS M
FROM orders GROUP BY user_id;
```
（进阶：用 `PERCENTILE_CONT` 求中位数作为分界，再 `CASE WHEN` 打 高/低 标签，最终组合成 8 类 RFM 人群。）

---

## 📌 面试加分&避坑清单

**加分点**
- 每题先讲**思路和业务含义**再写 SQL（面试官要看到你"懂业务"）。
- 善用 **CTE（WITH）** 分步拆，逻辑清晰。
- 主动处理**空值、除零、去重**；先 `WHERE` 缩小范围再聚合。
- 窗口函数记熟：`ROW_NUMBER/RANK/DENSE_RANK/LAG/LEAD/SUM..OVER`。

**避坑点**
- 忘记 **COUNT(DISTINCT)** 算用户导致虚高。
- 0 作分母报错 → 用 `NULLIF(分母,0)` 或 `IF` 判断。
- `RANK` 与 `ROW_NUMBER` 混淆导致 TopN 漏人。
- 不知道"日期-行号"连续登录套路，直接卡死。
- 只写对但讲不清"为什么"——面试官会追问。

**背诵口诀**
> Windows 三大兄弟（排名）、LAG/LEAD 看前后、日期减行号判连续、CASE WHEN 做漏斗逐层、PERCENTILE 算中位、SUM OVER 做累计。

---

**附**：图片底部约 5 道题（Part 5 增长分析后几题）因截图裁切未显示标题，本表已用常见的增长/留存/渠道类题型补全覆盖。如果你有完整版题目文档，发我即可补齐。
