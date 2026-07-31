import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/koki/Desktop/ai-komon2";
const BUILD = path.join(ROOT, ".lead-magnet-refresh/build-v3");
const ASSETS = path.join(BUILD, "assets");
const OUTPUT = path.join(BUILD, "output");
const FINAL_PPTX = path.join(ROOT, "materials/ai-komon-ai-presentation-masterclass.pptx");

const W = 1280;
const H = 720;
const C = {
  ink: "#111111",
  paper: "#FFFFFF",
  fog: "#F2F3F5",
  soft: "#E4E6EA",
  mid: "#62666D",
  red: "#E33B36",
  redSoft: "#FBE9E8",
  blue: "#2357D9",
  blueSoft: "#E9EEFD",
  yellow: "#F4C542",
  yellowSoft: "#FFF5CC",
  green: "#2F7A4A",
};

const S = {
  microsoftTips:
    "https://support.microsoft.com/en-US/PowerPoint/tips-for-creating-and-delivering-an-effective-presentation",
  microsoftAccess:
    "https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities",
  thinkcell:
    "https://info.think-cell.com/rs/287-QVC-366/images/EB-PPTBP23-EN-PowerPoint-Best-Practices.pdf",
  duarte:
    "https://www.duarte.com/resources/communication-skills/business-storytelling/",
  openai:
    "https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices",
  anthropic:
    "https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md",
  exportPdf:
    "https://support.microsoft.com/en-us/powerpoint/export-a-presentation",
  fonts:
    "https://support.microsoft.com/en-US/Office/fonts/download-and-install-custom-fonts-to-use-with-office",
  compatibility:
    "https://support.microsoft.com/en-US/PowerPoint/compatibility-checker-in-powerpoint",
};

const imagePaths = {
  cover: path.join(ASSETS, "cover-background.png"),
  stalled: path.join(ASSETS, "stalled-meeting.png"),
  generic: path.join(ASSETS, "generic-ai-background.png"),
  workshop: path.join(ASSETS, "meaningful-workshop.png"),
  busy: path.join(ASSETS, "busy-project-room.png"),
  closing: path.join(ASSETS, "closing-work-session.png"),
};

async function bytes(filePath) {
  const data = await fs.readFile(filePath);
  return data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function rect(slide, x, y, w, h, fill = C.paper, options = {}) {
  const geometry = options.geometry ?? "rect";
  return slide.shapes.add({
    geometry,
    name: options.name,
    position: { left: x, top: y, width: w, height: h, rotation: options.rotation ?? 0 },
    fill,
    line: options.line ?? { style: "solid", fill: options.lineColor ?? "none", width: options.lineWidth ?? 0 },
    ...(geometry === "rect" || geometry === "textbox" || geometry === "roundRect"
      ? { borderRadius: options.radius ?? 0 }
      : {}),
    shadow: options.shadow ?? "shadow-none",
  });
}

function text(slide, value, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: options.name,
    placeholderType: options.placeholderType,
    position: { left: x, top: y, width: w, height: h, rotation: options.rotation ?? 0 },
    fill: options.fill ?? "none",
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
    borderRadius: options.radius ?? 0,
  });
  shape.text = value;
  shape.text.style = {
    typeface: "Hiragino Kaku Gothic ProN",
    fontSize: options.size ?? 24,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
    lineSpacing: options.lineSpacing ?? 1,
    autoFit: options.autoFit ?? "shrinkText",
    wrap: "square",
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return shape;
}

function title(slide, value, options = {}) {
  const dark = options.dark ?? false;
  const y = options.y ?? 46;
  const x = options.x ?? 64;
  const w = options.w ?? 1152;
  const h = options.h ?? (value.includes("\n") ? 112 : 68);
  return text(slide, value, x, y, w, h, {
    name: `slide-title-${options.index ?? ""}`,
    placeholderType: "title",
    size: options.size ?? 48,
    bold: true,
    color: options.color ?? (dark ? C.paper : C.ink),
    lineSpacing: 0.95,
    valign: "middle",
  });
}

function label(slide, value, x, y, w, options = {}) {
  return text(slide, value, x, y, w, options.h ?? 24, {
    size: options.size ?? 15,
    bold: options.bold ?? true,
    color: options.color ?? C.mid,
    align: options.align ?? "left",
    valign: "middle",
  });
}

function pageNumber(slide, n, dark = false) {
  text(slide, String(n).padStart(2, "0"), 1184, 678, 32, 18, {
    size: 14,
    bold: true,
    align: "right",
    color: dark ? "#FFFFFF/70" : C.mid,
  });
}

function note(slide, purpose, urls = [], generated = []) {
  const lines = [purpose, "", "[Sources]"];
  for (const url of urls) lines.push(`- ${url}`);
  for (const asset of generated) lines.push(`- Generated visual: ${asset}（AI顧問室制作）`);
  if (!urls.length && !generated.length) lines.push("- AI顧問室による実務工程の整理");
  lines.push("[/Sources]");
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

function fullImage(slide, buffer, alt) {
  return slide.images.add({
    blob: buffer,
    contentType: "image/png",
    alt,
    fit: "cover",
    position: { left: 0, top: 0, width: W, height: H },
  });
}

function line(slide, x, y, w, h, color = C.ink, width = 2, rotation = 0) {
  const horizontalFlip = w < 0;
  const verticalFlip = h < 0;
  const left = horizontalFlip ? x + w : x;
  const top = verticalFlip ? y + h : y;
  return slide.shapes.add({
    geometry: "line",
    position: {
      left,
      top,
      width: Math.abs(w),
      height: Math.abs(h),
      rotation,
      horizontalFlip,
      verticalFlip,
    },
    fill: "none",
    line: { style: "solid", fill: color, width },
  });
}

function arrow(slide, x, y, w, h, fill = C.blue, rotation = 0) {
  return rect(slide, x, y, w, h, fill, {
    geometry: "rightArrow",
    rotation,
    line: { style: "solid", fill: "none", width: 0 },
  });
}

function dot(slide, x, y, d, fill, value = "", options = {}) {
  const shape = rect(slide, x, y, d, d, fill, {
    geometry: "ellipse",
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
    shadow: options.shadow,
  });
  if (value) {
    shape.text = value;
    shape.text.style = {
      typeface: "Hiragino Kaku Gothic ProN",
      fontSize: options.size ?? 24,
      bold: true,
      color: options.color ?? C.paper,
      alignment: "center",
      verticalAlignment: "middle",
      insets: { top: 0, right: 0, bottom: 0, left: 0 },
      autoFit: "shrinkText",
    };
  }
  return shape;
}

function paper(slide, x, y, w, h, options = {}) {
  return rect(slide, x, y, w, h, options.fill ?? C.paper, {
    radius: options.radius ?? 18,
    lineColor: options.lineColor ?? "#D8DADE",
    lineWidth: options.lineWidth ?? 1,
    shadow: options.shadow ?? "shadow-lg",
    rotation: options.rotation ?? 0,
  });
}

function section(slide, value, dark = false) {
  label(slide, value, 64, 18, 280, { color: dark ? "#FFFFFF/72" : C.mid, size: 14 });
}

function footerRule(slide, dark = false) {
  line(slide, 64, 665, 1088, 0, dark ? "#FFFFFF/20" : "#D9DADF", 1);
}

function checklistRows(slide, items, x, y, w, rowH, accent = C.blue) {
  items.forEach((item, index) => {
    dot(slide, x, y + index * rowH + 2, 28, accent, String(index + 1), { size: 15 });
    text(slide, item, x + 44, y + index * rowH, w - 44, rowH - 4, {
      size: 23,
      bold: index === 0,
      valign: "middle",
    });
  });
}

function miniSlide(slide, x, y, w, h, kind, accent, rotation = 0) {
  paper(slide, x, y, w, h, { radius: 8, shadow: "shadow-sm", rotation });
  if (kind === "hero") {
    rect(slide, x + 16, y + 16, w * 0.56, 14, accent);
    rect(slide, x + 16, y + 44, w * 0.72, 28, C.ink);
  } else if (kind === "contrast") {
    rect(slide, x + 16, y + 22, (w - 42) / 2, h - 42, C.redSoft);
    rect(slide, x + 26 + (w - 42) / 2, y + 22, (w - 42) / 2, h - 42, C.blueSoft);
  } else if (kind === "process") {
    for (let i = 0; i < 3; i++) {
      dot(slide, x + 18 + i * ((w - 56) / 2), y + h / 2 - 12, 24, i === 2 ? C.yellow : accent);
      if (i < 2) arrow(slide, x + 42 + i * ((w - 56) / 2), y + h / 2 - 6, (w - 86) / 2, 12, "#B7C5F3");
    }
  } else if (kind === "evidence") {
    rect(slide, x + 16, y + 20, w * 0.42, h - 40, C.fog);
    rect(slide, x + w * 0.52, y + 24, w * 0.32, 18, accent);
    rect(slide, x + w * 0.52, y + 54, w * 0.40, 12, C.soft);
  } else {
    rect(slide, x + 20, y + 20, w - 40, h - 62, C.yellowSoft);
    rect(slide, x + w * 0.55, y + h - 30, w * 0.30, 14, accent);
  }
}

async function build() {
  await fs.mkdir(OUTPUT, { recursive: true });
  await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });

  const IMG = {};
  for (const [key, filePath] of Object.entries(imagePaths)) IMG[key] = await bytes(filePath);

  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 01
  {
    const s = deck.slides.add();
    fullImage(s, IMG.cover, "夜の会議室とプレゼン資料、白い意思決定シート");
    rect(s, 0, 0, W, H, "#000000/26");
    paper(s, 92, 112, 620, 470, { fill: "#FFFFFF/96", radius: 20, shadow: "shadow-2xl" });
    label(s, "社長・決裁者向け 実務プレイブック", 132, 150, 420, { color: C.blue, size: 15 });
    text(s, "これだけでOK。\nAIでクオリティの高い\nスライドを作る方法", 132, 196, 520, 210, {
      name: "slide-title-01",
      placeholderType: "title",
      size: 52,
      bold: true,
      lineSpacing: 0.93,
    });
    text(s, "経営会議で判断される資料を、\nAIと人で設計する5段階", 132, 430, 500, 76, {
      size: 24,
      color: C.mid,
      lineSpacing: 1.08,
    });
    rect(s, 132, 532, 154, 8, C.yellow, { radius: 4 });
    pageNumber(s, 1, true);
    note(s, "この教材はデザイン集ではなく、AIと人の作業を分ける実務工程であると宣言する。", [], ["cover-background.png"]);
  }

  // 02
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "PROBLEM / SPEED ≠ DECISION");
    title(s, "AIで資料は速くなる。\nでも、経営会議の判断は速くならない。", { index: 2 });
    text(s, "生成速度", 90, 216, 360, 58, { size: 38, bold: true, color: C.blue, align: "center" });
    text(s, "判断速度", 830, 216, 360, 58, { size: 38, bold: true, color: C.red, align: "center" });
    for (let i = 0; i < 6; i++) {
      miniSlide(s, 86 + i * 46, 306 + i * 22, 230, 126, i % 2 ? "contrast" : "hero", C.blue, -7 + i * 2);
    }
    text(s, "≠", 554, 292, 170, 130, { size: 112, bold: true, align: "center", valign: "middle" });
    paper(s, 846, 312, 316, 184, { radius: 14, shadow: "shadow-md" });
    label(s, "会議後の決定", 878, 342, 220, { color: C.red });
    rect(s, 878, 388, 252, 54, C.redSoft, { radius: 8 });
    text(s, "未記入", 878, 388, 252, 54, { size: 26, bold: true, color: C.red, align: "center", valign: "middle" });
    text(s, "速く作ることと、相手が決められることは別の設計課題。", 192, 586, 896, 42, {
      size: 27,
      bold: true,
      align: "center",
    });
    footerRule(s);
    pageNumber(s, 2);
    note(s, "AIの価値を否定せず、評価軸を作成時間から意思決定へ移す。");
  }

  // 03
  {
    const s = deck.slides.add();
    fullImage(s, IMG.stalled, "資料を見ながら判断が止まっている日本の経営会議");
    rect(s, 0, 0, W, H, "#000000/22");
    paper(s, 62, 54, 1156, 602, { fill: "#FFFFFF/94", radius: 20, shadow: "shadow-2xl" });
    title(s, "資料は完成しているのに、\n経営会議の判断が進まない。", { index: 3, x: 104, y: 82, w: 1050 });
    label(s, "会議後に残る3つ", 104, 230, 300, { color: C.red, size: 17 });
    const remarks = ["「もう少し情報がほしい」", "「社内で確認します」", "「次回また検討します」"];
    remarks.forEach((v, i) => {
      rect(s, 104, 280 + i * 82, 690 - i * 58, 58, i === 2 ? C.redSoft : C.fog, { radius: 10 });
      text(s, v, 128, 280 + i * 82, 620, 58, { size: 26, bold: i === 2, valign: "middle" });
    });
    text(s, "ページは完成。\n決定は未完成。", 842, 306, 282, 128, {
      size: 38,
      bold: true,
      color: C.red,
      align: "center",
      valign: "middle",
      lineSpacing: 1.05,
    });
    pageNumber(s, 3);
    note(s, "読者自身の会議を想起させる。成果数値は断定しない。", [], ["stalled-meeting.png"]);
  }

  // 04
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "CAUSE / DEFINE THE DECISION");
    title(s, "止まる理由は、ページ不足ではなく\n「何を決めるか」が曖昧だから。", { index: 4 });
    for (let i = 0; i < 9; i++) {
      paper(s, 82 + i * 14, 260 - i * 10, 390, 238, { radius: 10, shadow: "shadow-sm", rotation: -5 + i });
    }
    text(s, "ページを増やす", 154, 382, 278, 50, { size: 30, bold: true, color: C.mid, align: "center" });
    arrow(s, 530, 356, 106, 40, C.red);
    paper(s, 696, 222, 492, 330, { radius: 18, shadow: "shadow-xl" });
    label(s, "決めること", 740, 258, 180, { color: C.blue, size: 17 });
    rect(s, 740, 308, 400, 102, C.yellowSoft, { radius: 12 });
    text(s, "次回、担当部署で\n2週間の検証を始めるか", 764, 326, 352, 66, {
      size: 28,
      bold: true,
      align: "center",
      valign: "middle",
    });
    text(s, "「決定」とは、会議後に誰が何をするかが変わる選択。", 740, 452, 400, 54, {
      size: 22,
      color: C.mid,
      align: "center",
      valign: "middle",
    });
    pageNumber(s, 4);
    note(s, "意思決定設計を、会議後の行動が変わる選択として定義する。");
  }

  // 05
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    section(s, "FAILURE MODE / ONE-SHOT GENERATION", true);
    title(s, "一発生成は、\n平均的なページを大量につくる。", { index: 5, dark: true, w: 610 });
    paper(s, 66, 228, 472, 298, { fill: "#1D1D1D", lineColor: "#444444", radius: 18, shadow: "shadow-xl" });
    label(s, "PROMPT", 98, 260, 120, { color: "#FFFFFF/60" });
    text(s, "「このテーマで\n30枚の資料を作って」", 98, 314, 382, 104, {
      size: 32,
      bold: true,
      color: C.paper,
      lineSpacing: 1.1,
    });
    rect(s, 98, 462, 214, 42, C.blue, { radius: 10 });
    text(s, "一度で完成させる", 98, 462, 214, 42, { size: 18, bold: true, color: C.paper, align: "center", valign: "middle" });
    for (let i = 0; i < 7; i++) {
      miniSlide(s, 666 + (i % 3) * 154, 182 + Math.floor(i / 3) * 136, 188, 106, i % 2 ? "contrast" : "hero", i % 3 === 0 ? C.red : C.blue, -3 + i);
    }
    const issues = ["似た構図", "長い本文", "根拠の混在", "弱い結論"];
    issues.forEach((v, i) => {
      text(s, v, 650 + i * 148, 586, 136, 38, { size: 19, bold: true, color: i === 3 ? C.red : C.paper, align: "center" });
    });
    footerRule(s, true);
    pageNumber(s, 5, true);
    note(s, "明確・具体的な指示と反復改善を、資料制作の工程分解へ翻訳する。", [S.openai]);
  }

  // 06
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "WORST FUTURE / FAILURE LOOP");
    title(s, "このままでは修正と不信が増え、\nAI導入そのものが止まる。", { index: 6 });
    const nodes = [
      { x: 136, y: 254, v: "生成", c: C.blue },
      { x: 478, y: 198, v: "修正", c: C.red },
      { x: 828, y: 254, v: "根拠確認", c: C.yellow },
      { x: 478, y: 440, v: "作り直し", c: C.red },
    ];
    arrow(s, 304, 270, 150, 34, "#C9D5FA", -10);
    arrow(s, 720, 270, 150, 34, "#F4D3D1", 10);
    arrow(s, 774, 420, 150, 34, "#F4D3D1", 150);
    arrow(s, 304, 420, 150, 34, "#F4D3D1", 210);
    nodes.forEach((n) => {
      dot(s, n.x, n.y, 154, n.c, n.v, { size: 24, color: n.c === C.yellow ? C.ink : C.paper, shadow: "shadow-md" });
    });
    rect(s, 512, 330, 256, 104, C.ink, { radius: 18, shadow: "shadow-xl" });
    text(s, "導入停止", 512, 330, 256, 104, { size: 38, bold: true, color: C.paper, align: "center", valign: "middle" });
    text(s, "起こりうる失敗ループ：生成を完成と扱い、人の確認工程を持たない。", 230, 626, 820, 34, {
      size: 21,
      color: C.mid,
      align: "center",
    });
    pageNumber(s, 6);
    note(s, "組織の実測値ではなく、起こりうる典型的なリスクモデルとして説明する。");
  }

  // 07
  {
    const s = deck.slides.add();
    s.background.fill = "#F6F7FA";
    section(s, "BEST FUTURE / DECISION LOG");
    title(s, "反対に、判断が設計された資料は、\n会議後の次の一手を生む。", { index: 7 });
    paper(s, 132, 208, 1016, 390, { radius: 20, shadow: "shadow-xl" });
    label(s, "会議後の決定ログ", 178, 244, 260, { color: C.blue, size: 18 });
    line(s, 178, 286, 924, 0, C.soft, 1);
    const log = [
      ["決定", "2週間の検証を開始", C.yellowSoft],
      ["Owner", "営業責任者", C.blueSoft],
      ["Deadline", "次回会議まで", C.fog],
      ["Next action", "対象業務を3つ選ぶ", C.redSoft],
    ];
    log.forEach((row, i) => {
      label(s, row[0], 178, 320 + i * 60, 180, { color: C.mid, size: 16 });
      rect(s, 378, 312 + i * 60, 688, 44, row[2], { radius: 8 });
      text(s, row[1], 398, 312 + i * 60, 640, 44, { size: 23, bold: i === 0, valign: "middle" });
    });
    dot(s, 1060, 522, 52, C.green, "✓", { size: 29 });
    label(s, "架空例", 1022, 574, 92, { align: "right", size: 14 });
    text(s, "良い資料は「分かった」で終わらず、次の行動が残る。", 238, 632, 804, 34, {
      size: 24,
      bold: true,
      align: "center",
    });
    pageNumber(s, 7);
    note(s, "決定を成果物として見せる。例は架空であることを明示する。");
  }

  // 08
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    section(s, "REFRAME / DECISION DESIGN", true);
    title(s, "経営者が判断できる資料は、\nページではなく意思決定を設計する。", { index: 8, dark: true });
    for (let i = 0; i < 5; i++) {
      miniSlide(s, 72 + i * 48, 306 + i * 32, 222, 126, i % 2 ? "contrast" : "hero", C.red, -8 + i * 3);
    }
    arrow(s, 386, 390, 168, 56, C.red);
    const stages = [
      ["理解", 622, 326, C.blue],
      ["比較", 758, 290, "#5276DF"],
      ["納得", 894, 252, C.yellow],
      ["行動", 1030, 210, C.red],
    ];
    stages.forEach(([v, x, y, c], i) => {
      dot(s, x, y, 104, c, v, { size: 22, color: c === C.yellow ? C.ink : C.paper, shadow: "shadow-lg" });
      if (i < stages.length - 1) arrow(s, x + 88, y + 44, 76, 18, "#FFFFFF/24", -15);
    });
    text(s, "意思決定設計 = 相手が理解し、比べ、納得し、行動できる順に材料を置くこと", 150, 600, 980, 42, {
      size: 25,
      bold: true,
      color: C.paper,
      align: "center",
    });
    footerRule(s, true);
    pageNumber(s, 8, true);
    note(s, "現状と可能性の差を使う考えを、実務の決定順序へ翻訳する。", [S.duarte]);
  }

  // 09
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "MAP / HOW PEOPLE MOVE");
    title(s, "経営者が判断するには、\n理解・比較・納得・行動の順が必要だ。", { index: 9 });
    const steps = [
      { n: "01", h: "理解", b: "何の話か", x: 88, y: 314, c: C.blue },
      { n: "02", h: "比較", b: "何が違うか", x: 376, y: 270, c: "#5276DF" },
      { n: "03", h: "納得", b: "なぜ信じられるか", x: 664, y: 224, c: C.yellow },
      { n: "04", h: "行動", b: "次に何をするか", x: 952, y: 176, c: C.red },
    ];
    steps.forEach((st, i) => {
      if (i < steps.length - 1) arrow(s, st.x + 180, st.y + 60, 122, 26, "#D5DDF6", -9);
      rect(s, st.x, st.y, 210, 142, st.c, { radius: 18, shadow: "shadow-lg" });
      label(s, st.n, st.x + 22, st.y + 18, 54, { color: st.c === C.yellow ? C.ink : "#FFFFFF/70" });
      text(s, st.h, st.x + 22, st.y + 48, 166, 40, { size: 31, bold: true, color: st.c === C.yellow ? C.ink : C.paper });
      text(s, st.b, st.x + 22, st.y + 96, 166, 28, { size: 18, color: st.c === C.yellow ? C.ink : "#FFFFFF/86" });
    });
    text(s, "AI導入提案なら：対象業務 → 現状との差 → 根拠 → 小さな検証", 194, 610, 892, 38, {
      size: 24,
      bold: true,
      align: "center",
    });
    pageNumber(s, 9);
    note(s, "学術モデルとしてではなく、本教材で使う実務上の順序として説明する。", [S.duarte]);
  }

  // 10
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "STEP 1 / BRIEF");
    title(s, "AIに頼む前に、読者・決定・根拠・\n次の行動を固定する。", { index: 10 });
    paper(s, 72, 212, 670, 402, { radius: 18, shadow: "shadow-lg" });
    label(s, "BRIEF / 4 QUESTIONS", 110, 242, 280, { color: C.blue, size: 17 });
    const fields = [
      ["読者", "誰が読むか"],
      ["決定", "何を決めてもらうか"],
      ["根拠", "何が信頼材料か"],
      ["次の行動", "会議後に何をしてほしいか"],
    ];
    fields.forEach((f, i) => {
      label(s, f[0], 110, 298 + i * 68, 128, { color: i === 1 ? C.red : C.mid, size: 17 });
      rect(s, 248, 288 + i * 68, 438, 46, i === 1 ? C.yellowSoft : C.fog, { radius: 8 });
      text(s, f[1], 268, 288 + i * 68, 398, 46, { size: 22, bold: i === 1, valign: "middle" });
    });
    paper(s, 786, 264, 420, 290, { fill: C.ink, lineColor: C.ink, radius: 18, shadow: "shadow-xl" });
    label(s, "COPY PROMPT", 822, 294, 180, { color: "#FFFFFF/60" });
    text(s, "あなたはプレゼン編集者です。\n次の4項目を質問し、曖昧な点を埋めてください。\n\n読者／決定／根拠／次の行動\n\n本文やスライドは、まだ作らないでください。", 822, 336, 346, 178, {
      size: 21,
      color: C.paper,
      lineSpacing: 1.12,
    });
    pageNumber(s, 10);
    note(s, "明確なコンテキストを先に渡す原則を、質問型のBrief作成にする。", [S.openai]);
  }

  // 11
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "BRIEF / VAGUE VS SPECIFIC");
    title(s, "Briefが曖昧なら、\nどれだけ良いプロンプトでも資料はぶれる。", { index: 11 });
    label(s, "VAGUE", 92, 226, 180, { color: C.red, size: 18 });
    paper(s, 92, 270, 446, 248, { fill: "#FAFAFA", radius: 16, shadow: "shadow-sm" });
    text(s, "経営者向けに\nAIの提案資料を作る", 132, 330, 366, 94, { size: 32, bold: true, color: "#8B8E94", align: "center", valign: "middle" });
    label(s, "読者も、決定も、場面も曖昧", 150, 460, 330, { color: C.red, align: "center" });
    arrow(s, 566, 368, 116, 44, C.yellow);
    label(s, "SPECIFIC", 726, 226, 180, { color: C.blue, size: 18 });
    paper(s, 726, 254, 466, 294, { radius: 16, shadow: "shadow-lg" });
    text(s, "従業員30〜100名の経営者が、\n問い合わせ対応で\n2週間の試験導入を承認する提案", 770, 314, 378, 134, {
      size: 25,
      bold: true,
      align: "center",
      valign: "middle",
      lineSpacing: 1.08,
    });
    rect(s, 816, 470, 284, 42, C.blueSoft, { radius: 8 });
    text(s, "判断条件が具体的", 816, 470, 284, 42, { size: 20, bold: true, color: C.blue, align: "center", valign: "middle" });
    text(s, "具体化するのは文章量ではなく、判断条件。", 322, 610, 636, 38, { size: 26, bold: true, align: "center" });
    pageNumber(s, 11);
    note(s, "具体的の意味を、形容詞追加ではなく読者・決定・場面の固定として説明する。", [S.openai]);
  }

  // 12
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    section(s, "STEP 2 / GHOST DECK", true);
    title(s, "最初に作るのは本文ではなく、\nタイトルだけのGhost Deckである。", { index: 12, dark: true, w: 700 });
    const ghostTitles = ["問題を特定する", "原因を絞る", "見方を変える", "根拠を示す", "今日の行動を決める"];
    ghostTitles.forEach((v, i) => {
      paper(s, 690 + i * 45, 158 + i * 78, 390, 104, { radius: 10, rotation: -6 + i * 2, shadow: "shadow-xl" });
      label(s, `0${i + 1}`, 718 + i * 45, 176 + i * 78, 44, { color: C.blue });
      text(s, v, 778 + i * 45, 180 + i * 78, 270, 56, { size: 25, bold: true, valign: "middle" });
    });
    paper(s, 68, 294, 508, 236, { fill: "#1C1C1C", lineColor: "#3C3C3C", radius: 18, shadow: "shadow-lg" });
    label(s, "COPY PROMPT", 104, 326, 160, { color: "#FFFFFF/60" });
    text(s, "Briefを基に、結論タイトルだけで\n12〜20枚の流れを作ってください。\n本文・画像・レイアウトは、\nまだ作らないでください。", 104, 370, 430, 130, {
      size: 23,
      color: C.paper,
      lineSpacing: 1.16,
    });
    footerRule(s, true);
    pageNumber(s, 12, true);
    note(s, "action title先行の考えを、日本語のGhost Deckとして手順化する。", [S.thinkcell]);
  }

  // 13
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "GHOST DECK / PASS-FAIL TEST");
    title(s, "タイトルだけで話が通れば、本文は短くできる。", { index: 13, h: 72 });
    const spine = [
      "問い合わせ対応に時間がかかっている",
      "原因は定型質問の繰り返しにある",
      "AIは一次回答だけを担当できる",
      "まず2週間、FAQ上位10件で検証する",
      "本日決めるのは担当者と開始日",
    ];
    line(s, 216, 224, 0, 360, C.blue, 4);
    spine.forEach((v, i) => {
      dot(s, 194, 226 + i * 72, 44, i === 4 ? C.yellow : C.blue, String(i + 1), {
        size: 18,
        color: i === 4 ? C.ink : C.paper,
      });
      paper(s, 264, 214 + i * 72, 760, 56, { radius: 10, shadow: i === 4 ? "shadow-md" : "shadow-sm" });
      text(s, v, 292, 214 + i * 72, 708, 56, { size: 24, bold: i === 4, valign: "middle" });
    });
    rect(s, 1054, 214, 146, 344, C.ink, { radius: 18 });
    text(s, "縦に読んで\n因果が\nつながるか", 1074, 290, 106, 126, {
      size: 26,
      bold: true,
      color: C.paper,
      align: "center",
      valign: "middle",
      lineSpacing: 1.08,
    });
    label(s, "架空例", 1068, 508, 112, { color: "#FFFFFF/60", align: "center" });
    pageNumber(s, 13);
    note(s, "action titles全体で一貫した物語になるという考えを、実務チェックへ落とす。", [S.thinkcell]);
  }

  // 14
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "STORY / BUILD PRESSURE");
    title(s, "物語は「現状・問題・転換・根拠・行動」の順に\n圧力をつくる。", { index: 14 });
    const story = [
      { x: 84, y: 388, h: "現状", b: "共有できる事実", c: C.mid },
      { x: 310, y: 432, h: "問題", b: "放置する損失", c: C.red },
      { x: 536, y: 318, h: "転換", b: "見方を変える一文", c: C.blue },
      { x: 762, y: 246, h: "根拠", b: "信じる材料", c: "#5276DF" },
      { x: 988, y: 174, h: "行動", b: "今日決めること", c: C.yellow },
    ];
    for (let i = 0; i < story.length - 1; i++) {
      const a = story[i];
      const b = story[i + 1];
      line(s, a.x + 74, a.y + 48, b.x - a.x - 48, b.y - a.y, i === 1 ? C.blue : "#BFC3C9", 5);
    }
    story.forEach((st) => {
      dot(s, st.x, st.y, 108, st.c, st.h, { size: 24, color: st.c === C.yellow ? C.ink : C.paper, shadow: "shadow-md" });
      text(s, st.b, st.x - 28, st.y + 124, 164, 38, { size: 17, color: C.mid, align: "center" });
    });
    paper(s, 308, 610, 664, 44, { fill: C.yellowSoft, radius: 10, shadow: "shadow-none" });
    text(s, "「圧力」は不安を煽ることではなく、次を知る必要を作ること。", 328, 610, 624, 44, {
      size: 21,
      bold: true,
      align: "center",
      valign: "middle",
    });
    pageNumber(s, 14);
    note(s, "現状と可能性の対比を、初心者向けの5段階に噛み砕く。", [S.duarte]);
  }

  // 15
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "COPY / TAKEAWAY TITLES");
    title(s, "タイトルには話題ではなく、\n読み手が持ち帰る結論を書く。", { index: 15 });
    paper(s, 92, 240, 1096, 314, { radius: 18, shadow: "shadow-lg" });
    label(s, "TOPIC TITLE", 132, 280, 200, { color: C.red });
    rect(s, 132, 324, 376, 104, C.redSoft, { radius: 12 });
    text(s, "AI導入の現状", 156, 324, 328, 104, { size: 34, bold: true, color: C.red, align: "center", valign: "middle" });
    arrow(s, 548, 352, 136, 48, C.yellow);
    label(s, "TAKEAWAY TITLE", 720, 280, 220, { color: C.blue });
    rect(s, 720, 318, 420, 126, C.blueSoft, { radius: 12 });
    text(s, "問い合わせ対応から始めると、\n小さく検証できる", 748, 338, 364, 84, {
      size: 27,
      bold: true,
      color: C.blue,
      align: "center",
      valign: "middle",
      lineSpacing: 1.05,
    });
    text(s, "主語 + 変化 / 判断 + 理由", 366, 478, 548, 42, { size: 24, bold: true, align: "center" });
    text(s, "タイトルだけで「だから何？」に答えているか。", 332, 606, 616, 38, { size: 25, bold: true, align: "center" });
    pageNumber(s, 15);
    note(s, "action titleは話題名ではなく、ページの主要メッセージを表すという原則を説明する。", [S.thinkcell]);
  }

  // 16
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "FOCUS / ONE SLIDE, ONE CLAIM");
    title(s, "1枚に1つの主張を守ると、\n視線の行き先が1つになる。", { index: 16 });
    label(s, "NG", 100, 228, 80, { color: C.red, size: 18 });
    paper(s, 100, 268, 470, 276, { radius: 14, shadow: "shadow-md" });
    const clutter = [
      [128, 302, 160, 52, C.redSoft],
      [350, 298, 174, 84, C.blueSoft],
      [162, 412, 222, 82, C.yellowSoft],
      [410, 420, 112, 68, C.fog],
    ];
    clutter.forEach((d, i) => {
      rect(s, d[0], d[1], d[2], d[3], d[4], { radius: 8 });
      text(s, ["結論", "例外", "次の行動", "補足"][i], d[0], d[1], d[2], d[3], { size: 21, bold: true, align: "center", valign: "middle" });
    });
    line(s, 332, 390, -124, -52, C.red, 3);
    line(s, 332, 390, 110, -54, C.red, 3);
    line(s, 332, 390, -72, 78, C.red, 3);
    line(s, 332, 390, 132, 78, C.red, 3);
    label(s, "OK", 706, 228, 80, { color: C.blue, size: 18 });
    paper(s, 706, 268, 474, 276, { radius: 14, shadow: "shadow-lg" });
    rect(s, 760, 314, 366, 98, C.blue, { radius: 12 });
    text(s, "結論は1つ", 760, 314, 366, 98, { size: 36, bold: true, color: C.paper, align: "center", valign: "middle" });
    text(s, "支える情報は、結論に従属させる", 760, 450, 366, 42, { size: 22, color: C.mid, align: "center" });
    text(s, "2つの「だから何？」があるなら、2枚に分ける。", 334, 608, 612, 38, { size: 25, bold: true, align: "center" });
    pageNumber(s, 16);
    note(s, "1スライド1アイデア、短い文章、折り返し回避の原則を結びつける。", [S.thinkcell, S.microsoftTips]);
  }

  // 17
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    section(s, "EVIDENCE / SO WHAT?", true);
    title(s, "根拠は数字を置くだけでなく、\n「だから何か」まで示す。", { index: 17, dark: true });
    const cols = [
      { x: 70, w: 328, c: "#232323", lab: "CLAIM", h: "次回は価格説明より\nセキュリティ確認を優先" },
      { x: 476, w: 328, c: "#F7F7F8", lab: "EVIDENCE", h: "稟議コメントの未確認事項が\nセキュリティ欄に集中" },
      { x: 882, w: 328, c: C.yellow, lab: "MEANING", h: "決裁停止の原因に合わせて\n会議の議題を変える" },
    ];
    arrow(s, 405, 366, 62, 34, "#FFFFFF/25");
    arrow(s, 811, 366, 62, 34, "#FFFFFF/25");
    cols.forEach((col, i) => {
      rect(s, col.x, 246, col.w, 298, col.c, { radius: 18, shadow: "shadow-xl" });
      label(s, col.lab, col.x + 28, 278, col.w - 56, { color: i === 0 ? "#FFFFFF/55" : C.mid });
      text(s, col.h, col.x + 28, 354, col.w - 56, 112, {
        size: 26,
        bold: true,
        color: i === 0 ? C.paper : C.ink,
        align: "center",
        valign: "middle",
        lineSpacing: 1.08,
      });
    });
    label(s, "架空例", 1088, 560, 114, { color: "#FFFFFF/55", align: "right" });
    footerRule(s, true);
    pageNumber(s, 17, true);
    note(s, "根拠を陳列せず、意思決定への含意まで書く。例は架空である。", [S.thinkcell]);
  }

  // 18
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "STEP 3 / SLIDE SPEC");
    title(s, "Slide Specが、各ページの主張・根拠・\n見せ方・出典を固定する。", { index: 18 });
    paper(s, 72, 208, 890, 422, { radius: 18, shadow: "shadow-xl" });
    label(s, "SLIDE SPEC / SAMPLE", 108, 236, 280, { color: C.blue, size: 17 });
    const specRows = [
      ["Title", "読み手が持ち帰る結論"],
      ["Narrative job", "このページが物語で担う役割"],
      ["Visible content", "画面に残す情報だけ"],
      ["Evidence", "主張を信じる材料"],
      ["Visual type", "HERO / CONTRAST / PROCESS / EVIDENCE / ACTION"],
      ["Layout", "情報の重心と視線"],
      ["Source", "出典URL"],
      ["QA risk", "切れ・重なり・誤認の危険"],
    ];
    specRows.forEach((r, i) => {
      label(s, r[0], 108, 280 + i * 39, 180, { color: i === 0 ? C.red : C.mid, size: 14 });
      rect(s, 288, 274 + i * 39, 628, 30, i === 0 ? C.yellowSoft : i % 2 ? C.paper : C.fog, { radius: 5 });
      text(s, r[1], 304, 274 + i * 39, 596, 30, { size: 17, bold: i === 0, valign: "middle" });
    });
    miniSlide(s, 1000, 280, 220, 132, "evidence", C.blue, 2);
    arrow(s, 934, 340, 72, 28, C.yellow);
    text(s, "作り始める前に、\n完成条件を\n言語化する。", 994, 442, 226, 108, {
      size: 23,
      bold: true,
      align: "center",
      valign: "middle",
      lineSpacing: 1.08,
    });
    pageNumber(s, 18);
    note(s, "計画・実装・QAの分離を参考に、初心者が使える事前仕様へ整理した。", [S.anthropic]);
  }

  // 19
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "VISUAL / FIVE TYPES");
    title(s, "見せ方は、主張に合わせて5つの型から選べる。", { index: 19, h: 72 });
    const types = [
      { x: 66, y: 250, w: 254, h: 210, k: "hero", n: "HERO", b: "結論を記憶させる", c: C.ink },
      { x: 338, y: 294, w: 208, h: 172, k: "contrast", n: "CONTRAST", b: "違いを判断させる", c: C.red },
      { x: 566, y: 250, w: 208, h: 210, k: "process", n: "PROCESS", b: "順序を理解させる", c: C.blue },
      { x: 794, y: 300, w: 208, h: 166, k: "evidence", n: "EVIDENCE", b: "根拠を信じてもらう", c: "#5276DF" },
      { x: 1022, y: 230, w: 192, h: 230, k: "action", n: "ACTION", b: "その場で使わせる", c: C.yellow },
    ];
    types.forEach((t) => {
      miniSlide(s, t.x, t.y, t.w, t.h, t.k, t.c);
      label(s, t.n, t.x, t.y + t.h + 22, t.w, { color: t.c === C.yellow ? C.ink : t.c, align: "center", size: 16 });
      text(s, t.b, t.x, t.y + t.h + 52, t.w, 36, { size: 18, align: "center", color: C.mid });
    });
    text(s, "先に型を選び、あとから内容を詰める。", 366, 626, 548, 38, { size: 26, bold: true, align: "center" });
    pageNumber(s, 19);
    note(s, "5型はAI顧問室による制作上の分類であり、状況に応じて複合してよい。", [S.microsoftTips, S.thinkcell]);
  }

  // 20
  {
    const s = deck.slides.add();
    fullImage(s, IMG.workshop, "業務プロセスを比較し意思決定する日本の管理職チーム");
    rect(s, 0, 0, W, H, "#000000/18");
    paper(s, 48, 42, 1184, 622, { fill: "#FFFFFF/92", radius: 20, shadow: "shadow-2xl" });
    title(s, "背景画像は、雰囲気ではなく\n理解を助ける舞台として使う。", { index: 20, x: 82, y: 72, w: 1110 });
    s.images.add({
      blob: IMG.generic,
      contentType: "image/png",
      alt: "意味を持たない抽象的なAI背景の例",
      fit: "cover",
      position: { left: 82, top: 246, width: 300, height: 214 },
      geometry: "roundRect",
      borderRadius: 14,
    });
    rect(s, 82, 246, 300, 214, "#000000/24", { radius: 14 });
    dot(s, 102, 266, 42, C.red, "×", { size: 25 });
    text(s, "ただ未来的\nただ綺麗\nただAIらしい", 126, 330, 212, 90, { size: 23, bold: true, color: C.paper, align: "center", valign: "middle", lineSpacing: 1.05 });
    paper(s, 448, 246, 700, 286, { fill: "#FFFFFF/96", radius: 16, shadow: "shadow-xl" });
    dot(s, 476, 274, 42, C.green, "✓", { size: 25 });
    text(s, "会議の緊張を見せる背景", 542, 272, 510, 42, { size: 27, bold: true, valign: "middle" });
    label(s, "+", 682, 336, 58, { size: 30, color: C.mid, align: "center" });
    rect(s, 536, 384, 520, 92, C.yellowSoft, { radius: 12 });
    text(s, "判断シートを前景に置く", 536, 384, 520, 92, { size: 29, bold: true, align: "center", valign: "middle" });
    text(s, "場所・人物・状況が、主張の理解に必要なときだけ使う。", 284, 590, 712, 38, { size: 23, bold: true, align: "center" });
    pageNumber(s, 20);
    note(s, "画像は話を伝えるために使い、多すぎないようにする原則を採用基準へ翻訳する。", [S.microsoftTips], ["generic-ai-background.png", "meaningful-workshop.png"]);
  }

  // 21
  {
    const s = deck.slides.add();
    fullImage(s, IMG.busy, "情報量の多いプロジェクトルーム");
    rect(s, 0, 0, W, H, "#000000/34");
    paper(s, 56, 42, 1168, 118, { fill: "#FFFFFF/96", radius: 18, shadow: "shadow-xl" });
    title(s, "背景画像の上には前景モックを置き、\n文字の居場所をつくる。", { index: 21, x: 90, y: 54, w: 1100, h: 94, size: 44 });
    paper(s, 82, 226, 378, 332, { radius: 18, shadow: "shadow-2xl", rotation: -3 });
    label(s, "PAPER MOCK", 120, 254, 180, { color: C.blue });
    text(s, "説明・結論", 120, 314, 300, 54, { size: 32, bold: true });
    text(s, "写真は舞台。\n文字は情報面。", 120, 394, 300, 84, { size: 25, color: C.mid, lineSpacing: 1.08 });
    paper(s, 482, 246, 438, 286, { fill: C.paper, radius: 18, shadow: "shadow-2xl", rotation: 2 });
    rect(s, 482, 246, 438, 42, C.ink, { radius: 18 });
    dot(s, 500, 260, 12, C.red);
    dot(s, 520, 260, 12, C.yellow);
    dot(s, 540, 260, 12, C.green);
    label(s, "BROWSER MOCK", 524, 318, 220, { color: C.blue });
    text(s, "プロンプト・操作", 524, 370, 338, 50, { size: 30, bold: true });
    rect(s, 524, 442, 338, 44, C.fog, { radius: 8 });
    text(s, "編集可能な入力欄", 544, 442, 298, 44, { size: 20, color: C.mid, valign: "middle" });
    paper(s, 964, 250, 208, 328, { fill: C.ink, radius: 28, shadow: "shadow-2xl", rotation: -2 });
    rect(s, 980, 274, 176, 278, C.paper, { radius: 18 });
    label(s, "DEVICE", 1002, 306, 130, { color: C.blue, align: "center" });
    text(s, "閲覧体験", 994, 366, 148, 52, { size: 28, bold: true, align: "center" });
    pageNumber(s, 21, true);
    note(s, "十分なコントラストを担保し、画像と文字の役割を分ける。", [S.microsoftTips, S.microsoftAccess], ["busy-project-room.png"]);
  }

  // 22
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "RHYTHM / VARY THE SILHOUETTE");
    title(s, "同じレイアウトを繰り返さず、\n主張に合わせて画面の形を変える。", { index: 22 });
    const rhythm = [
      { x: 70, y: 314, w: 188, h: 210, k: "hero", c: C.ink, r: -4 },
      { x: 260, y: 250, w: 180, h: 152, k: "contrast", c: C.red, r: 2 },
      { x: 448, y: 306, w: 196, h: 196, k: "process", c: C.blue, r: -2 },
      { x: 650, y: 232, w: 184, h: 168, k: "evidence", c: "#5276DF", r: 3 },
      { x: 842, y: 300, w: 176, h: 218, k: "action", c: C.yellow, r: -3 },
      { x: 1026, y: 218, w: 188, h: 178, k: "hero", c: C.ink, r: 2 },
    ];
    rhythm.forEach((r, i) => {
      miniSlide(s, r.x, r.y, r.w, r.h, r.k, r.c, r.r);
      if (i < rhythm.length - 1) line(s, r.x + r.w - 8, r.y + r.h / 2, rhythm[i + 1].x - (r.x + r.w) + 18, rhythm[i + 1].y + rhythm[i + 1].h / 2 - (r.y + r.h / 2), "#B7BAC1", 2);
    });
    text(s, "色を変えるのではなく、情報の形を変える。", 326, 604, 628, 38, { size: 26, bold: true, align: "center" });
    pageNumber(s, 22);
    note(s, "レイアウトを変え、全スライドを画像で確認する考えをリズム検査に使う。", [S.anthropic]);
  }

  // 23
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "COLLABORATION / AI × HUMAN");
    title(s, "AIには候補と速度を任せ、\n人は目的・事実・優先順位を持つ。", { index: 23 });
    label(s, "AI", 80, 236, 86, { color: C.blue, size: 20 });
    label(s, "HUMAN", 80, 452, 110, { color: C.red, size: 20 });
    line(s, 190, 260, 988, 0, C.soft, 2);
    line(s, 190, 476, 988, 0, C.soft, 2);
    const ai = ["タイトル候補", "構成案", "表現の短縮", "ビジュアル案"];
    const human = ["目的を決める", "事実を確認", "何を削るか", "最終承認"];
    for (let i = 0; i < 4; i++) {
      rect(s, 212 + i * 244, 286, 190, 74, C.blueSoft, { radius: 12 });
      text(s, ai[i], 212 + i * 244, 286, 190, 74, { size: 22, bold: true, color: C.blue, align: "center", valign: "middle" });
      if (i < 3) arrow(s, 404 + i * 244, 309, 46, 24, "#A8B9EF");
      rect(s, 212 + i * 244, 498, 190, 74, i === 3 ? C.yellowSoft : C.redSoft, { radius: 12 });
      text(s, human[i], 212 + i * 244, 498, 190, 74, { size: 22, bold: true, color: i === 3 ? C.ink : C.red, align: "center", valign: "middle" });
      if (i < 3) {
        rect(s, 420 + i * 244, 392, 52, 52, C.yellow, { geometry: "diamond", line: { style: "solid", fill: "none", width: 0 } });
        text(s, "承認", 408 + i * 244, 446, 76, 28, { size: 14, bold: true, align: "center" });
      }
    }
    text(s, "生成は委任できる。責任は委任しない。", 346, 632, 588, 40, { size: 27, bold: true, align: "center" });
    pageNumber(s, 23);
    note(s, "AIを自動完成装置ではなく、選択肢を速く出す協働者として位置づける。", [S.openai, S.anthropic]);
  }

  // 24
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    section(s, "WORKFLOW / FIVE STAGES", true);
    title(s, "制作はBrief、Ghost Deck、Slide Spec、\nVisual、QAの順に進める。", { index: 24, dark: true });
    const stages = [
      ["1", "Brief", "読者と決定"],
      ["2", "Ghost Deck", "タイトルで物語"],
      ["3", "Slide Spec", "根拠と見せ方"],
      ["4", "Visual", "制作"],
      ["5", "QA", "全ページ検査"],
    ];
    stages.forEach((st, i) => {
      const x = 58 + i * 244;
      rect(s, x, 278, 204, 144, i === 4 ? C.yellow : "#242424", {
        radius: 16,
        lineColor: i === 4 ? C.yellow : "#444444",
        lineWidth: 1,
        shadow: "shadow-lg",
      });
      label(s, st[0], x + 18, 294, 30, { color: i === 4 ? C.ink : "#FFFFFF/55" });
      text(s, st[1], x + 18, 332, 168, 42, { size: 25, bold: true, color: i === 4 ? C.ink : C.paper, align: "center" });
      text(s, st[2], x + 18, 380, 168, 28, { size: 16, color: i === 4 ? C.ink : "#FFFFFF/72", align: "center" });
      if (i < 4) {
        arrow(s, x + 202, 328, 42, 24, "#FFFFFF/22");
        if (i < 3) {
          rect(s, x + 208, 446, 48, 48, C.yellow, { geometry: "diamond", line: { style: "solid", fill: "none", width: 0 } });
          label(s, "人が承認", x + 180, 502, 106, { color: C.yellow, align: "center", size: 13 });
        }
      }
    });
    paper(s, 198, 554, 884, 74, { fill: "#1D1D1D", lineColor: "#444444", radius: 12, shadow: "shadow-none" });
    text(s, "「各工程の承認が出るまで次へ進まないでください。最初はBriefだけを作成してください。」", 224, 570, 832, 42, {
      size: 20,
      color: C.paper,
      align: "center",
      valign: "middle",
    });
    footerRule(s, true);
    pageNumber(s, 24, true);
    note(s, "本教材自身がこのワークフローで作られている。反復改善を工程承認で制御する。", [S.openai, S.anthropic]);
  }

  // 25
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "QA / DRAFT AS HYPOTHESIS");
    title(s, "AIの初稿は、完成品ではなく\n検査するための仮説である。", { index: 25 });
    miniSlide(s, 154, 228, 706, 372, "evidence", C.blue, -3);
    rect(s, 650, 250, 184, 58, C.red, { radius: 8, rotation: 4, shadow: "shadow-md" });
    text(s, "DRAFT 01", 650, 250, 184, 58, { size: 28, bold: true, color: C.paper, align: "center", valign: "middle", rotation: 4 });
    const review = [
      ["何が伝わるか", 914, 248, C.blue],
      ["何が余計か", 968, 344, C.red],
      ["何が足りないか", 926, 438, C.yellow],
      ["何が未確認か", 846, 536, C.ink],
    ];
    review.forEach((r) => {
      dot(s, r[1], r[2], 26, r[3]);
      text(s, r[0], r[1] + 42, r[2] - 4, 200, 34, { size: 21, bold: true, color: r[3] === C.yellow ? C.ink : r[3] });
      line(s, r[1] - 58, r[2] + 12, 52, 0, r[3], 2);
    });
    text(s, "直す前に、問題の種類を言葉にする。", 354, 626, 572, 38, { size: 26, bold: true, align: "center" });
    pageNumber(s, 25);
    note(s, "反復改善と全ページ検査を、初稿の定義として説明する。", [S.openai, S.anthropic]);
  }

  // 26
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    section(s, "QA / FIVE PASSES");
    title(s, "品質は、物語・焦点・収まり・根拠・\n読みやすさの5回に分けて確認する。", { index: 26 });
    miniSlide(s, 86, 286, 360, 220, "hero", C.blue, -2);
    const passes = [
      ["01", "物語", "タイトルだけで因果が通るか", C.blue],
      ["02", "焦点", "1枚1主張か", "#5276DF"],
      ["03", "収まり", "重なり・切れ・折返し", C.red],
      ["04", "根拠", "出典・仮定・架空例", C.yellow],
      ["05", "読みやすさ", "距離・コントラスト・読み順", C.green],
    ];
    passes.forEach((p, i) => {
      const y = 214 + i * 78;
      dot(s, 528, y, 48, p[3], p[0], { size: 16, color: p[3] === C.yellow ? C.ink : C.paper });
      text(s, p[1], 596, y - 4, 172, 40, { size: 25, bold: true, valign: "middle" });
      text(s, p[2], 772, y - 2, 414, 36, { size: 20, color: C.mid, valign: "middle" });
      if (i < passes.length - 1) line(s, 552, y + 48, 0, 30, C.soft, 2);
    });
    paper(s, 142, 548, 300, 74, { fill: C.ink, radius: 12, shadow: "shadow-md" });
    text(s, "1回 1目的", 142, 548, 300, 74, { size: 32, bold: true, color: C.paper, align: "center", valign: "middle" });
    pageNumber(s, 26);
    note(s, "検査を分けることで見落としを減らす実務手順。効果量は断定しない。", [S.microsoftTips, S.microsoftAccess, S.anthropic]);
  }

  // 27
  {
    const s = deck.slides.add();
    s.background.fill = C.fog;
    section(s, "QA / FOUR OUTPUTS");
    title(s, "PPTX、PDF、投影、スマホでは、\n同じ資料でも崩れ方が違う。", { index: 27 });
    const outputs = [
      { x: 74, y: 256, w: 286, h: 188, n: "PPTX", b: "編集・フォント・互換性", k: "hero", c: C.blue },
      { x: 390, y: 224, w: 220, h: 288, n: "PDF", b: "固定レイアウト・リンク", k: "evidence", c: C.red },
      { x: 640, y: 250, w: 316, h: 204, n: "投影", b: "距離・端の切れ・色", k: "contrast", c: C.yellow },
      { x: 1010, y: 218, w: 164, h: 300, n: "スマホ", b: "縮小時の文字量", k: "action", c: C.ink },
    ];
    outputs.forEach((o) => {
      if (o.n === "スマホ") {
        paper(s, o.x, o.y, o.w, o.h, { fill: C.ink, radius: 24, shadow: "shadow-xl" });
        rect(s, o.x + 12, o.y + 24, o.w - 24, o.h - 48, C.paper, { radius: 14 });
        miniSlide(s, o.x + 24, o.y + 54, o.w - 48, 92, o.k, o.c);
      } else {
        miniSlide(s, o.x, o.y, o.w, o.h, o.k, o.c);
      }
      label(s, o.n, o.x, o.y + o.h + 22, o.w, { color: o.c === C.yellow ? C.ink : o.c, align: "center", size: 18 });
      text(s, o.b, o.x, o.y + o.h + 50, o.w, 44, { size: 17, color: C.mid, align: "center" });
    });
    text(s, "開く → PDF化 → 全画面投影 → スマホ確認", 302, 622, 676, 38, { size: 25, bold: true, align: "center" });
    pageNumber(s, 27);
    note(s, "互換性、フォント置換、PDF書き出し、投影解像度の注意を実務チェックへまとめる。", [S.microsoftTips, S.exportPdf, S.fonts, S.compatibility]);
  }

  // 28
  {
    const s = deck.slides.add();
    fullImage(s, IMG.closing, "自社資料を一つ選びBriefを書き始める日本の経営者と担当者");
    rect(s, 0, 0, W, H, "#000000/12");
    paper(s, 54, 46, 742, 624, { fill: "#FFFFFF/96", radius: 20, shadow: "shadow-2xl" });
    title(s, "まず自社資料1本で試し、\nAI導入の判断を前に進める。", { index: 28, x: 92, y: 68, w: 648, h: 122 });
    label(s, "今日やること", 92, 232, 240, { color: C.blue, size: 18 });
    checklistRows(s, [
      "自社資料を1本選ぶ",
      "Briefの4項目を書く",
      "タイトルだけでGhost Deckを作る",
      "1枚だけSlide Specを書いて作り直す",
    ], 92, 274, 630, 64, C.blue);
    text(s, "教材だけで進められる方は、そのまま実践してください。", 92, 588, 626, 32, { size: 18, color: C.mid });
    paper(s, 844, 390, 364, 214, { fill: C.ink, lineColor: C.ink, radius: 18, shadow: "shadow-2xl" });
    label(s, "OPTION", 880, 420, 120, { color: "#FFFFFF/55" });
    text(s, "無料顧問\n1回分", 880, 458, 286, 74, { size: 34, bold: true, color: C.paper, lineSpacing: 0.98 });
    text(s, "自社資料を持ち込み、\nBriefとGhost Deckを一緒に作る", 880, 544, 286, 44, { size: 18, color: "#FFFFFF/78", lineSpacing: 1.1 });
    pageNumber(s, 28, true);
    note(s, "第1幕の会議が止まる問題を、自社資料1本の行動で回収する。CTAは支援の選択肢としてのみ提示する。", [], ["closing-work-session.png"]);
  }

  const inspect = await deck.inspect({
    kind: "slide,textbox,shape,image,notes",
    maxChars: 100000,
  });
  await fs.writeFile(path.join(OUTPUT, "deck-inspect.ndjson"), inspect.ndjson);

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await writeBlob(path.join(OUTPUT, `${stem}.png`), png);
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(OUTPUT, `${stem}.layout.json`), await layout.text());
  }

  const montage = await deck.export({ format: "webp", montage: true, scale: 0.5 });
  await writeBlob(path.join(OUTPUT, "deck-montage.webp"), montage);

  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL_PPTX);
  console.log(FINAL_PPTX);
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
