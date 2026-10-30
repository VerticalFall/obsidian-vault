# -*- coding: utf-8 -*-
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

@dataclass
class Company:
    code: str
    ticker: str
    name: str
    market: str
    industry: str
    subtitle: str
    price: float
    shares: float          # 亿股
    market_cap: float      # 亿元, computed
    net_debt: float        # 亿元
    minority: float        # 亿元
    bps: float
    eps_2026e: float
    dps_2026e: float
    net_profit_2026e: float
    roe_2026e: float
    # history 2021-2025
    years: List[str]
    revenue: List[float]
    net_profit: List[float]
    eps: List[float]
    roe: List[float]
    gross_margin: List[float]
    net_margin: List[float]
    debt_ratio: List[float]
    dps: List[float]
    payout: List[float]
    # valuation primary
    method1_name: str
    method1_value: float
    method2_name: str
    method2_value: float
    method3_name: str = ""
    method3_value: float = 0.0
    method1_weight: float = 0.5
    method2_weight: float = 0.5
    method3_weight: float = 0.0
    # scenarios
    scenario_values: Dict[str, float] = field(default_factory=dict)
    # conclusions
    conclusion: str = ""
    conclusion_short: str = ""
    confidence: str = ""
    rating: str = ""
    # key metrics
    key_rows: List[List[str]] = field(default_factory=list)

    def finalize(self):
        self.market_cap = self.price * self.shares
        vals = [(self.method1_value, self.method1_weight),
                (self.method2_value, self.method2_weight)]
        if self.method3_value:
            vals.append((self.method3_value, self.method3_weight))
        self.blended_value = sum(v*w for v,w in vals)/sum(w for _,w in vals)
        self.margin_of_safety = 1 - self.price/self.blended_value
        self.upside = self.blended_value/self.price - 1
        self.pe_2026e = self.price/self.eps_2026e
        self.dividend_yield_2026e = self.dps_2026e/self.price
        self.pb = self.price/self.bps

CJ = Company(
    code="600900.SH", ticker="600900", name="长江电力", market="A股",
    industry="水电 / 公用事业",
    subtitle="水电公用事业 · 2026H1 净利 +13.0%｜Q3 发电量 -14.9%",
    price=29.74, shares=244.68217716, market_cap=0, net_debt=2734.9, minority=119.8,
    bps=8.83, eps_2026e=1.316, dps_2026e=0.92, net_profit_2026e=322.0, roe_2026e=14.6,
    years=["2021","2022","2023","2024","2025"],
    revenue=[556.46,688.63,781.44,844.92,862.42],
    net_profit=[262.73,237.26,272.45,324.96,345.03],
    eps=[1.1553,0.9697,1.1135,1.3281,1.4101],
    roe=[14.9,11.6,12.7,15.8,16.0],
    gross_margin=[62.1,57.1,57.8,59.1,61.7],
    net_margin=[47.2,34.5,34.9,38.5,40.0],
    debt_ratio=[42.1,55.7,62.9,60.8,58.3],
    dps=[0.8153,0.8533,0.82,0.943,1.00],
    payout=[70.6,88.0,73.6,71.0,70.9],
    method1_name="FCFF DCF",
    method1_value=30.17,
    method2_name="DDM",
    method2_value=25.00,
    method1_weight=0.5, method2_weight=0.5,
    scenario_values={"悲观":19.73,"基准":27.59,"乐观":35.67},
    conclusion="合理偏贵：好资产，价格已在上沿；现价较基准高约 7.8%，无安全边际。",
    conclusion_short="3.1% 股息率、22.6 倍 PE；好资产，价格已在上沿",
    confidence="中高",
    rating="合理偏贵",
    key_rows=[
        ["FCFF DCF", "¥30.17", "现价 ¥29.74", "接近基准"],
        ["DDM", "¥25.00", "2026E DPS ¥0.92", "股息模型偏谨慎"],
        ["PB", "3.37x", "ROE 14.6%", "高 ROE 支撑"],
        ["2026E 股息率", "3.1%", "10Y 1.62%", "利差约 148bp"],
    ],
)
CJ.finalize()

PA = Company(
    code="000001.SZ", ticker="000001", name="平安银行", market="A股",
    industry="股份制银行",
    subtitle="股份制银行 · 2026Q3 营收 +2.4%、净利 +2.2%",
    price=11.64, shares=194.06, market_cap=0, net_debt=0, minority=0,
    bps=24.56, eps_2026e=2.24, dps_2026e=0.65, net_profit_2026e=435.0, roe_2026e=8.8,
    years=["2021","2022","2023","2024","2025"],
    revenue=[1693.83,1798.95,1646.99,1466.95,1314.42],
    net_profit=[363.36,455.16,464.55,445.08,426.33],
    eps=[1.73,2.20,2.25,2.15,2.07],
    roe=[10.85,12.36,11.38,10.08,9.15],
    gross_margin=[0,0,0,0,0],
    net_margin=[21.5,25.3,28.2,30.3,32.4],
    debt_ratio=[92.0,91.8,91.5,91.4,90.7],
    dps=[0.228,0.285,0.719,0.608,0.596],
    payout=[13.2,13.0,32.0,28.3,28.8],
    method1_name="剩余收益 RI",
    method1_value=12.28,
    method2_name="DDM",
    method2_value=8.13,
    method1_weight=0.7, method2_weight=0.3,
    scenario_values={"悲观":8.52,"基准":11.03,"乐观":15.34},
    conclusion="静态便宜、动态偏贵：0.47 倍 PB 已把 ROE 下行定价；DDM 受低分红率拖累，现价高于基准约 5.5%，安全边际不足。",
    conclusion_short="0.47 倍 PB、5.6% 股息率；静态便宜，ROE 低于股权成本",
    confidence="中低",
    rating="合理偏贵",
    key_rows=[
        ["剩余收益 RI", "¥12.28", "现价 ¥11.64", "高于现价 5.5%"],
        ["DDM", "¥8.13", "2026E DPS ¥0.65", "低分红率拖累"],
        ["P/B", "0.47x", "ROE 8.8%", "低 PB 有原因"],
        ["2026E 股息率", "5.6%", "10Y 1.62%", "利差约 396bp"],
    ],
)
PA.finalize()

SH = Company(
    code="601088.SH", ticker="601088", name="中国神华", market="A股",
    industry="煤炭 / 一体化能源",
    subtitle="煤炭一体化 · 2026Q3 净利 +3.8%｜千亿收购并表",
    price=51.99, shares=216.89434304, market_cap=0, net_debt=285.9, minority=969.25,
    bps=20.50, eps_2026e=2.60, dps_2026e=1.95, net_profit_2026e=565.0, roe_2026e=12.0,
    years=["2021","2022","2023","2024","2025"],
    revenue=[3356.40,3445.33,3430.74,3397.88,2949.16],
    net_profit=[500.84,696.48,596.94,558.05,528.49],
    eps=[2.52,3.505,3.004,2.809,2.66],
    roe=[13.6,18.1,14.9,13.5,12.8],
    gross_margin=[32.9,39.0,35.9,34.1,35.1],
    net_margin=[14.9,20.2,17.4,16.4,21.3],
    debt_ratio=[26.6,26.1,24.1,25.7,33.2],
    dps=[2.54,2.55,2.26,2.26,2.01],
    payout=[100.8,72.8,75.2,80.5,79.1],
    method1_name="FCFF DCF",
    method1_value=38.19,
    method2_name="DDM",
    method2_value=32.50,
    method3_name="PE",
    method3_value=39.00,
    method1_weight=0.5, method2_weight=0.3, method3_weight=0.2,
    scenario_values={"悲观":25.55,"基准":36.64,"乐观":50.09},
    conclusion="昂贵：现价接近乐观情景，19–20 倍 PE 为周期高位盈利付费；收购推高杠杆与少数股东权益，A/H 溢价显著。",
    conclusion_short="20.0 倍 PE、3.8% 股息率；现价接近乐观情景，昂贵",
    confidence="中高",
    rating="昂贵",
    key_rows=[
        ["FCFF DCF", "¥38.19", "现价 ¥51.99", "高 36%"],
        ["DDM", "¥32.50", "2026E DPS ¥1.95", "股息模型更低"],
        ["PE", "20.0x", "周期中枢 12–15x", "为高位盈利付费"],
        ["2026E 股息率", "3.8%", "10Y 1.62%", "利差约 213bp"],
    ],
)
SH.finalize()

COMPANIES=[CJ,PA,SH]
if __name__=="__main__":
    for c in COMPANIES:
        print(c.name, c.code, 'mcap',round(c.market_cap,2),'blend',round(c.blended_value,2),'MoS',round(c.margin_of_safety*100,1),'PE',round(c.pe_2026e,2),'yield',round(c.dividend_yield_2026e*100,2),'PB',round(c.pb,2))
        print(' methods',c.method1_value,c.method2_value,c.method3_value)
