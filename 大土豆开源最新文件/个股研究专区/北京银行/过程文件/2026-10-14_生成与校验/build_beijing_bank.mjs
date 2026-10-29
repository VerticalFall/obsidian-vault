import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "C:/Users/Administrator/Desktop/0000-最新研报整理/红利专区文件/outputs/北京银行估值_20261014";
const outputPath = path.join(outputDir, "北京银行一图流估值_20261014.xlsx");
const previewDir = path.join(outputDir, "previews");
await fs.mkdir(previewDir, { recursive: true });

const wb = Workbook.create();

const C = {
  navy: "#17365D",
  blue: "#2F75B5",
  blue2: "#5B9BD5",
  lightBlue: "#D9EAF7",
  paleBlue: "#EDF4FB",
  green: "#70AD47",
  lightGreen: "#E2F0D9",
  amber: "#FFC000",
  lightAmber: "#FFF2CC",
  red: "#C00000",
  lightRed: "#FCE4D6",
  gray: "#F2F2F2",
  midGray: "#D9E1F2",
  rule: "#B4C6E7",
  text: "#1F2937",
  white: "#FFFFFF",
  formulaGreen: "#008000",
  inputBlue: "#0000FF",
};
const FONT = "Arial";

const history = [
  ["2016", 474.56, 178.02, 0.96, 8.17, 0.1492, 0.0090, "n.a.", 0.0127, 2.5606, 0.0826, 0.2581, 21163.39, 8999.07, 11509.04, 0.250, 9.76],
  ["2017", 503.53, 187.33, 0.99, 7.43, 0.1377, 0.0085, "n.a.", 0.0124, 2.6557, 0.0892, 0.2685, 23298.05, 10771.01, 12686.98, 0.267, 7.15],
  ["2018", 554.88, 200.02, 0.91, 8.26, 0.1089, 0.0082, 0.0188, 0.0146, 2.1751, 0.0893, 0.2519, 25728.65, 12618.11, 13860.06, 0.286, 5.61],
  ["2019", 631.29, 214.41, 0.98, 8.95, 0.1145, 0.0081, 0.0196, 0.0140, 2.2469, 0.0922, 0.2323, 27370.40, 14519.09, 15451.30, 0.305, 5.68],
  ["2020", 642.99, 214.84, 0.98, 9.52, 0.1065, 0.0077, 0.0192, 0.0157, 2.1595, 0.0942, 0.2207, 29000.14, 15736.57, 16561.49, 0.300, 4.84],
  ["2021", 662.75, 222.26, 1.02, 10.27, 0.1029, 0.0075, 0.0183, 0.0144, 2.1022, 0.0986, 0.2496, 30589.59, 16732.38, 16993.37, 0.305, 4.44],
  ["2022", 662.76, 247.60, 1.02, 10.91, 0.0960, 0.0077, 0.0176, 0.0143, 2.1004, 0.0954, 0.2655, 33879.52, 17973.19, 19133.58, 0.310, 4.31],
  ["2023", 667.11, 256.24, 1.06, 11.78, 0.0932, 0.0072, 0.0154, 0.0132, 2.1678, 0.0921, 0.2888, 37486.79, 20155.52, 20697.91, 0.320, 4.53],
  ["2024", 704.20, 263.34, 1.09, 12.73, 0.0865, 0.0066, 0.0147, 0.0131, 2.0875, 0.0895, 0.2893, 42191.86, 22099.75, 24494.25, 0.320, 6.15],
  ["2025", 680.36, 200.86, 0.78, 12.97, 0.0611, 0.0044, 0.0127, 0.0129, 2.0021, 0.0837, 0.3090, 49382.73, 23997.55, 26950.00, 0.278, 5.48],
  ["2026H1", 382.48, 159.00, 0.71, 13.48, 0.1060, 0.0066, 0.0126, 0.0130, 1.9959, 0.0891, 0.2347, 47429.66, 24020.57, 28199.58, 0.130, 5.62],
];

const peers = [
  ["北京银行", "601169.SH", 5.62, 5.68, 0.42, 0.1060, 0.0126, 0.0130, 1.9959, 0.0891, 0.0560, 0.0563, 13.48],
  ["上海银行", "601229.SH", 9.68, 5.71, 0.54, 0.1050, 0.0115, 0.0142, 1.9825, 0.1068, 0.0548, 0.0051, 18.12],
  ["江苏银行", "600919.SH", 12.46, 6.33, 0.84, 0.1572, 0.0164, 0.0081, 3.0483, 0.0867, 0.0911, 0.0809, 14.79],
  ["南京银行", "601009.SH", 11.96, 6.47, 0.77, 0.1450, 0.0179, 0.0082, 3.0611, 0.0937, 0.1094, 0.0817, 15.62],
  ["宁波银行", "002142.SZ", 35.29, 7.49, 0.96, 0.1424, 0.0170, 0.0076, 3.7335, 0.0953, 0.1154, 0.1212, 36.76],
  ["杭州银行", "600926.SH", 17.08, 6.14, 0.88, 0.1774, 0.0139, 0.0076, 4.7196, 0.0952, 0.0475, 0.0987, 19.84],
  ["成都银行", "601838.SH", 19.31, 6.03, 0.91, 0.1498, 0.0167, 0.0068, 4.2606, 0.0897, 0.0413, 0.0435, 21.76],
];

const sheetNames = ["一图流", "投资结论", "估值系统", "估值敏感性", "股息估值", "财务十年", "资产质量", "同业比较", "巴菲特框架", "数据与来源"];
for (const name of sheetNames) wb.worksheets.add(name);

function sheet(name) { return wb.worksheets.getItem(name); }
function setBase(ws, address) {
  const r = ws.getRange(address);
  r.format.horizontalAlignment = "center";
  r.format.verticalAlignment = "center";
  r.format.wrapText = true;
  return r;
}
function title(ws, address, text, subtitle) {
  ws.mergeCells(address);
  const r = ws.getRange(address);
  r.values = [[text]];
  r.format.font = { name: FONT, size: 16, bold: true, color: C.navy };
  r.format.horizontalAlignment = "center";
  r.format.verticalAlignment = "center";
  r.format.rowHeight = 30;
  if (subtitle) {
    const [left, right] = address.split(":");
    const row = Number(left.match(/\d+/)[0]) + 1;
    const startCol = left.match(/[A-Z]+/)[0];
    const endCol = right.match(/[A-Z]+/)[0];
    ws.mergeCells(`${startCol}${row}:${endCol}${row}`);
    const s = ws.getRange(`${startCol}${row}:${endCol}${row}`);
    s.values = [[subtitle]];
    s.format.font = { name: FONT, size: 9, italic: true, color: "#667085" };
    s.format.horizontalAlignment = "center";
    s.format.verticalAlignment = "center";
  }
}
function section(ws, address, text, fill = C.navy) {
  ws.mergeCells(address);
  const r = ws.getRange(address);
  r.values = [[text]];
  r.format = {
    fill,
    font: { name: FONT, size: 10, bold: true, color: C.white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: fill },
  };
  r.format.rowHeight = 22;
}
function header(ws, address) {
  ws.getRange(address).format = {
    fill: C.blue,
    font: { name: FONT, size: 10, bold: true, color: C.white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: C.white },
  };
}
function bodyTable(ws, address) {
  ws.getRange(address).format.borders = {
    insideHorizontal: { style: "thin", color: "#DDE3EA" },
    bottom: { style: "thin", color: C.rule },
    left: { style: "thin", color: C.rule },
    right: { style: "thin", color: C.rule },
  };
}
function inputStyle(ws, address) {
  ws.getRange(address).format = {
    fill: C.lightAmber,
    font: { name: FONT, size: 10, color: C.inputBlue },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: C.amber },
  };
}
function linkedStyle(ws, address) {
  ws.getRange(address).format.font = { name: FONT, size: 10, color: C.formulaGreen };
}
function col(ws, letter, width, rows = 220) { ws.getRange(`${letter}1:${letter}${rows}`).format.columnWidth = width; }
function rowHeight(ws, start, end, height) { ws.getRange(`A${start}:Z${end}`).format.rowHeight = height; }
function fmt(ws, address, code) { ws.getRange(address).format.numberFormat = code; }
function addChart(ws, type, source, position, chartTitle, yFormat = "0.00") {
  const chart = ws.charts.add(type, source);
  chart.title = chartTitle;
  chart.titleTextStyle.fontSize = 12;
  chart.titleTextStyle.typeface = FONT;
  chart.legend = { position: "top", textStyle: { typeface: FONT, fontSize: 10 } };
  chart.xAxis = { axisType: "textAxis", textStyle: { typeface: FONT, fontSize: 9 } };
  chart.yAxis = { numberFormatCode: yFormat, numberFormatSourceLinked: false, textStyle: { typeface: FONT, fontSize: 9 } };
  chart.setPosition(position[0], position[1]);
  for (const [i, s] of chart.series.items.entries()) {
    const color = [C.blue, C.green, C.amber, "#A5A5A5", "#8064A2"][i % 5];
    s.fill = color;
    s.line = { fill: color, style: "solid", width: 2 };
  }
  return chart;
}

// 估值敏感性：模型的权威输入放在本页，以便原生双变量数据表直接驱动估值结果。
{
  const ws = sheet("估值敏感性");
  ws.showGridLines = false;
  ws.tabColor = C.blue;
  title(ws, "A2:M2", "北京银行估值敏感性", "ROE 与股权成本为模型的权威可编辑输入；黄色单元格可调整");
  section(ws, "A4:D4", "核心假设");
  ws.getRange("A5:B9").values = [
    ["归一化可持续 ROE", 0.085],
    ["股权成本 Ke", 0.115],
    ["长期增长率 g", 0.025],
    ["归一化 EPS（元）", 1.20],
    ["基础股利支付率", 0.32],
  ];
  ws.getRange("C5:D9").values = [
    ["口径", "分析假设"],
    ["口径", "分析假设"],
    ["口径", "分析假设"],
    ["口径", "2026H1 年化后审慎下调"],
    ["口径", "参考历史与资本约束"],
  ];
  inputStyle(ws, "B5:B9");
  fmt(ws, "B5:B7", "0.0%"); fmt(ws, "B8", "0.00"); fmt(ws, "B9", "0.0%");
  header(ws, "A11:D11");
  ws.getRange("A11:D11").values = [["情景", "悲观", "基准", "乐观"]];
  ws.getRange("A12:A19").values = [["净息差"],["营收增速"],["信用成本"],["归一化 ROE"],["Ke"],["长期增长率"],["支付率"],["目标股息率"]];
  ws.getRange("B12:D19").values = [
    [0.0115,0.0126,0.0135],[-0.02,0.04,0.08],[0.0110,0.0089,0.0070],[0.07,0.085,0.10],[0.125,0.115,0.105],[0.015,0.025,0.03],[0.28,0.32,0.36],[0.065,0.055,0.05],
  ];
  inputStyle(ws, "B12:D19"); fmt(ws, "B12:D19", "0.0%");
  bodyTable(ws, "A12:D19");
  section(ws, "A22:E22", "经营情景估值");
  ws.getRange("A23:E23").values = [["指标", "悲观", "基准", "乐观", "说明"]]; header(ws, "A23:E23");
  ws.getRange("A24:A28").values = [["可持续 EPS（元）"],["合理 PB（x）"],["PB–ROE 价值（元）"],["股息率反推价值（元）"],["相对当前价安全边际"]];
  ws.getRange("B24:D24").values = [[1.05,1.20,1.30]];
  ws.getRange("B25:D25").formulas = [["=(B15-B17)/(B16-B17)","=(C15-C17)/(C16-C17)","=(D15-D17)/(D16-D17)"]];
  ws.getRange("B26:D26").formulas = [["=B25*'估值系统'!$B$8*(1-'估值系统'!$B$12)","=C25*'估值系统'!$B$8*(1-'估值系统'!$B$12)","=D25*'估值系统'!$B$8*(1-'估值系统'!$B$12)"]];
  ws.getRange("B27:D27").formulas = [["=B24*B18/B19","=C24*C18/C19","=D24*D18/D19"]];
  ws.getRange("B28:D28").formulas = [["=1-'估值系统'!$B$7/AVERAGE(B26:B27)","=1-'估值系统'!$B$7/AVERAGE(C26:C27)","=1-'估值系统'!$B$7/AVERAGE(D26:D27)"]];
  ws.getRange("E24:E28").values = [["归一化，不是盈利预测"],["稳定期公式"],["含模型折价"],["DPS/目标收益率"],["正数表示折价"]];
  fmt(ws, "B24:D24", "0.00"); fmt(ws, "B25:D25", "0.00x"); fmt(ws, "B26:D27", "0.00"); fmt(ws, "B28:D28", "0.0%");
  bodyTable(ws, "A24:E28");
  ws.getRange("B24:D28").format.fill = C.paleBlue;
  col(ws,"A",24); col(ws,"B",13); col(ws,"C",13); col(ws,"D",13); col(ws,"E",28); for (const x of ["F","G","H","I","J","K","L","M"]) col(ws,x,12);
  setBase(ws, "A1:M65");
  rowHeight(ws, 12, 19, 24); rowHeight(ws, 24, 28, 24);
}

// 财务十年：先写底稿，为估值历史倍数提供公式来源。
{
  const ws = sheet("财务十年");
  ws.showGridLines = false;
  ws.tabColor = "#A5A5A5";
  title(ws, "A2:S2", "北京银行财务十年", "金额单位：亿元；2026H1 为半年度数据，ROE/ROA 为公司披露年化口径");
  const hdr = ["期间","营业收入","归母净利润","EPS","BPS","ROE","ROA","净息差","不良率","拨备覆盖率","CET1","成本收入比","总资产","贷款本金","存款本金","DPS","期末/当前价","PB","PE"];
  ws.getRange("A4:S4").values = [hdr]; header(ws, "A4:S4");
  ws.getRange("A5:Q15").values = history;
  for (let r=5;r<=15;r++) {
    ws.getRange(`R${r}`).formulas = [[`=Q${r}/E${r}`]];
    if (r<15) ws.getRange(`S${r}`).formulas = [[`=Q${r}/D${r}`]];
  }
  ws.getRange("S15").values = [[5.68]];
  bodyTable(ws, "A5:S15");
  ws.getRange("A15:S15").format.fill = C.lightBlue;
  fmt(ws,"B5:C15","#,##0.00"); fmt(ws,"D5:E15","0.00"); fmt(ws,"F5:L15","0.00%");
  fmt(ws,"M5:O15","#,##0.00"); fmt(ws,"P5:Q15","0.000"); fmt(ws,"R5:S15","0.00x");
  section(ws, "A17:I17", "盈利与规模趋势");
  section(ws, "J17:S17", "收益率与息差趋势");
  addChart(ws, "line", ws.getRange("A4:C15"), ["A18","I34"], "营业收入与归母净利润（亿元）", "#,##0");
  addChart(ws, "line", [ws.getRange("A4:A15"),ws.getRange("F4:F15"),ws.getRange("H4:H15")], ["J18","S34"], "ROE 与净息差", "0.0%");
  ws.getRange("A36:S37").values = [["口径说明","2016—2025 为年度数据；2024 起保险合同准则导致比较数据有重述，采用最新披露口径。2026H1 不与全年金额直接相加或同比。","","","","","","","","","","","","","","","","",""],["历史估值用途","历史 PB/PE 主锚使用 2020—2025 六个年末快照，避免把更早股本变动直接混入中枢。","","","","","","","","","","","","","","","","",""]];
  ws.mergeCells("B36:S36"); ws.mergeCells("B37:S37");
  ws.getRange("A36:A37").format.fill = C.gray; ws.getRange("B36:S37").format.fill = C.paleBlue;
  for (const x of ["A"]) col(ws,x,12); for (const x of ["B","C","M","N","O"]) col(ws,x,14); for (const x of ["D","E","F","G","H","I","J","K","L","P","Q","R","S"]) col(ws,x,11);
  setBase(ws,"A1:S40"); rowHeight(ws,5,15,22); rowHeight(ws,36,37,32);
  ws.freezePanes.freezeRows(4); ws.freezePanes.freezeColumns(1);
}

// 同业比较。
{
  const ws = sheet("同业比较");
  ws.showGridLines = false;
  ws.tabColor = "#A5A5A5";
  title(ws, "A2:M2", "北京银行同业比较", "市场快照：2026-10-14 11:55；财务数据：2026H1；ROE 为半年值简单年化");
  const hdr=["银行","代码","股价","PE TTM","PB","ROE(年化)","净息差","不良率","拨备覆盖率","CET1","营收增速","净利增速","BPS"];
  ws.getRange("A4:M4").values=[hdr]; header(ws,"A4:M4");
  ws.getRange("A5:M11").values=peers; bodyTable(ws,"A5:M11");
  ws.getRange("A5:M5").format.fill=C.lightBlue;
  fmt(ws,"C5:C11","0.00"); fmt(ws,"D5:E11","0.00x"); fmt(ws,"F5:L11","0.00%"); fmt(ws,"M5:M11","0.00");
  ws.getRange("A13:M13").values=[["同业中位数（不含北京银行）","","","","","","","","","","","",""]];
  for (const colLetter of ["C","D","E","F","G","H","I","J","K","L","M"]) ws.getRange(`${colLetter}13`).formulas=[[`=MEDIAN(${colLetter}6:${colLetter}11)`]];
  ws.getRange("A13:M13").format={fill:C.gray,font:{name:FONT,size:10,bold:true,color:C.text},horizontalAlignment:"center",verticalAlignment:"center",wrapText:true,borders:{preset:"outside",style:"thin",color:C.rule}};
  fmt(ws,"C13:C13","0.00"); fmt(ws,"D13:E13","0.00x"); fmt(ws,"F13:L13","0.00%"); fmt(ws,"M13:M13","0.00");
  section(ws,"A15:F15","同业 ROE 调整 PB");
  ws.getRange("A16:B21").values=[["同业 PB 中位数",null],["北京银行 ROE",null],["同业 ROE 中位数",null],["ROE 弹性 β",0.80],["质量与资本折价",0.15],["目标 PB",null]];
  ws.getRange("B16").formulas=[["=E13"]]; ws.getRange("B17").formulas=[["=F5"]]; ws.getRange("B18").formulas=[["=F13"]];
  ws.getRange("B21").formulas=[["=B16*(B17/B18)^B19*(1-B20)"]];
  ws.getRange("D16:E21").values=[["计算说明",""],["可比组","城商行同业"],["β","ROE 差异向 PB 传导"],["额外折价","北京银行 CET1 较低且资产质量弱于优质同业"],["目标每股价值",null],["结果口径","目标 PB × 北京银行 BPS"]];
  ws.mergeCells("E16:F16"); ws.mergeCells("E17:F17"); ws.mergeCells("E18:F18"); ws.mergeCells("E19:F19"); ws.mergeCells("E20:F20"); ws.mergeCells("E21:F21");
  ws.getRange("E20").formulas=[["=B21*M5"]];
  inputStyle(ws,"B19:B20"); linkedStyle(ws,"B16:B18");
  fmt(ws,"B16:B16","0.00x"); fmt(ws,"B17:B18","0.00%"); fmt(ws,"B19","0.00"); fmt(ws,"B20","0.0%"); fmt(ws,"B21","0.00x"); fmt(ws,"E20","0.00");
  bodyTable(ws,"A16:B21"); bodyTable(ws,"D16:F21");
  section(ws,"H15:M15","当前 PB 对比");
  addChart(ws,"bar",[ws.getRange("A4:A11"),ws.getRange("E4:E11")],["H16","M31"],"PB 对比（x）","0.00x");
  ws.getRange("A24:F27").values=[["结论","北京银行 PB 低于同业中位数，但 ROE、CET1 和不良率也弱于多数高质量城商行。折价并非全是误定价。","","","",""],["模型使用","以 β=0.8 调整 ROE 差异，再追加 15% 质量与资本折价，结果进入组合估值。","","","",""],["局限","市场数据来自同一时点第三方快照；各行会计和业务结构仍有差异。","","","",""],["监控","若北京银行 ROE 提升且 CET1 保持 8.8%以上，额外折价可下调；反之应上调。","","","","" ]];
  for (let r=24;r<=27;r++) ws.mergeCells(`B${r}:F${r}`);
  ws.getRange("A24:A27").format.fill=C.gray; ws.getRange("B24:F27").format.fill=C.paleBlue;
  col(ws,"A",15); col(ws,"B",14); for(const x of ["C","D","E","F","G","H","I","J","K","L","M"]) col(ws,x,12);
  setBase(ws,"A1:M33"); rowHeight(ws,5,13,22); rowHeight(ws,24,27,32); ws.freezePanes.freezeRows(4);
}

// 股息估值与 DDM。
{
  const ws=sheet("股息估值");
  ws.showGridLines=false; ws.tabColor=C.blue2;
  title(ws,"A2:N2","北京银行股息估值","区分已实施年度股息、2026H1 拟派中期股息与可持续情景股息");
  section(ws,"A4:F4","历史分红");
  ws.getRange("A5:F5").values=[["年度/期间","EPS","DPS","支付率","当前价静态收益率","状态"]]; header(ws,"A5:F5");
  const divRows=history.map(r=>[r[0],r[3],r[15],null,null,r[0]==="2026H1"?"董事会预案":"已实施"]);
  ws.getRange("A6:F16").values=divRows;
  for(let r=6;r<=16;r++) { ws.getRange(`D${r}`).formulas=[[`=C${r}/B${r}`]]; ws.getRange(`E${r}`).formulas=[[`=C${r}/'估值系统'!$B$7`]]; }
  bodyTable(ws,"A6:F16"); ws.getRange("A16:F16").format.fill=C.lightAmber;
  fmt(ws,"B6:C16","0.000"); fmt(ws,"D6:E16","0.0%");
  section(ws,"H4:N4","股息情景与收益率反推");
  ws.getRange("H5:N5").values=[["情景","归一化 EPS","支付率","可持续 DPS","当前股息率","目标股息率","反推价格"]]; header(ws,"H5:N5");
  ws.getRange("H6:H8").values=[["保守"],["基准"],["条件上限"]];
  ws.getRange("I6:K8").values=[[1.05,0.28,null],[1.20,0.32,null],[1.30,0.36,null]];
  ws.getRange("M6:M8").values=[[0.06],[0.055],[0.05]];
  for(let r=6;r<=8;r++) { ws.getRange(`K${r}`).formulas=[[`=I${r}*J${r}`]]; ws.getRange(`L${r}`).formulas=[[`=K${r}/'估值系统'!$B$7`]]; ws.getRange(`N${r}`).formulas=[[`=K${r}/M${r}`]]; }
  inputStyle(ws,"I6:J8"); inputStyle(ws,"M6:M8"); bodyTable(ws,"H6:N8");
  fmt(ws,"I6:I8","0.00"); fmt(ws,"J6:J8","0.0%"); fmt(ws,"K6:K8","0.000"); fmt(ws,"L6:M8","0.0%"); fmt(ws,"N6:N8","0.00");
  ws.getRange("H10:J14").values=[["当前价",null,"元"],["2025 年度 DPS",0.278,"已实施"],["2026H1 DPS",0.130,"预案，未实施"],["已实施静态股息率",null,"只含最近完整年度"],["年度+中期预案合计收益率",null,"并非已实现 LTM"]];
  ws.getRange("I10").formulas=[["='估值系统'!$B$7"]]; ws.getRange("I13").formulas=[["=I11/I10"]]; ws.getRange("I14").formulas=[["=(I11+I12)/I10"]];
  fmt(ws,"I10:I12","0.000"); fmt(ws,"I13:I14","0.0%"); bodyTable(ws,"H10:J14");
  section(ws,"A19:I19","两阶段股利折现模型（DDM）");
  ws.getRange("A20:I20").values=[["年份","期初 EPS","EPS 增速","期末 EPS","支付率","DPS","折现因子","DPS 现值","说明"]]; header(ws,"A20:I20");
  ws.getRange("A21:A25").values=[[1],[2],[3],[4],[5]];
  ws.getRange("C21:C25").values=[[0.05],[0.045],[0.04],[0.035],[0.03]];
  ws.getRange("E21:E25").values=[[0.30],[0.31],[0.32],[0.33],[0.35]];
  ws.getRange("I21:I25").values=[["盈利修复"],["修复放缓"],["接近稳态"],["资本约束仍在"],["稳态过渡"]];
  ws.getRange("B21").formulas=[["='估值敏感性'!$B$8"]]; ws.getRange("B22:B25").formulas=[["=D21"],["=D22"],["=D23"],["=D24"]];
  for(let r=21;r<=25;r++) { ws.getRange(`D${r}`).formulas=[[`=B${r}*(1+C${r})`]]; ws.getRange(`F${r}`).formulas=[[`=D${r}*E${r}`]]; ws.getRange(`G${r}`).formulas=[[`=1/(1+'估值敏感性'!$B$6)^A${r}`]]; ws.getRange(`H${r}`).formulas=[[`=F${r}*G${r}`]]; }
  bodyTable(ws,"A21:I25"); inputStyle(ws,"C21:C25"); inputStyle(ws,"E21:E25"); linkedStyle(ws,"B21:B21");
  fmt(ws,"B21:B25","0.000"); fmt(ws,"C21:C25","0.0%"); fmt(ws,"D21:D25","0.000"); fmt(ws,"E21:E25","0.0%"); fmt(ws,"F21:H25","0.000");
  ws.getRange("A27:B33").values=[["长期增长率",null],["终值支付率",0.38],["第6年 DPS",null],["终值",null],["终值现值",null],["前5年 DPS 现值",null],["DDM 每股价值",null]];
  ws.getRange("B27").formulas=[["='估值敏感性'!$B$7"]]; ws.getRange("B29").formulas=[["=D25*(1+B27)*B28"]];
  ws.getRange("B30").formulas=[["=B29/('估值敏感性'!$B$6-B27)"]]; ws.getRange("B31").formulas=[["=B30/(1+'估值敏感性'!$B$6)^5"]];
  ws.getRange("B32").formulas=[["=SUM(H21:H25)"]]; ws.getRange("B33").formulas=[["=B31+B32"]];
  inputStyle(ws,"B28"); linkedStyle(ws,"B27"); fmt(ws,"B27:B28","0.0%"); fmt(ws,"B29:B33","0.00");
  ws.getRange("A33:B33").format={fill:C.lightGreen,font:{name:FONT,size:11,bold:true,color:C.text},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"medium",color:C.green}};
  section(ws,"K19:N19","资本约束");
  ws.getRange("K20:N25").values=[["事实","CET1 8.91%，较年初回升 54bp，但仍低于多数可比城商行。","",""],["事实","2026H1 已发行/计入其他一级资本，普通股分红仍要服从核心一级资本内生积累。","",""],["判断","基准支付率 32%；36% 仅在 CET1 不低于 8.8%、风险加权资产温和增长、资产质量不恶化时成立。","",""],["风险","信用成本 0.89%，同比上升；若继续走高，分红提升空间受限。","",""],["监控","CET1、RWA 增速、不良生成、核销与拨备覆盖率。","",""],["结论","高股息有支撑，但预案股息不能与已实施股息混为一谈。","",""]];
  for(let r=20;r<=25;r++) ws.mergeCells(`L${r}:N${r}`);
  ws.getRange("K20:K25").format.fill=C.gray; ws.getRange("L20:N25").format.fill=C.paleBlue;
  addChart(ws,"line",[ws.getRange("A5:A16"),ws.getRange("C5:C16")],["K27","N41"],"每股现金股息（元）","0.00");
  for(const x of ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]) col(ws,x,x==="I"||x==="L"?16:12);
  setBase(ws,"A1:N43"); rowHeight(ws,6,16,22); rowHeight(ws,20,25,24); rowHeight(ws,20,25,30); ws.freezePanes.freezeRows(5);
}

// 估值系统。
{
  const ws=sheet("估值系统");
  ws.showGridLines=false; ws.tabColor=C.blue;
  title(ws,"A2:J2","北京银行多模型估值系统","价格为 2026-10-14 11:55 盘中快照；经营数据截至 2026-06-30");
  section(ws,"A4:D4","关键输入");
  ws.getRange("A5:B12").values=[["公司","北京银行"],["代码","601169.SH"],["当前价（元）",5.62],["BPS（元）",13.48],["归一化 EPS（元）",null],["归一化 ROE",null],["股权成本 Ke",null],["PB–ROE 模型折价",0.05]];
  ws.getRange("D5:E12").values=[["经营数据截至",new Date("2026-06-30")],["股价快照",new Date("2026-10-14T11:55:55+08:00")],["长期增长率",null],["基础支付率",null],["同业 β",0.80],["同业额外折价",0.15],["历史区间", "2020—2025 年末"],["报告制作日",new Date("2026-10-14")]];
  ws.getRange("B9").formulas=[["='估值敏感性'!$B$8"]]; ws.getRange("B10").formulas=[["='估值敏感性'!$B$5"]]; ws.getRange("B11").formulas=[["='估值敏感性'!$B$6"]];
  ws.getRange("E7").formulas=[["='估值敏感性'!$B$7"]]; ws.getRange("E8").formulas=[["='估值敏感性'!$B$9"]];
  inputStyle(ws,"B7:B8"); inputStyle(ws,"B12"); inputStyle(ws,"E9:E10");
  linkedStyle(ws,"B9:B11"); linkedStyle(ws,"E7:E8");
  fmt(ws,"B7:B9","0.00"); fmt(ws,"B10:B12","0.0%"); fmt(ws,"E5:E6","yyyy-mm-dd"); fmt(ws,"E7:E8","0.0%"); fmt(ws,"E9","0.00"); fmt(ws,"E10","0.0%"); fmt(ws,"E12","yyyy-mm-dd");
  bodyTable(ws,"A5:B12"); bodyTable(ws,"D5:E12");
  section(ws,"A15:J15","六种主估值方法");
  ws.getRange("A16:J16").values=[["方法","关键输入","每股价值","权重","加权贡献","可靠性","主要限制","模型组","当前价折价","是否主锚"]]; header(ws,"A16:J16");
  ws.getRange("A17:A22").values=[["剩余收益模型 RIM"],["PB–ROE 合理倍数"],["历史 PB"],["历史 PE"],["同业 ROE 调整 PB"],["两阶段 DDM"]];
  ws.getRange("B17:B22").values=[["5年 ROE 路径、Ke、终值"],["ROE、Ke、g、模型折价"],["2020—2025 年末 PB 中位数"],["2020—2025 年末 PE 中位数×归一化EPS"],["同业 PB×ROE 弹性×额外折价"],["5年股息+稳定增长终值"]];
  ws.getRange("D17:D22").values=[[0.15],[0.15],[0.10],[0.10],[0.20],[0.30]];
  ws.getRange("F17:F22").values=[["中"],["中"],["中低"],["中低"],["中"],["中高"]];
  ws.getRange("G17:G22").values=[["终值受长期 ROE 影响"],["稳定期公式对 Ke-g 敏感"],["历史 ROE 下移会压低可比性"],["2025 EPS 受大额减值扰动"],["同业结构和资本质量不同"],["对支付率与 Ke 最敏感"]];
  ws.getRange("H17:H22").values=[["ROE内生"],["ROE内生"],["历史倍数"],["历史倍数"],["同业比较"],["分红模型"]];
  ws.getRange("J17:J22").values=[["是"],["是"],["否"],["否"],["是"],["是"]];
  // RIM 在下方明细计算后回链。
  ws.getRange("C17").formulas=[["=I34"]];
  ws.getRange("C18").formulas=[["=((B10-E7)/(B11-E7))*B8*(1-B12)"]];
  ws.getRange("C19").formulas=[["=MEDIAN('财务十年'!R9:R14)*B8"]];
  ws.getRange("C20").formulas=[["=MEDIAN('财务十年'!S9:S14)*B9"]];
  ws.getRange("C21").formulas=[["='同业比较'!$E$20"]];
  ws.getRange("C22").formulas=[["='股息估值'!$B$33"]];
  for(let r=17;r<=22;r++){ws.getRange(`E${r}`).formulas=[[`=C${r}*D${r}`]];ws.getRange(`I${r}`).formulas=[[`=1-$B$7/C${r}`]];}
  bodyTable(ws,"A17:J22"); fmt(ws,"C17:C22","0.00"); fmt(ws,"D17:D22","0.0%"); fmt(ws,"E17:E22","0.00"); fmt(ws,"I17:I22","0.0%");
  ws.getRange("A24:E28").values=[["组合估值",null,"","", ""],["权重合计",null,"","", ""],["修正组合中枢",null,"元","", ""],["组合安全边际",null,"","", ""],["保守安全边际",null,"相对 DDM","", ""]];
  ws.getRange("B25").formulas=[["=SUM(D17:D22)"]]; ws.getRange("B26").formulas=[["=SUM(E17:E22)"]]; ws.getRange("B27").formulas=[["=1-B7/B26"]]; ws.getRange("B28").formulas=[["=1-B7/C22"]];
  ws.mergeCells("B24:E24"); ws.getRange("B24:E24").values=[["历史倍数权重仅 20%；DDM 权重 30%，反映资本与分红约束"]];
  ws.getRange("A24:A28").format.fill=C.gray; ws.getRange("B24:E28").format.fill=C.paleBlue;
  ws.getRange("A26:B28").format.font={name:FONT,size:11,bold:true,color:C.text};
  fmt(ws,"B25","0.0%"); fmt(ws,"B26","0.00"); fmt(ws,"B27:B28","0.0%");
  section(ws,"A31:I31","剩余收益模型明细");
  ws.getRange("A32:I32").values=[["年份","期初 BPS","ROE","EPS","支付率","DPS","期末 BPS","剩余收益","现值"]]; header(ws,"A32:I32");
  ws.getRange("A33:A37").values=[[1],[2],[3],[4],[5]];
  ws.getRange("C33:C37").formulas=[["='估值敏感性'!$B$5+1.0%"],["='估值敏感性'!$B$5+0.7%"],["='估值敏感性'!$B$5+0.4%"],["='估值敏感性'!$B$5+0.2%"],["='估值敏感性'!$B$5"]];
  ws.getRange("E33:E37").values=[[0.30],[0.31],[0.32],[0.33],[0.35]];
  ws.getRange("B33").formulas=[["=$B$8"]]; ws.getRange("B34:B37").formulas=[["=G33"],["=G34"],["=G35"],["=G36"]];
  for(let r=33;r<=37;r++){ws.getRange(`D${r}`).formulas=[[`=B${r}*C${r}`]];ws.getRange(`F${r}`).formulas=[[`=D${r}*E${r}`]];ws.getRange(`G${r}`).formulas=[[`=B${r}+D${r}-F${r}`]];ws.getRange(`H${r}`).formulas=[[`=(C${r}-$B$11)*B${r}`]];ws.getRange(`I${r}`).formulas=[[`=H${r}/(1+$B$11)^A${r}`]];}
  bodyTable(ws,"A33:I37"); inputStyle(ws,"E33:E37"); linkedStyle(ws,"C33:C37");
  fmt(ws,"B33:B37","0.00"); fmt(ws,"C33:C37","0.0%"); fmt(ws,"D33:D37","0.00"); fmt(ws,"E33:E37","0.0%"); fmt(ws,"F33:I37","0.00");
  ws.getRange("H39:I42").values=[["终值现值",null],["残余收益现值合计",null],["期初 BPS",null],["RIM 每股价值",null]];
  ws.getRange("I39").formulas=[["=((C37-$B$11)*G37)/($B$11-$E$7)/(1+$B$11)^5"]];
  ws.getRange("I40").formulas=[["=SUM(I33:I37)"]]; ws.getRange("I41").formulas=[["=$B$8"]]; ws.getRange("I42").formulas=[["=I39+I40+I41"]];
  // C17 的真实 RIM 输出使用 I42；I34 为普通明细单元格，不作为主结果。
  ws.getRange("C17").formulas=[["=I42"]];
  ws.getRange("H42:I42").format={fill:C.lightGreen,font:{name:FONT,size:11,bold:true,color:C.text},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"medium",color:C.green}};
  fmt(ws,"I39:I42","0.00");
  ws.getRange("A44:J47").values=[["结论","当前价低于组合中枢，但高于保守 DDM；估值有一定折价，却不是无条件高安全边际。","","","","","","","",""] ,["解释","2026H1 盈利恢复、费用下降和负债成本改善支持 ROE 修复；信用成本、迁徙率和较低 CET1 限制估值上沿。","","","","","","","",""] ,["估值区间","以 DDM 防守价值至修正组合中枢为主区间；历史高估值修复仅作为条件性上行。","","","","","","","",""] ,["失效条件","NIM 再降、信用成本持续高于 1%、CET1 低于 8.5%、不良/关注/逾期同步恶化。","","","","","","","",""]];
  for(let r=44;r<=47;r++) ws.mergeCells(`B${r}:J${r}`);
  ws.getRange("A44:A47").format.fill=C.gray; ws.getRange("B44:J47").format.fill=C.paleBlue;
  col(ws,"A",18); col(ws,"B",22); for(const x of ["C","D","E","F","H","I","J"]) col(ws,x,13); col(ws,"G",26);
  setBase(ws,"A1:J49"); rowHeight(ws,17,22,30); rowHeight(ws,44,47,34); ws.freezePanes.freezeRows(16);
}

// 原生 What-If Data Tables：引用估值系统的三个输出。
{
  const ws=sheet("估值敏感性");
  const roeVals=[0.06,0.07,0.08,0.09,0.10,0.105];
  const keVals=[0.095,0.105,0.115];
  const blocks=[
    {start:"G4",title:"RIM：ROE × Ke",formula:"='估值系统'!$C$17"},
    {start:"G14",title:"PB–ROE：ROE × Ke",formula:"='估值系统'!$C$18"},
    {start:"G24",title:"组合中枢：ROE × Ke",formula:"='估值系统'!$B$26"},
  ];
  function cell(colIdx,row){ const letters=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P"]; return `${letters[colIdx]}${row}`; }
  for(const b of blocks){
    const col0=b.start.charCodeAt(0)-65; const row0=Number(b.start.slice(1));
    section(ws,`${cell(col0,row0)}:${cell(col0+4,row0)}`,b.title);
    const tl=cell(col0,row0+2); ws.getRange(tl).formulas=[[b.formula]]; ws.getRange(tl).format.numberFormat=";;;";
    const top=keVals.map(v=>v); ws.getRange(`${cell(col0+1,row0+2)}:${cell(col0+3,row0+2)}`).values=[top];
    ws.getRange(`${cell(col0,row0+3)}:${cell(col0,row0+8)}`).values=roeVals.map(v=>[v]);
    const full=`${cell(col0,row0+2)}:${cell(col0+3,row0+8)}`;
    ws.dataTables.add(full,{rowInput:"B6",columnInput:"B5"});
    ws.getRange(`${cell(col0+1,row0+2)}:${cell(col0+3,row0+2)}`).format.fill=C.gray;
    ws.getRange(`${cell(col0,row0+3)}:${cell(col0,row0+8)}`).format.fill=C.gray;
    ws.getRange(`${cell(col0+1,row0+3)}:${cell(col0+3,row0+8)}`).format.fill=C.paleBlue;
    fmt(ws,`${cell(col0+1,row0+2)}:${cell(col0+3,row0+2)}`,"0.0%");
    fmt(ws,`${cell(col0,row0+3)}:${cell(col0,row0+8)}`,"0.0%");
    fmt(ws,`${cell(col0+1,row0+3)}:${cell(col0+3,row0+8)}`,"0.00");
    bodyTable(ws,full);
    // Highlight ROE 8% and 9% rows.
    ws.getRange(`${cell(col0,row0+5)}:${cell(col0+3,row0+6)}`).format.font={name:FONT,size:10,bold:true,color:C.text};
  }
  ws.getRange("G34:M38").values=[["解读","ROE 8% 与 9% 为重点观察行；Ke 越高，RIM、PB–ROE 与组合中枢均下降。","","","","",""] ,["边界","所有测试 Ke 均高于长期增长率 2.5%，避免公式奇点。","","","","",""] ,["当前价",5.62,"元","","","",""] ,["基准组合中枢",null,"元","","","",""] ,["基准组合安全边际",null,"","","","",""]];
  ws.mergeCells("H34:M34"); ws.mergeCells("H35:M35");
  ws.getRange("H37").formulas=[["='估值系统'!$B$26"]]; ws.getRange("H38").formulas=[["='估值系统'!$B$27"]];
  fmt(ws,"H36:H37","0.00"); fmt(ws,"H38","0.0%");
  ws.getRange("G34:G38").format.fill=C.gray; ws.getRange("H34:M38").format.fill=C.paleBlue;
}

// 资产质量。
{
  const ws=sheet("资产质量"); ws.showGridLines=false; ws.tabColor="#A5A5A5";
  title(ws,"A2:N2","北京银行资产质量、资本与重点敞口","经营数据截至 2026-06-30；金额单位：亿元");
  section(ws,"A4:E4","核心风险指标");
  ws.getRange("A5:E5").values=[["指标","2024A","2025A","2026H1","变化/判断"]]; header(ws,"A5:E5");
  ws.getRange("A6:A15").values=[["不良率"],["关注率"],["逾期率"],["90天以上逾期/不良"],["拨备覆盖率"],["拨贷比"],["信用成本"],["核心一级资本充足率"],["资本充足率"],["流动性覆盖率"]];
  ws.getRange("B6:D15").values=[[0.0131,0.0129,0.0130],[null,0.0161,0.0158],[null,0.0196,0.0196],[null,0.8404,0.8622],[2.0875,2.0021,1.9959],[0.0273,0.0258,0.0259],[0.0087,0.0075,0.0089],[0.0895,0.0837,0.0891],[0.1306,0.1288,0.1410],[1.3806,1.7099,1.8230]];
  ws.getRange("E6:E15").values=[["较年初 +1bp"],["较年初 -3bp"],["持平"],["较年初 +218bp"],["较年初 -62bp"],["较年初 +1bp"],["较2025全年 +14bp"],["较年初 +54bp"],["较年初 +122bp"],["流动性充足"]];
  bodyTable(ws,"A6:E15"); fmt(ws,"B6:D15","0.00%");
  section(ws,"G4:N4","贷款结构与重点敞口");
  ws.getRange("G5:N5").values=[["项目","2025A","2026H1","变动","占贷款比","风险含义","口径","备注"]]; header(ws,"G5:N5");
  ws.getRange("G6:N14").values=[
    ["公司贷款",16808.76,17120.67,0.0186,0.7128,"主体增长来源","本金","含一般贷款、贴现、福费廷"],
    ["个人贷款",7188.79,6899.90,-0.0402,0.2872,"零售收缩","本金","个人端需求与风险出清并存"],
    ["住房按揭",3301.89,3256.12,-0.0139,0.1356,"抵押类零售","本金","不等同于全部涉房敞口"],
    ["个人经营贷",1677.00,1566.55,-0.0659,0.0652,"下降较快","本金","需关注小微还款能力"],
    ["个人消费贷",2057.45,1943.93,-0.0552,0.0809,"下降","本金","收益较高但信用风险敏感"],
    ["信用卡",152.45,133.30,-0.1256,0.0055,"规模较小","本金","同比口径未披露"],
    ["房地产业贷款",1211.60,1114.71,-0.0800,0.0464,"对公口径下降","行业分类","不能代表承担信用风险涉房总敞口"],
    ["关注贷款",387.13,380.05,-0.0183,0.0158,"余额下降","五级分类","迁徙率升至 50.72%"],
    ["逾期贷款",470.48,470.95,0.0010,0.0196,"总额基本持平","本金逾期","90天以上偏离度上升"],
  ];
  bodyTable(ws,"G6:N14"); fmt(ws,"H6:I14","#,##0.00"); fmt(ws,"J6:K14","0.00%");
  section(ws,"A18:F18","不良、拨备与处置");
  ws.getRange("A19:F19").values=[["项目","2025A","2026H1","变化","单位","解读"]]; header(ws,"A19:F19");
  ws.getRange("A20:F27").values=[
    ["正常类贷款",23300.75,23328.94,28.19,"亿元","贷款总量近乎不变"],
    ["关注类贷款",387.13,380.05,-7.08,"亿元","余额下降"],
    ["不良贷款",309.67,311.58,1.91,"亿元","余额小幅上升"],
    ["贷款减值准备期初",null,620.00,null,"亿元","本行口径"],
    ["本期计提",null,106.92,null,"亿元","信用成本上行"],
    ["收回已核销",null,16.11,null,"亿元","补充拨备"],
    ["本期核销及转出",null,-119.28,null,"亿元","处置规模大于不良净增"],
    ["贷款减值准备期末",null,621.87,null,"亿元","本行口径"],
  ];
  bodyTable(ws,"A20:F27"); fmt(ws,"B20:D27","#,##0.00;(#,##0.00);-");
  section(ws,"H18:N18","风险诊断");
  ws.getRange("H19:N25").values=[["事实","2026H1 信用减值损失 100.05 亿元，同比增加 11.49%。","","","","",""] ,["事实","关注率下降，但关注类迁徙率由 28.69% 升至 50.72%。","","","","",""] ,["事实","核销及转出 119.28 亿元，不良余额仅增加 1.91 亿元。","","","","",""] ,["判断","点时不良率稳定不能单独证明风险已彻底改善；处置与核销贡献较大。","","","","",""] ,["判断","房地产业贷款占比 4.64%，但报告未完整拆分承担信用风险涉房业务总口径。","","","","",""] ,["资本","CET1 回升至 8.91%，改善明显，但仍需约束增长和支付率假设。","","","","",""] ,["监控","信用成本>1%、关注率>1.7%、逾期率>2.1%、CET1<8.5% 为主要触发线。","","","","",""]];
  for(let r=19;r<=25;r++) ws.mergeCells(`I${r}:N${r}`);
  ws.getRange("H19:H25").format.fill=C.gray; ws.getRange("I19:N25").format.fill=C.paleBlue;
  addChart(ws,"line",[sheet("财务十年").getRange("A4:A15"),sheet("财务十年").getRange("I4:I15")],["A30","F44"],"不良率趋势","0.00%");
  addChart(ws,"line",[sheet("财务十年").getRange("A4:A15"),sheet("财务十年").getRange("J4:J15"),sheet("财务十年").getRange("K4:K15")],["H30","N44"],"拨备覆盖率与 CET1","0.0%");
  for(const x of ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]) col(ws,x,x==="F"||x==="L"||x==="N"?20:12);
  setBase(ws,"A1:N46"); rowHeight(ws,6,15,24); rowHeight(ws,19,27,28); ws.freezePanes.freezeRows(5);
}

// 巴菲特框架。
{
  const ws=sheet("巴菲特框架"); ws.showGridLines=false; ws.tabColor="#A5A5A5";
  title(ws,"A2:H2","北京银行长期质量框架","适用于银行的能力圈、负债优势、信贷文化、资本配置与价值陷阱检查");
  ws.getRange("A4:H4").values=[["维度","客观证据","判断","支持因素","反证/风险","监控指标","失效条件","结论"]]; header(ws,"A4:H4");
  const rows=[
    ["能力圈","扎根北京并覆盖京津冀、长三角等区域；北京贷款占 41.18%。","可理解","区域客户基础清晰","区域与大客户集中度","北京贷款占比、前十大客户","区域信用风险明显抬升","中性偏正面"],
    ["商业模式","利息净收入占营收 71.86%，存款占负债 65.07%。","较稳定","公司与政府客户基础","息差仍处下行区间","NIM、存款成本","NIM 持续低于 1.15%","中性"],
    ["存款成本优势","负债成本率 1.45%，同比下降 27bp；企业活期存款增长 8.02%。","改善","高成本负债压降","个人活期存款略降","活期占比、存款成本","存款成本重新上升","正面"],
    ["信贷文化","不良率 1.30%，拨备覆盖率 199.59%。","需验证","拨备仍接近 200%","迁徙率和信用成本上升，核销规模大","新生成不良、核销、迁徙率","关注与逾期同步恶化","谨慎"],
    ["治理诚信","定期披露较完整，2026 中报经审阅。","可接受","审计与监管披露","政府股东与关联授信需持续观察","关联交易、监管处罚","重大内控或合规事件","中性"],
    ["资本配置","CET1 8.91%，总资本充足率 14.10%；提出中期分红。","受约束","资本指标回升","核心一级资本低于优质同业","CET1、RWA、支付率","高增长与高分红同时出现","谨慎"],
    ["股东回报","2025 DPS 0.278 元；2026H1 拟派 0.13 元。","稳定性提升","连续分红并新增中期预案","预案未实施，盈利需覆盖","DPS、普通股口径支付率","资本下降而支付率上升","中性偏正面"],
    ["价值陷阱","当前 PB 约 0.42x，明显低于同业中位数。","不能排除","盈利修复可带来重估","ROE 低、资本薄、信用成本上行","ROE、CET1、信用成本","ROE 长期低于 8%","需持续验证"],
  ];
  ws.getRange("A5:H12").values=rows; bodyTable(ws,"A5:H12");
  ws.getRange("A5:A12").format.fill=C.gray; ws.getRange("H5:H12").format.fill=C.paleBlue;
  section(ws,"A15:H15","总体判断");
  ws.getRange("A16:H19").values=[["质量","北京银行具备区域资源、存款基础和较强风险抵补，但 ROE 与核心一级资本仍弱于高质量城商行。","","","","","",""] ,["价格","0.42x PB 提供估值缓冲；是否形成长期复利仍取决于 ROE 能否稳定在 8.5% 以上。","","","","","",""] ,["分红","股息吸引力提升，但中期预案未实施，且提高支付率不能脱离 CET1 与信用成本。","","","","","",""] ,["结论","属于“有折价、需验证”的银行股，而不是仅凭低 PB 就能确认的深度价值。","","","","","",""]];
  for(let r=16;r<=19;r++) ws.mergeCells(`B${r}:H${r}`);
  ws.getRange("A16:A19").format.fill=C.gray; ws.getRange("B16:H19").format.fill=C.paleBlue;
  for(const x of ["A","B","C","D","E","F","G","H"]) col(ws,x,x==="A"||x==="C"||x==="H"?16:24);
  setBase(ws,"A1:H21"); rowHeight(ws,5,12,56); rowHeight(ws,16,19,36); ws.freezePanes.freezeRows(4);
}

// 投资结论。
{
  const ws=sheet("投资结论"); ws.showGridLines=false; ws.tabColor=C.navy;
  title(ws,"A2:J2","北京银行投资研究结论","事实、分析假设与研究判断分色呈现；不构成个性化买卖建议");
  section(ws,"A4:J4","结论概览");
  ws.getRange("A5:B11").values=[["当前价",5.62],["合理价值下沿",null],["合理价值上沿",null],["组合中枢",null],["组合安全边际",null],["保守安全边际",null],["研究结论","有折价、需验证"]];
  ws.getRange("B6").formulas=[["='估值系统'!$C$22"]]; ws.getRange("B7").formulas=[["='估值系统'!$B$26"]]; ws.getRange("B8").formulas=[["='估值系统'!$B$26"]]; ws.getRange("B9").formulas=[["='估值系统'!$B$27"]]; ws.getRange("B10").formulas=[["='估值系统'!$B$28"]];
  fmt(ws,"B5:B8","0.00"); fmt(ws,"B9:B10","0.0%"); bodyTable(ws,"A5:B11");
  ws.getRange("A5:A11").format.fill=C.gray; ws.getRange("B5:B11").format.fill=C.lightGreen;
  ws.getRange("D5:J11").values=[
    ["类型","核心内容","证据/假设","影响","监控","触发线","结论"],
    ["事实","2026H1 营收和归母净利润分别增长 5.60% 和 5.63%。","中报","盈利恢复","2026Q3","增速转负","正面"],
    ["事实","PPOP 约 287.85 亿元，同比增长约 9.6%；但信用减值损失增至 100.05 亿元。","中报测算","经营改善与风险成本并存","信用成本","高于1%","中性"],
    ["事实","不良率 1.30%，关注率 1.58%，逾期率 1.96%，CET1 8.91%。","中报","资本和风险仍约束估值","不良/关注/CET1","同步恶化","谨慎"],
    ["假设","归一化 ROE 8.5%，Ke 11.5%，长期增长率 2.5%，支付率 32%。","可编辑模型","决定内生价值","敏感性页","Ke-g 收窄","基准"],
    ["判断","当前价低于组合中枢约 17.2%，但高于保守 DDM 约 7.1%。","模型","折价不等于深度安全边际","股息与资本","DDM低于价","中性偏正面"],
    ["判断","若 ROE 稳定在 9% 以上且 CET1 不低于 8.8%，价值区间可向上沿靠拢。","情景","需要经营兑现","ROE/CET1","连续两个报告期","条件性"],
  ];
  header(ws,"D5:J5"); bodyTable(ws,"D6:J11");
  ws.getRange("D6:J8").format.fill=C.paleBlue; ws.getRange("D9:J9").format.fill=C.lightAmber; ws.getRange("D10:J11").format.fill=C.lightGreen;
  section(ws,"A14:E14","三条核心结论"); section(ws,"G14:J14","三条核心风险",C.red);
  ws.getRange("A15:E17").values=[["1","盈利与费用端改善，NIM 降幅收窄，负债成本管理有效。","","",""],["2","低 PB 有折价，但 ROE 与资本水平解释了部分折价。","","",""] ,["3","主要价值来自分红与温和 ROE 修复，而非历史估值全面回归。","","",""]];
  for(let r=15;r<=17;r++) ws.mergeCells(`B${r}:E${r}`);
  ws.getRange("G15:J17").values=[["1","信用成本与迁徙率上升，核销掩盖点时不良净增。","",""],["2","CET1 较薄，高增长和高支付率不能同时假设。","",""],["3","NIM 仍处下行区间，个人贷款收缩，盈利修复可能反复。","",""]];
  for(let r=15;r<=17;r++) ws.mergeCells(`H${r}:J${r}`);
  ws.getRange("A15:E17").format.fill=C.lightGreen; ws.getRange("G15:J17").format.fill=C.lightRed;
  section(ws,"A20:J20","季度监控与估值动作");
  ws.getRange("A21:J21").values=[["指标","当前","改善条件","恶化条件","改善时含义","恶化时含义","数据频率","下一节点","来源","备注"]]; header(ws,"A21:J21");
  ws.getRange("A22:J27").values=[
    ["ROE",0.106,"≥9%可持续","<8%","上调内生估值","下调 PB–ROE/RIM","季度/年度","2026Q3", "定期报告","H1为年化"],
    ["净息差",0.0126,"止跌或回升","<1.15%","提高盈利确定性","下调 EPS/ROE","半年/年度","2026Q3辅助", "定期报告","季度未必披露"],
    ["信用成本",0.0089,"≤0.8%",">1.0%","风险成本正常化","下调盈利与分红","半年/年度","2026Q3辅助", "定期报告","H1年化"],
    ["不良率",0.0130,"≤1.30%",">1.40%","维持质量判断","提高折价","季度","2026Q3", "定期报告","结合关注/逾期"],
    ["CET1",0.0891,"≥8.8%","<8.5%","支持32%支付率","下调支付率","季度","2026Q3", "资本披露","集团口径"],
    ["拨备覆盖率",1.9959,"≥190%", "<180%","风险缓冲稳定","估值下沿下移","季度","2026Q3", "定期报告","结合核销"],
  ];
  bodyTable(ws,"A22:J27"); fmt(ws,"B22:D27","0.0%");
  ws.getRange("A29:J31").values=[["边界","2026 年三季报预约 2026-10-31 披露，本报告未纳入尚未公开的数据。","","","","","","","",""] ,["区间","主合理价值区间为防守 DDM 至修正组合中枢；条件性上行不并入主区间。","","","","","","","",""] ,["使用","修改黄色假设后，估值系统、一图流与敏感性结果联动。","","","","","","","",""]];
  for(let r=29;r<=31;r++) ws.mergeCells(`B${r}:J${r}`);
  ws.getRange("A29:A31").format.fill=C.gray; ws.getRange("B29:J31").format.fill=C.paleBlue;
  for(const x of ["A","B","C","D","E","F","G","H","I","J"]) col(ws,x,x==="B"||x==="E"||x==="F"?18:13);
  setBase(ws,"A1:J33"); rowHeight(ws,6,11,38); rowHeight(ws,15,17,34); rowHeight(ws,22,27,28); ws.freezePanes.freezeRows(5);
}

// 一图流（旧版布局保留在构建器内，便于追溯；不再执行）。
if(false){
  const ws=sheet("一图流"); ws.showGridLines=false; ws.tabColor=C.navy;
  title(ws,"A2:N2","北京银行一图流估值","601169.SH｜经营数据截至 2026-06-30｜股价 5.62 元，2026-10-14 11:55 盘中快照");
  const cards=[
    ["A5:B7","当前价","='估值系统'!$B$7","0.00"],
    ["C5:D7","合理区间下沿","='估值系统'!$C$22","0.00"],
    ["E5:F7","组合中枢","='估值系统'!$B$26","0.00"],
    ["G5:H7","组合安全边际","='估值系统'!$B$27","0.0%"],
    ["I5:J7","保守安全边际","='估值系统'!$B$28","0.0%"],
    ["K5:L7","当前 PB","='同业比较'!$E$5","0.00x"],
    ["M5:N7","静态股息率","='股息估值'!$I$13","0.0%"],
  ];
  for(const [addr,label,formula,numFmt] of cards){
    const [s,e]=addr.split(":"); const c1=s.match(/[A-Z]+/)[0], r1=Number(s.match(/\d+/)[0]), c2=e.match(/[A-Z]+/)[0], r2=Number(e.match(/\d+/)[0]);
    ws.mergeCells(`${c1}${r1}:${c2}${r1}`); ws.mergeCells(`${c1}${r1+1}:${c2}${r2}`);
    ws.getRange(`${c1}${r1}:${c2}${r1}`).values=[[label]]; ws.getRange(`${c1}${r1}:${c2}${r1}`).format={fill:C.navy,font:{name:FONT,size:9,bold:true,color:C.white},horizontalAlignment:"center",verticalAlignment:"center"};
    ws.getRange(`${c1}${r1+1}`).formulas=[[formula]]; ws.getRange(`${c1}${r1+1}:${c2}${r2}`).format={fill:C.paleBlue,font:{name:FONT,size:14,bold:true,color:C.navy},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.rule}};
    ws.getRange(`${c1}${r1+1}`).format.numberFormat=numFmt;
  }
  section(ws,"A10:D10","业务全貌"); section(ws,"E10:H10","盈利趋势"); section(ws,"I10:L10","风险与资本"); section(ws,"M10:N10","分红与估值");
  ws.getRange("A11:D16").values=[["定位","北京市属系统重要性城商行，综合经营平台。","",""] ,["区域","北京贷款占 41.18%，兼顾长三角与其他核心城市。","",""] ,["资产","公司贷款 71.28%，个人贷款 28.72%。","",""] ,["负债","存款占负债 65.07%，企业活期存款增长 8.02%。","",""] ,["优势","首都客户、科技金融与对公生态。","",""] ,["限制","区域/大客户集中，零售贷款下降 4.02%。","",""]];
  for(let r=11;r<=16;r++) ws.mergeCells(`B${r}:D${r}`);
  ws.getRange("E11:H16").values=[["营收增速",0.0560,"归母净利增速",0.0563],["PPOP增速",0.0959,"信用减值增速",0.1149],["年化 ROE",0.1060,"净息差",0.0126],["成本收入比",0.2347,"净利息收入增速",0.0634],["手续费净收入增速",0.0714,"个人贷款增速",-0.0402],["归一化 ROE",null,"归一化 EPS",null]];
  ws.getRange("F16").formulas=[["='估值敏感性'!$B$5"]]; ws.getRange("H16").formulas=[["='估值敏感性'!$B$8"]];
  fmt(ws,"F11:F16","0.0%"); fmt(ws,"H11:H15","0.0%"); fmt(ws,"H16","0.00"); linkedStyle(ws,"F16:H16");
  ws.getRange("I11:L16").values=[["不良率",0.0130,"关注率",0.0158],["逾期率",0.0196,"拨备覆盖率",1.9959],["信用成本",0.0089,"CET1",0.0891],["资本充足率",0.1410,"LCR",1.8230],["核销及转出",119.28,"亿元","处置规模大"],["房地产行业贷款",1114.71,"亿元","占贷款4.64%"]];
  fmt(ws,"J11:J14","0.00%"); fmt(ws,"L11:L14","0.00%"); fmt(ws,"J15:J16","#,##0.00");
  ws.getRange("M11:N16").values=[["2025 DPS",0.278],["2026H1 拟派",0.130],["静态股息率",null],["DDM",null],["组合中枢",null],["价值区间","5.25—6.79"]];
  ws.getRange("N13").formulas=[["='股息估值'!$I$13"]]; ws.getRange("N14").formulas=[["='估值系统'!$C$22"]]; ws.getRange("N15").formulas=[["='估值系统'!$B$26"]];
  fmt(ws,"N11:N12","0.000"); fmt(ws,"N13","0.0%"); fmt(ws,"N14:N15","0.00");
  for(const addr of ["A11:D16","E11:H16","I11:L16","M11:N16"]) bodyTable(ws,addr);
  ws.getRange("A11:A16").format.fill=C.gray; ws.getRange("E11:E16").format.fill=C.gray; ws.getRange("G11:G16").format.fill=C.gray; ws.getRange("I11:I16").format.fill=C.gray; ws.getRange("K11:K16").format.fill=C.gray; ws.getRange("M11:M16").format.fill=C.gray;
  section(ws,"A19:F19","核心结论"); section(ws,"H19:N19","核心风险",C.red);
  ws.getRange("A20:F22").values=[["1","2026H1 盈利恢复，费用率下降，PPOP 增长快于净利润。","","","",""] ,["2","当前价较组合中枢有约 17.2% 折价，但较保守 DDM 溢价约 7.1%。","","","",""] ,["3","估值改善依赖 ROE 稳在 8.5%以上、CET1 不低于 8.8%。","","","",""]];
  for(let r=20;r<=22;r++) ws.mergeCells(`B${r}:F${r}`);
  ws.getRange("H20:N22").values=[["1","信用成本与迁徙率上行，点时不良稳定受核销支撑。","","","","",""] ,["2","CET1 仍偏薄，限制资产扩张和支付率上限。","","","","",""] ,["3","NIM 仍下行，个人贷款收缩，修复持续性待三季报验证。","","","","",""]];
  for(let r=20;r<=22;r++) ws.mergeCells(`I${r}:N${r}`);
  ws.getRange("A20:F22").format.fill=C.lightGreen; ws.getRange("H20:N22").format.fill=C.lightRed;
  section(ws,"A25:H25","六法估值"); section(ws,"J25:N25","监控触发线");
  ws.getRange("A26:C32").values=[["方法","价值","权重"],["RIM",null,0.15],["PB–ROE",null,0.15],["历史 PB",null,0.10],["历史 PE",null,0.10],["同业调整 PB",null,0.20],["DDM",null,0.30]]; header(ws,"A26:C26");
  for(let r=27;r<=32;r++){ws.getRange(`B${r}`).formulas=[[`='估值系统'!C${r-10}`]];}
  bodyTable(ws,"A27:C32"); fmt(ws,"B27:B32","0.00"); fmt(ws,"C27:C32","0.0%");
  addChart(ws,"bar",[ws.getRange("A26:A32"),ws.getRange("B26:B32")],["E26","H39"],"每股价值（元）","0.00");
  ws.getRange("J26:N32").values=[["指标","改善","恶化","当前","节点"],["ROE","≥9%","<8%","10.6%","2026Q3"],["净息差","止跌","<1.15%","1.26%","中报/年报"],["信用成本","≤0.8%",">1.0%","0.89%","中报/年报"],["不良率","≤1.30%",">1.40%","1.30%","2026Q3"],["CET1","≥8.8%","<8.5%","8.91%","2026Q3"],["拨备覆盖率","≥190%","<180%","199.59%","2026Q3"]]; header(ws,"J26:N26"); bodyTable(ws,"J27:N32");
  ws.getRange("A41:N43").values=[["判断","当前估值提供一定缓冲，但保守分红价值没有留下明显安全垫；最关键的验证点是 2026Q3 的盈利延续、信用成本与资本。","","","","","","","","","","","",""] ,["数据边界","2026 年三季报预约 2026-10-31 披露，尚未公开；当前价为盘中快照，非收盘价。","","","","","","","","","","","",""] ,["使用提示","黄色单元格为可编辑假设。修改估值敏感性、股息估值和同业折价后，核心结果联动。","","","","","","","","","","","",""]];
  for(let r=41;r<=43;r++) ws.mergeCells(`B${r}:N${r}`);
  ws.getRange("A41:A43").format.fill=C.gray; ws.getRange("B41:N43").format.fill=C.paleBlue;
  for(const x of ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]) col(ws,x,12);
  setBase(ws,"A1:N45"); rowHeight(ws,11,16,28); rowHeight(ws,20,22,34); rowHeight(ws,41,43,34);
}

// 一图流（可读性优化版）。
{
  const ws=sheet("一图流"); ws.showGridLines=false; ws.tabColor=C.navy;
  title(ws,"A2:L2","北京银行一图流估值","601169.SH　经营数据截至 2026-06-30　股价快照 2026-10-14 11:55（盘中）");

  const cards=[
    ["A5:C5","A6:C8","当前价（元）","='估值系统'!$B$7","0.00",C.paleBlue,C.navy],
    ["D5:F5","D6:F8","合理价值区间（元）",`=TEXT('估值系统'!$C$22,"0.00")&" — "&TEXT('估值系统'!$B$26,"0.00")`,"@",C.paleBlue,C.navy],
    ["G5:I5","G6:I8","组合安全边际","='估值系统'!$B$27","0.0%",C.lightGreen,"#006100"],
    ["J5:L5","J6:L8","保守安全边际","='估值系统'!$B$28","0.0%",C.lightRed,C.red],
  ];
  for(const [labelRange,valueRange,label,formula,numFmt,fill,fontColor] of cards){
    ws.mergeCells(labelRange); ws.mergeCells(valueRange);
    ws.getRange(labelRange).values=[[label]];
    ws.getRange(labelRange).format={fill:C.navy,font:{name:FONT,size:11,bold:true,color:C.white},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.navy}};
    ws.getRange(valueRange.split(":")[0]).formulas=[[formula]];
    ws.getRange(valueRange).format={fill,font:{name:FONT,size:20,bold:true,color:fontColor},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.rule}};
    ws.getRange(valueRange.split(":")[0]).format.numberFormat=numFmt;
  }

  ws.mergeCells("A10:L11");
  ws.getRange("A10").formulas=[[`="有折价、需验证：当前价低于组合中枢 "&TEXT('估值系统'!$B$27,"0.0%")&"，但高于保守 DDM "&TEXT(-'估值系统'!$B$28,"0.0%")`]];
  ws.getRange("A10:L11").format={fill:C.lightAmber,font:{name:FONT,size:14,bold:true,color:C.text},horizontalAlignment:"center",verticalAlignment:"center",wrapText:true,borders:{preset:"outside",style:"medium",color:C.amber}};

  section(ws,"A13:L13","经营与风险指标（2026H1）");
  const metrics=[
    ["A14:B14","A15:B16","A17:B17","营收增速",0.0560,"0.0%","同比"],
    ["C14:D14","C15:D16","C17:D17","归母净利润增速",0.0563,"0.0%","同比"],
    ["E14:F14","E15:F16","E17:F17","年化 ROE",0.1060,"0.0%","公司披露口径"],
    ["G14:H14","G15:H16","G17:H17","净息差",0.0126,"0.00%","同比 -5bp"],
    ["I14:J14","I15:J16","I17:J17","不良率",0.0130,"0.00%","较年初 +1bp"],
    ["K14:L14","K15:L16","K17:L17","CET1",0.0891,"0.00%","较年初 +54bp"],
  ];
  for(const [labelRange,valueRange,noteRange,label,value,numFmt,note] of metrics){
    ws.mergeCells(labelRange); ws.mergeCells(valueRange); ws.mergeCells(noteRange);
    ws.getRange(labelRange).values=[[label]]; ws.getRange(valueRange.split(":")[0]).values=[[value]]; ws.getRange(noteRange).values=[[note]];
    ws.getRange(labelRange).format={fill:C.gray,font:{name:FONT,size:10,bold:true,color:C.text},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.rule}};
    ws.getRange(valueRange).format={fill:C.white,font:{name:FONT,size:16,bold:true,color:C.navy},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.rule}};
    ws.getRange(valueRange.split(":")[0]).format.numberFormat=numFmt;
    ws.getRange(noteRange).format={fill:C.paleBlue,font:{name:FONT,size:9,color:"#667085"},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.rule}};
  }

  section(ws,"A19:F19","支持估值的因素",C.green); section(ws,"G19:L19","需要继续验证",C.red);
  const support=[
    [20,21,"盈利","营收与归母净利润均增长约 5.6%，PPOP 增长 9.6%。"],
    [22,23,"负债","负债成本率降至 1.45%，企业活期存款增长 8.0%。"],
    [24,25,"估值","PB 0.42x，低于可比城商行中位数 0.86x。"],
  ];
  const verify=[
    [20,21,"资产质量","信用成本升至 0.89%，关注贷款迁徙率升至 50.72%。"],
    [22,23,"资本","CET1 为 8.91%，高增长与高支付率不能同时假设。"],
    [24,25,"盈利持续性","NIM 1.26%，个人贷款下降 4.0%，修复仍需后续财报验证。"],
  ];
  for(const [r1,r2,label,textValue] of support){
    ws.mergeCells(`A${r1}:A${r2}`); ws.mergeCells(`B${r1}:F${r2}`);
    ws.getRange(`A${r1}`).values=[[label]]; ws.getRange(`B${r1}`).values=[[textValue]];
    ws.getRange(`A${r1}:A${r2}`).format={fill:C.lightGreen,font:{name:FONT,size:11,bold:true,color:"#006100"},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:"#A9D18E"}};
    ws.getRange(`B${r1}:F${r2}`).format={fill:C.lightGreen,font:{name:FONT,size:11,color:C.text},horizontalAlignment:"left",verticalAlignment:"center",wrapText:true,borders:{preset:"outside",style:"thin",color:"#A9D18E"}};
  }
  for(const [r1,r2,label,textValue] of verify){
    ws.mergeCells(`G${r1}:G${r2}`); ws.mergeCells(`H${r1}:L${r2}`);
    ws.getRange(`G${r1}`).values=[[label]]; ws.getRange(`H${r1}`).values=[[textValue]];
    ws.getRange(`G${r1}:G${r2}`).format={fill:C.lightRed,font:{name:FONT,size:11,bold:true,color:C.red},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:"#F4B183"}};
    ws.getRange(`H${r1}:L${r2}`).format={fill:C.lightRed,font:{name:FONT,size:11,color:C.text},horizontalAlignment:"left",verticalAlignment:"center",wrapText:true,borders:{preset:"outside",style:"thin",color:"#F4B183"}};
  }

  section(ws,"A27:H27","六法估值（元/股）"); section(ws,"I27:L27","关键监控");
  ws.getRange("A28:C34").values=[["方法","价值","权重"],["RIM",null,0.15],["PB–ROE",null,0.15],["历史 PB",null,0.10],["历史 PE",null,0.10],["同业调整 PB",null,0.20],["DDM",null,0.30]]; header(ws,"A28:C28");
  for(let r=29;r<=34;r++) ws.getRange(`B${r}`).formulas=[[`='估值系统'!C${r-12}`]];
  bodyTable(ws,"A29:C34"); fmt(ws,"B29:B34","0.00"); fmt(ws,"C29:C34","0.0%");
  const valuationChart=addChart(ws,"bar",[ws.getRange("A28:A34"),ws.getRange("B28:B34")],["D28","H40"],"估值结果","0.00");
  valuationChart.hasLegend=false;
  ws.getRange("I28:L34").values=[["指标","当前","警戒线","下一节点"],["ROE","10.6%","<8%","2026Q3"],["净息差","1.26%","<1.15%","中报/年报"],["信用成本","0.89%",">1.0%","中报/年报"],["不良率","1.30%",">1.40%","2026Q3"],["CET1","8.91%","<8.5%","2026Q3"],["拨备覆盖率","199.59%","<180%","2026Q3"]];
  header(ws,"I28:L28"); bodyTable(ws,"I29:L34");

  ws.getRange("A42:L44").values=[
    ["判断","当前估值提供一定缓冲，但保守分红价值没有明显安全垫。重点验证盈利延续、信用成本与资本。","","","","","","","","","",""],
    ["数据边界","2026 年三季报预约 2026-10-31 披露，尚未公开。当前价为盘中快照，非收盘价。","","","","","","","","","",""],
    ["使用提示","黄色单元格为可编辑假设。修改假设后，估值系统、一图流与敏感性结果联动。","","","","","","","","","",""],
  ];
  for(let r=42;r<=44;r++) ws.mergeCells(`B${r}:L${r}`);
  ws.getRange("A42:A44").format={fill:C.gray,font:{name:FONT,size:10,bold:true,color:C.text},horizontalAlignment:"center",verticalAlignment:"center"};
  ws.getRange("B42:L44").format={fill:C.paleBlue,font:{name:FONT,size:10,color:C.text},horizontalAlignment:"left",verticalAlignment:"center",wrapText:true};

  for(const x of ["A","C","E","G","I","K"]) col(ws,x,11);
  for(const x of ["B","D","F","H","J","L"]) col(ws,x,15);
  setBase(ws,"A1:L45");
  rowHeight(ws,1,1,8); rowHeight(ws,2,2,30); rowHeight(ws,3,3,20); rowHeight(ws,4,4,8);
  rowHeight(ws,5,5,24); rowHeight(ws,6,8,24); rowHeight(ws,9,9,8); rowHeight(ws,10,11,28);
  rowHeight(ws,13,14,22); rowHeight(ws,15,16,24); rowHeight(ws,17,17,20); rowHeight(ws,18,18,8);
  rowHeight(ws,19,19,22); rowHeight(ws,20,25,24); rowHeight(ws,26,26,8); rowHeight(ws,27,27,22); rowHeight(ws,28,34,23); rowHeight(ws,42,44,28);
  ws.getRange("A2:L3").format.horizontalAlignment="left";
  ws.getRange("B20:F25").format.horizontalAlignment="left"; ws.getRange("H20:L25").format.horizontalAlignment="left"; ws.getRange("B42:L44").format.horizontalAlignment="left";
}

// 数据与来源。
{
  const ws=sheet("数据与来源"); ws.showGridLines=false; ws.tabColor="#7F8C8D";
  title(ws,"A2:I2","北京银行估值数据与来源","优先使用交易所定期报告；市场与同业快照使用同一时点第三方数据并交叉核验");
  ws.getRange("A4:I4").values=[["指标/表格","数据值/范围","口径与单位","截至日期","发布日期","来源名称","URL","页码/表名","备注"]]; header(ws,"A4:I4");
  const sourceRows=[
    ["2026H1经营与风险","营收、利润、ROE、NIM、资产质量、资本","集团；百万元/比率",new Date("2026-06-30"),new Date("2026-08-29"),"北京银行2026年半年度报告","https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-29/601169_20260829_PXP5.pdf","第12—17页、管理层讨论","关键事实主来源"],
    ["2025A经营与资本","年度利润、BPS、NIM、不良、资本","集团；百万元/比率",new Date("2025-12-31"),new Date("2026-04-28"),"北京银行2025年年度报告","https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2026/2026-4/2026-04-28/12226675.PDF","第23—31页","交易所披露文件镜像"],
    ["当前股价","5.62元","盘中延迟快照",new Date("2026-10-14T11:55:55+08:00"),new Date("2026-10-14"),"东方财富行情接口","https://push2.eastmoney.com/api/qt/stock/get?secid=1.601169&fields=f57,f58,f43,f60,f84,f116,f162,f164,f167,f86","实时行情字段","非收盘价"],
    ["历史价格","2016—2026日线","不复权收盘价",new Date("2026-10-14"),new Date("2026-10-14"),"东方财富历史行情接口","https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.601169&klt=101&fqt=0&beg=20160101&end=20261014&lmt=5000&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61","年末最后交易日","用于历史PB/PE"],
    ["十年财务","2016—2025年度，2026H1","亿元/元/比率",new Date("2026-06-30"),new Date("2026-08-29"),"东方财富F10主财务数据","https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_F10_FINANCE_MAINFINADATA&columns=ALL&filter=(SECUCODE%3D%22601169.SH%22)&sortColumns=REPORT_DATE&sortTypes=-1&pageSize=100&pageNumber=1","主财务指标","年度关键数与公司报告核对"],
    ["分红历史","2016—2026H1","每10股税前现金分红",new Date("2026-06-30"),new Date("2026-08-29"),"东方财富分红数据","https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_SHAREBONUS_DET&columns=ALL&filter=(SECURITY_CODE%3D%22601169%22)&sortColumns=REPORT_DATE&sortTypes=-1&pageSize=100&pageNumber=1","分红实施/预案","2026H1为董事会预案"],
    ["同业快照","7家城商行","股价、PE、PB",new Date("2026-10-14T11:56:00+08:00"),new Date("2026-10-14"),"东方财富行情接口","https://push2.eastmoney.com/api/qt/stock/get","同一时点字段","第三方便利数据"],
    ["同业财务","7家城商行2026H1","ROE、NIM、不良、拨备、CET1",new Date("2026-06-30"),new Date("2026-08-31"),"东方财富F10主财务数据","https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_F10_FINANCE_MAINFINADATA&columns=ALL","2026中报字段","关键北京银行数据以公司报告为准"],
    ["三季报边界","预约2026-10-31披露","上交所预约日期",new Date("2026-10-14"),new Date("2026-10-14"),"上交所定期报告预约情况","https://www.sse.com.cn/disclosure/listedinfo/periodic/","2026年三季报","尚未披露，不纳入"],
    ["监管最低资本","CET1 5%、一级6%、总资本8%基础线","不含附加与缓冲",new Date("2026-10-14"),new Date("2024-01-01"),"商业银行资本管理办法","https://www.gov.cn/zhengce/zhengceku/202311/content_6915944.htm","资本要求","实际监管要求还含储备与系统重要性附加"],
  ];
  ws.getRange("A5:I14").values=sourceRows; bodyTable(ws,"A5:I14"); fmt(ws,"D5:E14","yyyy-mm-dd");
  section(ws,"A17:F17","关键模型假设");
  ws.getRange("A18:F18").values=[["假设","数值","类型","理由","可编辑位置","版本"]]; header(ws,"A18:F18");
  ws.getRange("A19:F27").values=[["归一化EPS",1.20,"分析假设","2026H1年化后考虑季节性与风险成本","估值敏感性!B8","2026-10-14"],["归一化ROE",0.085,"分析假设","低于2026H1年化ROE，接近资本约束下稳态","估值敏感性!B5","2026-10-14"],["股权成本Ke",0.115,"分析假设","城商行风险、资本与资产质量溢价","估值敏感性!B6","2026-10-14"],["长期增长率",0.025,"分析假设","低于长期名义经济增速的审慎取值","估值敏感性!B7","2026-10-14"],["基准支付率",0.32,"分析假设","参考历史约30%并考虑中期分红","估值敏感性!B9","2026-10-14"],["PB–ROE模型折价",0.05,"分析假设","公式稳定期假设偏强","估值系统!B12","2026-10-14"],["同业ROE弹性β",0.80,"分析假设","PB对ROE差异非线性传导","同业比较!B19","2026-10-14"],["同业额外折价",0.15,"分析假设","CET1、NPL与业务结构差异","同业比较!B20","2026-10-14"],["估值权重","15/15/10/10/20/30%","分析假设","提高DDM权重，降低历史倍数权重","估值系统!D17:D22","2026-10-14"]];
  bodyTable(ws,"A19:F27"); fmt(ws,"B19","0.00"); fmt(ws,"B20:B24","0.0%"); fmt(ws,"B25","0.00"); fmt(ws,"B26","0.0%");
  ws.getRange("A29:I33").values=[["限制","股价为盘中延迟快照，后续交易会改变安全边际。","","","","","","",""] ,["限制","2026Q3 未披露；截至报告制作日，最新经营数据仍为 2026H1。","","","","","","",""] ,["限制","半年度报告未完整拆分承担信用风险的涉房业务总口径，不能用对公房地产贷款代替。","","","","","","",""] ,["限制","同业数据采用统一第三方字段，仍可能存在会计与业务结构差异。","","","","","","",""] ,["说明","本工作簿用于研究与信息整理，不构成个性化投资建议。","","","","","","",""]];
  for(let r=29;r<=33;r++) ws.mergeCells(`B${r}:I${r}`);
  ws.getRange("A29:A33").format.fill=C.gray; ws.getRange("B29:I33").format.fill=C.paleBlue;
  col(ws,"A",22); col(ws,"B",18); col(ws,"C",18); col(ws,"D",15); col(ws,"E",15); col(ws,"F",24); col(ws,"G",52); col(ws,"H",22); col(ws,"I",28);
  setBase(ws,"A1:I35"); rowHeight(ws,5,14,44); rowHeight(ws,19,27,32); rowHeight(ws,29,33,34); ws.freezePanes.freezeRows(4);
}

// 统一工作表基础样式、首屏和条件格式。
for(const name of sheetNames){
  const ws=sheet(name);
  const used=ws.getUsedRange();
  if(used){
    used.format.font.name=FONT;
  }
}

// 估值敏感性条件格式：低于当前价显示红色，高于当前价显示绿色。
for(const addr of ["H7:J12","H17:J22","H27:J32"]){
  const r=sheet("估值敏感性").getRange(addr);
  r.conditionalFormats.add("cellIs",{operator:"lessThan",formula:5.62,format:{fill:C.lightRed,font:{color:C.red,bold:true}}});
  r.conditionalFormats.add("cellIs",{operator:"greaterThanOrEqual",formula:5.62,format:{fill:C.lightGreen,font:{color:"#006100"}}});
}

// 统一标签色和页签顺序视觉。
sheet("一图流").tabColor=C.navy;
sheet("投资结论").tabColor=C.navy;
sheet("估值系统").tabColor=C.blue;
sheet("估值敏感性").tabColor=C.blue;
sheet("股息估值").tabColor=C.blue2;
sheet("数据与来源").tabColor="#7F8C8D";

// 计算、输入扰动测试、恢复。
wb.recalculate();
const baseComposite = sheet("估值系统").getRange("B26").values[0][0];
sheet("估值敏感性").getRange("B5").values=[[0.09]];
wb.recalculate();
const changedComposite = sheet("估值系统").getRange("B26").values[0][0];
sheet("估值敏感性").getRange("B5").values=[[0.085]];
wb.recalculate();

const keyCheck = await wb.inspect({kind:"table",range:"一图流!A1:N43",include:"values,formulas",tableMaxRows:43,tableMaxCols:14,maxChars:9000});
const errorCheck = await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:100},summary:"final formula error scan",maxChars:6000});
console.log(JSON.stringify({baseComposite,changedComposite,assumptionTestPassed:changedComposite!==baseComposite},null,2));
console.log(keyCheck.ndjson.slice(0,9000));
console.log(errorCheck.ndjson.slice(0,6000));

for(const name of sheetNames){
  const preview=await wb.render({sheetName:name,autoCrop:"all",scale:0.8,format:"png"});
  await fs.writeFile(path.join(previewDir,`${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}

const out=await SpreadsheetFile.exportXlsx(wb);
await out.save(outputPath);

const imported=await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const recheck=await imported.inspect({kind:"sheet",include:"id,name",maxChars:4000});
const reErrors=await imported.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:100},summary:"reimport formula error scan",maxChars:6000});
let chartCount=0;
for(const name of sheetNames) chartCount += imported.worksheets.getItem(name).charts.items.length;
console.log(recheck.ndjson);
console.log(reErrors.ndjson);
console.log(JSON.stringify({outputPath,chartCount,sheetCount:sheetNames.length},null,2));
