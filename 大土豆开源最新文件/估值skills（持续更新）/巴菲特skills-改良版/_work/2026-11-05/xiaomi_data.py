# -*- coding: utf-8 -*-
"""小米集团 1810.HK 数据与估值（2026-11-05）"""

DATE = "2026-11-05"
PRICE_NOTE = "2026-11-05 收盘"
PRICE_HKD = 30.90
FX = 0.85601          # HKD/CNY 2026-11-05 中间价
PRICE = PRICE_HKD * FX  # 26.45 CNY
SHARES = 258.4         # 亿股
MARKET_CAP_HKD = PRICE_HKD * SHARES   # 7,984 亿港元
MARKET_CAP = MARKET_CAP_HKD * FX      # 6,835 亿元

NET_CASH = 1800.0      # 2026H1 现金储备 2,193 − 借款 393
MINORITY = 0.0
BPS = 8.9              # 估算：归母净资产约 2,300 亿 / 258.4 亿股

# 2026E / 2027E（经调整净利润，亿元）
NP_ADJ_2026E = 250.0
NP_ADJ_2027E_BASE = 350.0
NP_ADJ_2027E_BEAR = 280.0
NP_ADJ_2027E_BULL = 420.0
EPS_2027E_BASE = NP_ADJ_2027E_BASE / SHARES
EPS_2027E_BEAR = NP_ADJ_2027E_BEAR / SHARES
EPS_2027E_BULL = NP_ADJ_2027E_BULL / SHARES

# TTM 经调整净利：2025Q3 113.11 + 2025Q4 63 + 2026Q1 60.72 + 2026Q2 62.19
TTM_NP_ADJ = 299.02
TTM_PE = MARKET_CAP / TTM_NP_ADJ

# DCF
F0 = 200.0
G1 = 0.13
FADE_YEARS = 10
WACC = 0.096
G_TERM = 0.03
BEAR_F0, BEAR_G1, BEAR_WACC, BEAR_G = 160.0, 0.05, 0.106, 0.025
BULL_F0, BULL_G1, BULL_WACC, BULL_G = 230.0, 0.17, 0.090, 0.035

# PE
PE_BASE, PE_BEAR, PE_BULL = 22.0, 17.0, 25.0
DCF_WEIGHT, PE_WEIGHT = 0.5, 0.5


def dcf(f0=F0, g1=G1, wacc=WACC, g=G_TERM, years=FADE_YEARS):
    pv = 0.0
    fcf = f0
    rows = []
    for t in range(1, years + 1):
        growth = g1 - (g1 - g) * (t - 1) / (years - 1)
        fcf = fcf * (1 + growth)
        disc = 1 / (1 + wacc) ** t
        pv += fcf * disc
        rows.append((t, growth, fcf, disc, fcf * disc))
    tv = fcf * (1 + g) / (wacc - g)
    tv_pv = tv / (1 + wacc) ** years
    ev = pv + tv_pv
    equity = ev + NET_CASH - MINORITY
    return {"ev": ev, "equity": equity, "value": equity / SHARES,
            "pv": pv, "tv": tv, "tv_pv": tv_pv, "f10": fcf, "rows": rows}


DCF_BASE = dcf()["value"]
DCF_BEAR = dcf(BEAR_F0, BEAR_G1, BEAR_WACC, BEAR_G)["value"]
DCF_BULL = dcf(BULL_F0, BULL_G1, BULL_WACC, BULL_G)["value"]
PE_BASE_V = EPS_2027E_BASE * PE_BASE
PE_BEAR_V = EPS_2027E_BEAR * PE_BEAR
PE_BULL_V = EPS_2027E_BULL * PE_BULL
BLEND_BASE = DCF_BASE * DCF_WEIGHT + PE_BASE_V * PE_WEIGHT
BLEND_BEAR = DCF_BEAR * DCF_WEIGHT + PE_BEAR_V * PE_WEIGHT
BLEND_BULL = DCF_BULL * DCF_WEIGHT + PE_BULL_V * PE_WEIGHT
MOS = 1 - PRICE / BLEND_BASE
UPSIDE = BLEND_BASE / PRICE - 1
MOS20_PRICE = BLEND_BASE * 0.8
# 现价反推 F0：按基准 DCF 的倍数关系
DCF_AT_PRICE_F0 = F0 * (PRICE * SHARES - NET_CASH) / (DCF_BASE * SHARES - NET_CASH)

# 历史（亿元）
YEARS = ["2021", "2022", "2023", "2024", "2025"]
REVENUE = [3283.09, 2800.44, 2709.70, 3659.06, 4572.87]
NP = [193.4, 24.7, 174.8, 235.8, 415.66]
NP_ADJ = [220.35, 85.00, 192.73, 272.35, 391.66]
OCF = [428.0, -43.9, 413.0, 392.95, 341.42]
CAPEX = [50.0, 58.0, 62.69, 72.97, 127.69]
FCF = [o - c for o, c in zip(OCF, CAPEX)]
EPS = [0.76, 0.10, 0.70, 0.94, 1.62]
ROE = [12.0, 1.5, 10.0, 12.0, 18.0]  # 估算/约值

# 2026 季度
Q_REV = [991.42, 1089.22]
Q_NP = [47.23, 94.63]
Q_ADJ = [60.72, 62.19]
Q_DELIV = [80856, 104199]
Q_GM = [0.22, 0.198]

# 分部（2025 / 2026H1）
SEG_2025 = [
    ("智能手机", 1864.0, -2.8, 40.8, 10.9),
    ("IoT与生活消费", 1232.0, 18.3, 26.9, 21.0),
    ("互联网服务", 374.0, 9.7, 8.2, 76.5),
    ("智能电动汽车及AI", 1060.7, 223.8, 23.2, 24.3),
    ("其他", 41.2, -12.0, 0.9, 30.0),
]

# 2026Q2 分部
SEG_2026Q2 = [
    ("智能手机", 421.0, -7.5, 8.5),
    ("IoT与生活消费", 313.0, -19.2, 20.1),
    ("互联网服务", 90.0, -0.6, 76.8),
    ("智能电动汽车及AI", 249.0, 17.1, 19.2),
]

# 敏感性网格（WACC × g）
SENS_WACC = [0.090, 0.093, 0.096, 0.099, 0.102]
SENS_G = [0.025, 0.0275, 0.030, 0.0325, 0.035]
SENS = [[dcf(wacc=w, g=g)["value"] for g in SENS_G] for w in SENS_WACC]


def sanity():
    print("价格 CNY", round(PRICE, 2), "市值亿", round(MARKET_CAP, 0), "港元市值", round(MARKET_CAP_HKD, 0))
    print("2026E PE", round(MARKET_CAP / NP_ADJ_2026E, 1), "2027E PE", round(MARKET_CAP / NP_ADJ_2027E_BASE, 1), "TTM PE", round(TTM_PE, 1))
    print("DCF", round(DCF_BASE, 2), "bear", round(DCF_BEAR, 2), "bull", round(DCF_BULL, 2))
    print("PE", round(PE_BASE_V, 2), "bear", round(PE_BEAR_V, 2), "bull", round(PE_BULL_V, 2))
    print("BLEND", round(BLEND_BASE, 2), "bear", round(BLEND_BEAR, 2), "bull", round(BLEND_BULL, 2))
    print("MoS", round(MOS * 100, 1), "upside", round(UPSIDE * 100, 1), "20%价", round(MOS20_PRICE, 2))
    print("implied F0", round(DCF_AT_PRICE_F0, 1))
    for row in SENS:
        print([round(x, 1) for x in row])


if __name__ == "__main__":
    sanity()
