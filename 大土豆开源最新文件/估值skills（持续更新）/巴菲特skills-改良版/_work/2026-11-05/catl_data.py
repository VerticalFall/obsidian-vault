# -*- coding: utf-8 -*-
"""宁德时代 300750.SZ · 巴菲特框架研究数据与模型参数（2026-11-05）"""

DATE = "2026-11-05"
PRICE_NOTE = "2026-11-05 午间"

# ---------- 市场与股本 ----------
PRICE = 265.94
SHARES = 46.2725          # 亿股
MARKET_CAP = PRICE * SHARES

# ---------- 资产负债表（2026Q3） ----------
CASH = 3698.1
TRADING_FA = 627.8
INTEREST_DEBT = 1899.2
NET_CASH = CASH + TRADING_FA - INTEREST_DEBT   # 2426.7
MINORITY = 363.4
TOTAL_ASSETS = 11831.7
TOTAL_LIAB = 7599.6
PARENT_EQUITY = 3868.8

# ---------- 盈利 ----------
NP_2026E = 906.0          # 亿，机构一致预期
EPS_2026E = NP_2026E / SHARES
EPS_2027E_BASE = 22.50    # 模型假设，低于一致预期 23.57
EPS_2027E_BEAR = 17.50
EPS_2027E_BULL = 25.00
DPS_2026E = 9.79          # 假设 50% 总派息
BPS = PARENT_EQUITY / SHARES

TTM_NP = 877.0
TTM_EPS = TTM_NP / SHARES

# ---------- DCF ----------
F0 = 490.0                # 2026E FCFF，亿
G1 = 0.12
FADE_YEARS = 10
WACC = 0.078
G_TERM = 0.025

BEAR_F0, BEAR_G1, BEAR_WACC = 435.0, 0.05, 0.086
BULL_F0, BULL_G1, BULL_WACC = 520.0, 0.155, 0.0745

PE_BASE, PE_BEAR, PE_BULL = 15.3, 12.5, 18.0
DCF_WEIGHT, PE_WEIGHT = 0.5, 0.5


def dcf(f0, g1, wacc, g_term=G_TERM, years=FADE_YEARS,
        net_cash=NET_CASH, minority=MINORITY, shares=SHARES):
    pv = 0.0
    f = f0
    for t in range(1, years + 1):
        g = g1 + (g_term - g1) * (t - 1) / (years - 1)
        f *= (1 + g)
        pv += f / (1 + wacc) ** t
    tv = f * (1 + g_term) / (wacc - g_term)
    ev = pv + tv / (1 + wacc) ** years
    equity = ev + net_cash - minority
    return {"ev": ev, "equity": equity, "value": equity / shares,
            "pv": pv, "tv": tv, "tv_pv": tv / (1 + wacc) ** years, "f10": f}


DCF_BASE = dcf(F0, G1, WACC)["value"]
DCF_BEAR = dcf(BEAR_F0, BEAR_G1, BEAR_WACC)["value"]
DCF_BULL = dcf(BULL_F0, BULL_G1, BULL_WACC)["value"]

PE_BASE_V = EPS_2027E_BASE * PE_BASE
PE_BEAR_V = EPS_2027E_BEAR * PE_BEAR
PE_BULL_V = EPS_2027E_BULL * PE_BULL

BLEND_BASE = DCF_BASE * DCF_WEIGHT + PE_BASE_V * PE_WEIGHT
BLEND_BEAR = DCF_BEAR * DCF_WEIGHT + PE_BEAR_V * PE_WEIGHT
BLEND_BULL = DCF_BULL * DCF_WEIGHT + PE_BULL_V * PE_WEIGHT

MOS = 1 - PRICE / BLEND_BASE
UPSIDE = BLEND_BASE / PRICE - 1
MOS20_PRICE = BLEND_BASE * 0.8

DCF_AT_PRICE_F0 = F0 * PRICE / DCF_BASE

# ---------- 历史财务 ----------
YEARS = ["2021", "2022", "2023", "2024", "2025"]
REVENUE = [1303.56, 3285.94, 4009.17, 3620.13, 4237.02]
NP = [159.31, 307.29, 441.21, 507.45, 722.01]
EPS = [6.876, 7.1766, 10.06, 11.58, 16.14]
ROE = [0.2152, 0.2467, 0.2404, 0.2413, 0.2491]
GM = [0.2628, 0.2025, 0.1919, 0.2444, 0.2627]
NM = [0.1222, 0.0935, 0.1101, 0.1402, 0.1704]
OCF = [429.08, 612.09, 928.26, 969.90, 1332.20]
CAPEX = [437.68, 482.15, 336.25, 311.80, 423.45]
FCF = [a - b for a, b in zip(OCF, CAPEX)]

# ---------- 2026 分季 ----------
Q_REV = [1291.31, 1477.86, 1652.21]
Q_NP = [207.38, 225.46, 212.46]
Q_GM = [0.2482, 0.2393, 0.2070]

# ---------- 分红 ----------
DIV_YEARS = ["2022", "2023", "2024", "2025", "2026E"]
DPS = [2.52, 2.011, 4.553, 7.964, 9.79]
PAYOUT = [0.351, 0.196, 0.393, 0.500, 0.500]

# ---------- 敏感性 ----------
WACC_GRID = [0.070, 0.074, 0.078, 0.082, 0.086]
G_GRID = [0.015, 0.020, 0.025, 0.030, 0.035]
SENS = [[dcf(F0, G1, w, g)["value"] for g in G_GRID] for w in WACC_GRID]

# ---------- 经营 ----------
SEGMENTS_2025 = [
    ("动力电池系统", 3165.1, 0.747, 0.238),
    ("储能电池系统", 624.4, 0.147, 0.267),
    ("电池材料及回收", 301.0, 0.071, 0.121),
    ("其他", 146.5, 0.035, 0.150),
]
SEGMENTS_2026H1 = [
    ("动力电池系统", 1921.2, 0.694, 0.206),
    ("储能电池系统", 532.6, 0.192, 0.240),
    ("电池材料及回收", 218.0, 0.079, 0.110),
    ("其他", 97.4, 0.035, 0.140),
]

SHARE_2025 = 0.392
SHARE_2024 = 0.380
SALES_2025 = 661.0        # GWh
CAPACITY_2025 = 772.0     # GWh
UTILIZATION_2025 = 0.969
UNDER_CONSTRUCTION = 321.0
OVERSEAS_REV_2025 = 1296.4
OVERSEAS_SHARE_2025 = 0.306
OVERSEAS_GM_2025 = 0.314
RND_2025 = 221.0

if __name__ == "__main__":
    print("market cap", round(MARKET_CAP, 1))
    print("EPS26", round(EPS_2026E, 2), "PE26", round(PRICE / EPS_2026E, 2))
    print("EPS27", EPS_2027E_BASE, "PE27", round(PRICE / EPS_2027E_BASE, 2))
    print("BPS", round(BPS, 2), "PB", round(PRICE / BPS, 2))
    print("TTM EPS", round(TTM_EPS, 2), "PE", round(PRICE / TTM_EPS, 2))
    print("DCF base/bear/bull", round(DCF_BASE, 1), round(DCF_BEAR, 1), round(DCF_BULL, 1))
    print("PE base/bear/bull", round(PE_BASE_V, 1), round(PE_BEAR_V, 1), round(PE_BULL_V, 1))
    print("blend", round(BLEND_BASE, 1), round(BLEND_BEAR, 1), round(BLEND_BULL, 1))
    print("MoS", round(MOS * 100, 1), "upside", round(UPSIDE * 100, 1))
    print("implied F0", round(DCF_AT_PRICE_F0, 1))
    print("sens")
    for row in SENS:
        print([round(x, 0) for x in row])
