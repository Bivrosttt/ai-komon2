import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/koki/Desktop/ai-komon2";
const OUT_DIR = `${ROOT}/.lead-magnet-refresh/build/masterclass-output`;
const FINAL_PPTX = `${ROOT}/materials/ai-komon-ai-presentation-masterclass.pptx`;
const ASSET_DIR = `${ROOT}/.lead-magnet-refresh/build/masterclass-assets`;
const IMG = {
  cover: `${ASSET_DIR}/cover.png`,
  problem: `${ASSET_DIR}/problem.png`,
  structure: `${ASSET_DIR}/structure.png`,
  cta: `${ASSET_DIR}/cta.png`,
};

const W = 1280;
const H = 720;
const FONT = "Hiragino Sans";
const C = {
  ink: "#111214",
  charcoal: "#202225",
  paper: "#F7F7F4",
  white: "#FFFFFF",
  gray: "#656A70",
  light: "#E6E7E4",
  pale: "#EFF0ED",
  red: "#E43E2B",
  blue: "#1858D8",
  yellow: "#F6C945",
  paleRed: "#FBE9E6",
  paleBlue: "#E9F0FF",
  paleYellow: "#FFF5CE",
};

const SRC = {
  anthropic: "https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md",
  layouts: "https://github.com/tristan-mcinnis/pptx-from-layouts-skill",
  academic: "https://github.com/Gabberflast/academic-pptx-skill",
  fluid: "https://github.com/FluidForm-ai/fluiddocs-deck-builder",
  openai: "https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices",
  microsoft: "https://support.microsoft.com/en-us/office/make-your-powerpoint-presentations-accessible-to-people-with-disabilities-6f7772b2-2f33-4bd2-8ca7-dae3b2b3ef25",
  generated: "AI image generation via OpenAI image tool, 2026-07-28",
};

function shape(slide, geometry, x, y, w, h, fill = "none", line = "none", lineWidth = 0) {
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: lineWidth },
  });
}

function text(slide, value, x, y, w, h, style = {}) {
  const box = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  box.text = value;
  box.text.style = {
    typeface: FONT,
    fontSize: 20,
    color: C.ink,
    verticalAlignment: "top",
    wrap: "square",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
    ...style,
  };
  return box;
}

function img(slide, path, x, y, w, h, alt, fit = "cover") {
  return slide.images.add({
    blob: new Uint8Array(readFileSync(path)),
    contentType: "image/png",
    alt,
    fit,
    position: { left: x, top: y, width: w, height: h },
    geometry: "rect",
  });
}

function rule(slide, x, y, w, color = C.light, h = 2) {
  return shape(slide, "rect", x, y, w, h, color);
}

function dot(slide, x, y, size, color) {
  return shape(slide, "ellipse", x, y, size, size, color);
}

function frame(slide, page, section, dark = false) {
  const ink = dark ? C.white : C.ink;
  const muted = dark ? "#A9ADB2" : C.gray;
  text(slide, "AI顧問室", 66, 28, 150, 22, { fontSize: 14, bold: true, color: ink });
  text(slide, section.toUpperCase(), 220, 29, 340, 20, { fontSize: 12, bold: true, color: muted });
  text(slide, String(page).padStart(2, "0"), 1150, 28, 62, 22, { fontSize: 14, bold: true, color: muted, alignment: "right" });
  shape(slide, "rect", 66, 668, 8, 8, dark ? C.yellow : C.red);
  shape(slide, "rect", 1188, 668, 8, 8, dark ? C.blue : C.ink);
}

function notes(slide, body, sources = []) {
  const sourceLines = sources.map((url) => `- ${url}`).join("\n");
  slide.speakerNotes.textFrame.setText(`${body}\n\n[Sources]\n${sourceLines}\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}

function bigTitle(slide, value, y = 92, w = 1040, dark = false, size = 48) {
  return text(slide, value, 66, y, w, 126, {
    fontSize: size,
    bold: true,
    color: dark ? C.white : C.ink,
    lineSpacing: 0.96,
  });
}

function miniSlide(slide, x, y, w, h, accent, titleText, bodyLines = 3, dark = false) {
  shape(slide, "rect", x, y, w, h, dark ? C.charcoal : C.white, dark ? "#3B3E42" : C.light, 1);
  shape(slide, "rect", x + 14, y + 14, w * 0.18, 7, accent);
  text(slide, titleText, x + 14, y + 34, w - 28, 40, { fontSize: 13, bold: true, color: dark ? C.white : C.ink });
  for (let i = 0; i < bodyLines; i += 1) {
    const width = i === bodyLines - 1 ? w * 0.52 : w * (0.75 - i * 0.05);
    shape(slide, "rect", x + 14, y + 84 + i * 18, width, 4, dark ? "#686C72" : "#C8CBC8");
  }
}

function paperMock(slide, x, y, w, h, accent, titleText, subtitleText = "", dark = false) {
  const card = slide.shapes.add({
    geometry: "roundRect",
    position: { left: x, top: y, width: w, height: h },
    fill: dark ? C.charcoal : C.paper,
    line: { style: "solid", fill: dark ? "#555A61" : C.light, width: 1 },
    borderRadius: "rounded-xl",
    shadow: "shadow-lg",
  });
  shape(slide, "rect", x, y, 10, h, accent);
  shape(slide, "rect", x + 30, y + 28, 76, 7, accent);
  if (titleText) {
    text(slide, titleText, x + 30, y + 58, w - 62, 96, {
      fontSize: 36,
      bold: true,
      color: dark ? C.white : C.ink,
      lineSpacing: 0.98,
    });
  }
  if (subtitleText) {
    text(slide, subtitleText, x + 32, y + h - 72, w - 64, 42, {
      fontSize: 18,
      color: dark ? "#C8CCD1" : C.gray,
      lineSpacing: 1.12,
    });
  }
  return card;
}

function browserMock(slide, x, y, w, h, titleText, dark = false) {
  shape(slide, "roundRect", x, y, w, h, dark ? C.charcoal : C.white, dark ? "#555A61" : C.light, 1);
  shape(slide, "rect", x, y, w, 34, dark ? "#33373C" : "#E9EBE8");
  [C.red, C.yellow, C.blue].forEach((color, i) => dot(slide, x + 16 + i * 18, y + 11, 8, color));
  text(slide, titleText, x + 88, y + 8, w - 108, 18, { fontSize: 12, bold: true, color: dark ? "#D7DADF" : C.gray });
  return shape(slide, "rect", x + 18, y + 56, w - 36, h - 74, dark ? "#24272B" : C.paper, dark ? "#4A4E54" : C.light, 1);
}

async function writeBlob(path, blob) {
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 01 — Cover
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    img(s, IMG.cover, 0, 0, W, H, "断片的なアイデアが明快なプレゼンへ変わる編集的ビジュアル");
    shape(s, "rect", 0, 0, W, H, { color: C.ink, transparency: 48 });
    paperMock(s, 66, 86, 558, 548, C.red, "", "", false);
    text(s, "AI × PRESENTATION", 108, 146, 360, 22, { fontSize: 14, bold: true, color: C.red });
    text(s, "AIで、\n良質なプレゼンを\nつくる。", 108, 206, 470, 210, { fontSize: 52, bold: true, color: C.ink, lineSpacing: 0.92 });
    text(s, "速く埋める技術ではなく、\n相手の判断を動かす設計法。", 108, 506, 440, 48, { fontSize: 18, color: C.gray, lineSpacing: 1.12 });
    text(s, "AI顧問室 / 実務リードマグネット", 108, 584, 390, 22, { fontSize: 15, bold: true, color: C.gray });
    shape(s, "rect", 112, 620, 54, 12, C.blue);
    shape(s, "rect", 174, 620, 18, 12, C.yellow);
    text(s, "判断を動かす資料は、\n最初に物語から設計する。", 760, 548, 420, 60, { fontSize: 24, bold: true, color: C.white, lineSpacing: 1.08 });
    text(s, "22 SLIDES / EDITABLE PPTX", 760, 632, 360, 20, { fontSize: 13, bold: true, color: C.yellow });
    notes(s, "表紙は背景画像を全面に残しながら、前景に紙の教材カバーを置いてタイトルの可読性を担保します。物語の入口は『AIで速く作る』ではなく『判断を動かす資料を設計する』です。", [SRC.anthropic, SRC.generated]);
  }

  // 02 — Promise
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    frame(s, 2, "WHY", true);
    text(s, "目標は、\n作成時間を半分にすることではない。", 66, 112, 760, 130, { fontSize: 50, bold: true, color: C.white, lineSpacing: 0.98 });
    text(s, "相手が「何を決めればいいか」を、\n一度で理解できる資料にすること。", 70, 296, 680, 74, { fontSize: 24, color: "#C9CDD2", lineSpacing: 1.12 });
    text(s, "SPEED", 862, 128, 280, 46, { fontSize: 34, bold: true, color: "#5A5E64" });
    text(s, "≠", 906, 214, 180, 94, { fontSize: 76, bold: true, color: C.red, alignment: "center" });
    text(s, "QUALITY", 830, 344, 340, 54, { fontSize: 42, bold: true, color: C.white, alignment: "center" });
    rule(s, 70, 544, 1080, "#3A3D42", 2);
    text(s, "この資料では、構成 → 1枚の主張 → 視覚化 → 検査の順に作ります。", 70, 580, 910, 28, { fontSize: 20, bold: true, color: C.yellow });
    notes(s, "生成速度と資料品質を分け、教材全体のゴールを『判断が進むこと』に置きます。", [SRC.anthropic, SRC.academic]);
  }

  // 03 — Problem
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    img(s, IMG.problem, 0, 0, W, H, "似たようなAI生成スライドの壁を前に迷う人物");
    shape(s, "rect", 0, 0, W, H, { color: C.ink, transparency: 50 });
    frame(s, 3, "PROBLEM", true);
    paperMock(s, 66, 104, 574, 400, C.yellow, "AIは、空白を\n埋めるのがうまい。", "しかし、何を捨てるかは決めてくれない。", false);
    browserMock(s, 742, 236, 430, 258, "AI SLIDE GENERATOR / DRAFT 01", true);
    text(s, "同じ型のページが\n増えていく", 780, 320, 320, 68, { fontSize: 30, bold: true, color: C.white, lineSpacing: 1.02 });
    text(s, "RESULT", 66, 556, 120, 22, { fontSize: 13, bold: true, color: C.red });
    text(s, "似た見た目・多すぎる情報・弱い結論。", 66, 592, 610, 30, { fontSize: 22, bold: true, color: C.white });
    notes(s, "問題提起は、背景画像の人物を『AIに任せた結果、似た画面が増える担当者』として扱います。画面モックを前景に置き、何が起きているかを文字だけに頼らず見せます。", [SRC.anthropic, SRC.generated]);
  }

  // 04 — Failure modes
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 4, "DIAGNOSE");
    bigTitle(s, "AI資料が弱くなる原因は、3つしかない。", 92, 1040, false, 46);
    const rows = [
      ["01", "目的が広い", "「分かりやすく」だけで、誰の何を変えるかがない。", C.red],
      ["02", "主張が薄い", "タイトルが話題名で、読み手が得る結論になっていない。", C.blue],
      ["03", "検査がない", "生成した瞬間を完成とし、全ページを画像で見直していない。", C.yellow],
    ];
    rows.forEach(([num, head, body, color], i) => {
      const y = 278 + i * 112;
      text(s, num, 74, y, 78, 44, { fontSize: 32, bold: true, color });
      text(s, head, 182, y + 2, 260, 36, { fontSize: 27, bold: true });
      text(s, body, 476, y + 4, 690, 48, { fontSize: 18, color: C.gray, lineSpacing: 1.15 });
      rule(s, 182, y + 72, 984, C.light, 1);
    });
    text(s, "つまり、プロンプトより先に“判断の型”が必要です。", 182, 626, 820, 30, { fontSize: 22, bold: true });
    notes(s, "海外スキルに共通する失敗パターンを、目的・主張・QAの3つに整理しています。", [SRC.anthropic, SRC.layouts, SRC.academic]);
  }

  // 05 — Reframe
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    frame(s, 5, "REFRAME");
    text(s, "プレゼンは、ページ制作ではない。", 66, 108, 860, 68, { fontSize: 48, bold: true });
    text(s, "意思決定の設計である。", 66, 196, 760, 72, { fontSize: 54, bold: true, color: C.red });
    const x0 = 92;
    const y0 = 378;
    ["理解する", "比較する", "信じる", "動く"].forEach((label, i) => {
      const x = x0 + i * 276;
      if (i < 3) {
        rule(s, x + 152, y0 + 42, 112, C.ink, 3);
        shape(s, "triangle", x + 252, y0 + 32, 22, 22, C.ink);
      }
      dot(s, x, y0, 86, [C.paleRed, C.paleBlue, C.paleYellow, C.ink][i]);
      text(s, String(i + 1), x + 24, y0 + 28, 38, 24, { fontSize: 17, bold: true, color: i === 3 ? C.white : C.ink, alignment: "center" });
      text(s, label, x - 16, y0 + 112, 120, 28, { fontSize: 20, bold: true, alignment: "center" });
    });
    text(s, "スライドは、この順番を支える“画面”にすぎません。", 66, 592, 780, 30, { fontSize: 22, bold: true, color: C.gray });
    notes(s, "プレゼンを画面装飾ではなく、相手の認知と行動を順に進める設計として定義します。", [SRC.academic]);
  }

  // 06 — Four layers
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    frame(s, 6, "MODEL", true);
    text(s, "良質な資料は、4層でできている。", 66, 94, 800, 66, { fontSize: 47, bold: true, color: C.white });
    text(s, "下から順に固める。デザインは3番目。", 70, 172, 620, 30, { fontSize: 20, color: "#B9BDC2" });
    const layers = [
      ["01", "STORY", "相手の判断が進む順番", 940, C.red],
      ["02", "MESSAGE", "1枚で言うこと", 780, C.blue],
      ["03", "VISUAL", "主張に合う見せ方", 620, C.yellow],
      ["04", "QA", "最終検査", 460, C.white],
    ];
    layers.forEach(([num, head, body, width, color], i) => {
      const y = 302 + i * 76;
      const x = 66 + (980 - width) / 2;
      shape(s, "rect", x, y, width, 58, i === 3 ? C.white : "#2E3136", color, 2);
      text(s, num, x + 22, y + 16, 52, 24, { fontSize: 15, bold: true, color: i === 3 ? C.ink : color });
      text(s, head, x + 86, y + 13, 180, 28, { fontSize: 22, bold: true, color: i === 3 ? C.ink : C.white });
      text(s, body, x + 310, y + 17, width - 340, 24, { fontSize: 17, color: i === 3 ? C.gray : "#BFC3C7" });
    });
    notes(s, "構成、主張、視覚化、QAを別工程にすることで、AIが一度に全部を平均化する問題を防ぎます。", [SRC.anthropic, SRC.fluid, SRC.layouts]);
  }

  // 07 — Brief
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 7, "01 BRIEF");
    text(s, "最初の10分で、4つを決める。", 66, 94, 820, 62, { fontSize: 46, bold: true });
    text(s, "AIに渡す前に、人が答える質問です。", 70, 170, 680, 30, { fontSize: 20, color: C.gray });
    const items = [
      ["WHO", "誰が読む？", "役職・知識・不安", C.red],
      ["DECISION", "何を決める？", "会議後の選択", C.blue],
      ["PROOF", "何で信じる？", "数字・実例・比較", C.yellow],
      ["ACTION", "次に何をする？", "承認・返信・予約", C.ink],
    ];
    items.forEach(([tag, q, hint, color], i) => {
      const x = 66 + i * 290;
      const y = 304 + (i % 2) * 42;
      text(s, tag, x, y, 120, 20, { fontSize: 13, bold: true, color });
      text(s, q, x, y + 38, 240, 34, { fontSize: 26, bold: true });
      text(s, hint, x, y + 88, 230, 26, { fontSize: 17, color: C.gray });
      dot(s, x, y + 148, 18, color);
      rule(s, x + 32, y + 156, 194, color, 2);
    });
    shape(s, "rect", 66, 586, 1136, 58, C.ink);
    text(s, "1文で言う：この資料は［誰］が［何］を決めるためのもの。", 94, 603, 1060, 26, { fontSize: 20, bold: true, color: C.white });
    notes(s, "用途・読者・判断・証拠・次の行動を明示するプレゼンブリーフです。", [SRC.openai, SRC.academic]);
  }

  // 08 — Storyline
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    img(s, IMG.structure, 0, 0, W, H, "散らかった情報が構造を通って明快な三枚の資料へ変わるビジュアル");
    shape(s, "rect", 0, 0, W, H, { color: C.white, transparency: 60 });
    frame(s, 8, "02 STORY");
    paperMock(s, 56, 92, 600, 230, C.blue, "情報を並べず、\n物語の“圧力”をつくる。", "", false);
    text(s, "現状 → 問題 → 転換 → 根拠 → 行動", 92, 270, 520, 26, { fontSize: 18, bold: true, color: C.blue });
    const board = browserMock(s, 696, 304, 510, 276, "GHOST DECK / STORYBOARD", false);
    text(s, "SITUATION", 732, 388, 130, 18, { fontSize: 12, bold: true, color: C.red });
    text(s, "現状", 732, 420, 100, 26, { fontSize: 24, bold: true });
    text(s, "COMPLICATION", 892, 388, 160, 18, { fontSize: 12, bold: true, color: C.yellow });
    text(s, "問題", 892, 420, 100, 26, { fontSize: 24, bold: true });
    text(s, "RESOLUTION", 1052, 388, 130, 18, { fontSize: 12, bold: true, color: C.blue });
    text(s, "転換", 1052, 420, 100, 26, { fontSize: 24, bold: true });
    rule(s, 824, 430, 46, C.ink, 2);
    rule(s, 984, 430, 46, C.ink, 2);
    text(s, "タイトルだけを読んでも、話が通るか。", 66, 612, 700, 30, { fontSize: 22, bold: true });
    notes(s, "Situation・Complication・Resolutionを使い、各ページタイトルだけで筋が通る『ghost deck』を作ります。背景は情報が構造化される過程、前景はその設計図として役割を分けています。", [SRC.academic, SRC.generated]);
  }

  // 09 — Action titles
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 9, "03 MESSAGE");
    bigTitle(s, "タイトルは“話題”ではなく、“結論”を書く。", 88, 1070, false, 45);
    shape(s, "rect", 66, 276, 500, 258, C.white, C.light, 1);
    text(s, "TOPIC TITLE", 94, 302, 180, 22, { fontSize: 13, bold: true, color: C.gray });
    text(s, "AI導入について", 94, 364, 390, 42, { fontSize: 31, bold: true });
    text(s, "読み手は、本文を読むまで\n何が言いたいか分からない。", 94, 438, 400, 54, { fontSize: 18, color: C.gray, lineSpacing: 1.14 });
    text(s, "→", 584, 368, 80, 70, { fontSize: 56, bold: true, color: C.red, alignment: "center" });
    shape(s, "rect", 682, 250, 520, 308, C.ink);
    text(s, "ACTION TITLE", 714, 282, 190, 22, { fontSize: 13, bold: true, color: C.yellow });
    text(s, "最初は3業務に絞ると、\nAI導入は定着しやすい。", 714, 342, 446, 80, { fontSize: 32, bold: true, color: C.white, lineSpacing: 1.04 });
    text(s, "タイトルだけで、\n次に何を考えるかが分かる。", 714, 466, 410, 56, { fontSize: 18, color: "#C8CCD1", lineSpacing: 1.14 });
    text(s, "全タイトルを縦に並べ、1本の文章として読めるか確認する。", 66, 612, 960, 30, { fontSize: 21, bold: true, color: C.blue });
    notes(s, "タイトルを完全な結論文にし、タイトルだけで論理が追えるか検査します。", [SRC.academic]);
  }

  // 10 — One message
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    frame(s, 10, "03 MESSAGE", true);
    text(s, "1枚に、1つの主張。", 66, 96, 720, 66, { fontSize: 50, bold: true, color: C.white });
    text(s, "情報量ではなく、視線の行き先を1つにする。", 70, 176, 720, 30, { fontSize: 20, color: "#BFC3C7" });
    // Left: crowded
    shape(s, "rect", 66, 278, 468, 296, "#2B2E33", "#4A4E54", 1);
    text(s, "× 3つ言いたい", 94, 304, 230, 28, { fontSize: 20, bold: true, color: C.red });
    [0, 1, 2].forEach((i) => {
      miniSlide(s, 96 + i * 120, 374 + (i % 2) * 38, 180, 122, [C.red, C.blue, C.yellow][i], ["市場", "機能", "価格"][i], 3, true);
    });
    // Right: focused
    shape(s, "rect", 620, 250, 582, 354, C.white);
    text(s, "○ 1つだけ伝える", 652, 282, 280, 28, { fontSize: 20, bold: true, color: C.blue });
    text(s, "今月は、\n提案書作成から始める。", 652, 356, 470, 100, { fontSize: 38, bold: true, color: C.ink, lineSpacing: 1.02 });
    dot(s, 1062, 454, 78, C.red);
    text(s, "理由は\n3つ", 1074, 472, 54, 38, { fontSize: 14, bold: true, color: C.white, alignment: "center" });
    text(s, "補足は、話す。載せない。別紙に逃がす。", 652, 532, 450, 28, { fontSize: 18, bold: true, color: C.gray });
    notes(s, "1枚の視覚的焦点を1つに絞り、補足は口頭・別紙・次ページへ分離します。", [SRC.anthropic]);
  }

  // 11 — Visual grammar
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    frame(s, 11, "04 VISUAL");
    bigTitle(s, "主張が決まれば、見せ方は5択になる。", 88, 1040, false, 45);
    const visuals = [
      ["HERO", "一言を残す", "主張", C.red],
      ["CONTRAST", "違いを選ぶ", "比較", C.blue],
      ["PROCESS", "順番を追う", "工程", C.yellow],
      ["EVIDENCE", "根拠を信じる", "証拠", C.ink],
      ["ACTION", "次へ進む", "行動", C.red],
    ];
    visuals.forEach(([tag, use, jp, color], i) => {
      const x = 66 + i * 224;
      const y = 304 + (i % 2) * 34;
      text(s, tag, x, y, 180, 22, { fontSize: 12, bold: true, color });
      if (i === 0) {
        text(s, "A", x, y + 54, 100, 90, { fontSize: 76, bold: true, color });
      } else if (i === 1) {
        shape(s, "rect", x, y + 56, 64, 80, C.paleBlue);
        shape(s, "rect", x + 72, y + 78, 84, 58, C.blue);
      } else if (i === 2) {
        [0, 1, 2].forEach((j) => {
          dot(s, x + j * 54, y + 74, 28, j === 1 ? C.yellow : C.paleYellow);
          if (j < 2) rule(s, x + 28 + j * 54, y + 87, 26, C.ink, 2);
        });
      } else if (i === 3) {
        [50, 84, 118].forEach((h, j) => shape(s, "rect", x + j * 44, y + 152 - h, 26, h, j === 2 ? C.ink : "#B7BBC0"));
      } else {
        shape(s, "rightArrow", x, y + 68, 154, 60, C.red);
      }
      text(s, jp, x, y + 174, 180, 30, { fontSize: 22, bold: true });
      text(s, use, x, y + 214, 180, 28, { fontSize: 16, color: C.gray });
    });
    text(s, "箇条書きは、他の4つが合わない時だけ使う。", 66, 620, 760, 28, { fontSize: 21, bold: true, color: C.red });
    notes(s, "内容の意味に応じて、hero・comparison・process・evidence・actionを選び、箇条書きを最後の手段にします。", [SRC.layouts, SRC.anthropic]);
  }

  // 12 — Density
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 12, "05 EDIT");
    text(s, "装飾する前に、削る。", 66, 94, 720, 66, { fontSize: 50, bold: true });
    text(s, "良いデザインは、情報の優先順位が見える状態です。", 70, 174, 740, 30, { fontSize: 20, color: C.gray });
    miniSlide(s, 82, 286, 436, 264, C.red, "AI導入の全体像", 8, false);
    text(s, "BEFORE", 82, 570, 120, 22, { fontSize: 13, bold: true, color: C.gray });
    text(s, "全部を1枚に載せる", 82, 600, 340, 28, { fontSize: 20, bold: true });
    text(s, "−", 566, 376, 92, 74, { fontSize: 64, bold: true, color: C.red, alignment: "center" });
    shape(s, "rect", 704, 256, 498, 324, C.white, C.ink, 2);
    text(s, "今月、\nどこから始める？", 742, 306, 390, 86, { fontSize: 36, bold: true, lineSpacing: 1.02 });
    shape(s, "rect", 742, 444, 286, 18, C.blue);
    text(s, "提案書作成", 742, 486, 260, 38, { fontSize: 28, bold: true, color: C.blue });
    text(s, "AFTER", 704, 600, 120, 22, { fontSize: 13, bold: true, color: C.gray });
    text(s, "判断に必要な1点だけ残す", 824, 600, 360, 28, { fontSize: 20, bold: true });
    notes(s, "文字を小さくするのではなく、主張に不要な情報を削除・分割・別紙化します。", [SRC.anthropic]);
  }

  // 13 — Evidence
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    frame(s, 13, "06 EVIDENCE", true);
    text(s, "根拠は、数字を置くだけでは伝わらない。", 66, 94, 900, 66, { fontSize: 46, bold: true, color: C.white });
    text(s, "主張 → 証拠 → 意味、まで1セットにする。", 70, 172, 760, 30, { fontSize: 21, color: C.yellow, bold: true });
    const parts = [
      ["CLAIM", "提案書作成から\n始めるべき", C.red],
      ["EVIDENCE", "週8時間を消費\n修正回数が多い", C.blue],
      ["IMPLICATION", "効果が見えやすく\n定着の入口になる", C.yellow],
    ];
    parts.forEach(([tag, body, color], i) => {
      const x = 66 + i * 382;
      if (i < 2) {
        rule(s, x + 300, 404, 66, "#73777C", 2);
        shape(s, "triangle", x + 354, 394, 22, 22, "#73777C");
      }
      dot(s, x, 310, 72, color);
      text(s, String(i + 1), x + 24, 334, 24, 20, { fontSize: 16, bold: true, color: i === 1 ? C.white : C.ink, alignment: "center" });
      text(s, tag, x, 406, 240, 22, { fontSize: 13, bold: true, color });
      text(s, body, x, 454, 280, 74, { fontSize: 24, bold: true, color: C.white, lineSpacing: 1.08 });
    });
    text(s, "出典と“要確認”は、最後ではなく生成時に付ける。", 66, 612, 850, 30, { fontSize: 21, bold: true, color: "#C6CAD0" });
    notes(s, "証拠を列挙せず、主張を支える証拠と、その意味を同じページでつなぎます。", [SRC.academic]);
  }

  // 14 — Design system
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    frame(s, 14, "07 SYSTEM");
    bigTitle(s, "毎回ゼロからデザインしない。", 90, 920, false, 46);
    text(s, "AIに渡すのは、テンプレではなく“選択ルール”。", 70, 174, 760, 30, { fontSize: 21, color: C.gray });
    // Palette
    text(s, "COLOR", 70, 286, 160, 22, { fontSize: 13, bold: true, color: C.gray });
    [C.ink, C.white, C.red, C.blue, C.yellow].forEach((color, i) => {
      shape(s, "rect", 70 + i * 76, 332, 58, 106, color, i === 1 ? C.light : "none", i === 1 ? 1 : 0);
    });
    text(s, "1色を主役に、\n強調色は1ページ1つ。", 70, 474, 360, 54, { fontSize: 19, bold: true, lineSpacing: 1.14 });
    // Type
    text(s, "TYPE", 488, 286, 160, 22, { fontSize: 13, bold: true, color: C.gray });
    text(s, "Aa", 488, 324, 150, 78, { fontSize: 66, bold: true });
    text(s, "結論は大きく。\n説明は短く。", 488, 426, 260, 62, { fontSize: 22, bold: true, lineSpacing: 1.14 });
    // Layout
    text(s, "LAYOUT", 812, 286, 160, 22, { fontSize: 13, bold: true, color: C.gray });
    miniSlide(s, 812, 330, 170, 112, C.red, "HERO", 1);
    miniSlide(s, 1000, 330, 170, 112, C.blue, "COMPARE", 2);
    miniSlide(s, 906, 466, 170, 112, C.yellow, "PROCESS", 3);
    text(s, "型を変え、ルールは変えない。", 812, 608, 360, 28, { fontSize: 20, bold: true });
    notes(s, "配色の支配関係、文字階層、内容に応じたレイアウト型をデザインシステムとして固定します。", [SRC.anthropic, SRC.layouts]);
  }

  // 15 — Prompt stack
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 15, "PROMPT SYSTEM");
    text(s, "AIへの指示は、3段階に分ける。", 66, 92, 820, 66, { fontSize: 47, bold: true });
    text(s, "一発生成より、判断の順番を守る方が強い。", 70, 172, 720, 30, { fontSize: 21, color: C.gray });
    const stages = [
      ["01", "BRIEF", "相手と目的を固定", C.red],
      ["02", "GHOST DECK", "タイトルだけで物語を作る", C.blue],
      ["03", "SLIDE SPEC", "1枚ごとの見せ方を決める", C.yellow],
    ];
    stages.forEach(([num, head, body, color], i) => {
      const x = 66 + i * 382;
      const y = 306 + i * 34;
      shape(s, "rect", x, y, 330, 210, i === 2 ? C.ink : C.white, C.light, 1);
      text(s, num, x + 24, y + 24, 52, 24, { fontSize: 15, bold: true, color });
      text(s, head, x + 24, y + 70, 270, 32, { fontSize: 25, bold: true, color: i === 2 ? C.white : C.ink });
      text(s, body, x + 24, y + 124, 276, 48, { fontSize: 17, color: i === 2 ? "#C8CCD1" : C.gray, lineSpacing: 1.12 });
      if (i < 2) text(s, "→", x + 338, y + 82, 38, 38, { fontSize: 30, bold: true, color: C.gray, alignment: "center" });
    });
    text(s, "各段階で人が承認してから、次へ進む。", 66, 616, 700, 30, { fontSize: 21, bold: true, color: C.red });
    notes(s, "ブリーフ、ghost deck、slide specを分離し、各工程でレビューするプロンプト設計です。", [SRC.openai, SRC.fluid, SRC.academic]);
  }

  // 16 — Brief prompt
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    frame(s, 16, "PROMPT 01", true);
    text(s, "まず、資料の設計条件だけを作らせる。", 66, 92, 920, 62, { fontSize: 44, bold: true, color: C.white });
    shape(s, "rect", 66, 214, 1136, 364, "#2A2D31", "#4B4F55", 1);
    text(s, "COPY & PASTE", 94, 242, 180, 22, { fontSize: 13, bold: true, color: C.yellow });
    text(s,
      "あなたは経営者向けプレゼンの編集者です。\n" +
      "以下の素材から、スライド本文は作らず、まず設計ブリーフだけを作成してください。\n\n" +
      "1. 読み手：役職、前提知識、不安\n" +
      "2. 決めてほしいこと：会議後の具体的な選択\n" +
      "3. 信じるための根拠：数字、実例、比較\n" +
      "4. 次の行動：承認、返信、予約\n" +
      "5. 使わない情報：今回の判断に不要な素材",
      94, 290, 1040, 238,
      { fontSize: 19, color: C.white, lineSpacing: 1.18 }
    );
    text(s, "入力：目的 / 読み手 / 手持ち素材 / 制約 / 希望ページ数", 94, 542, 950, 24, { fontSize: 16, bold: true, color: "#BFC3C7" });
    text(s, "出力を見て、人が“決めてほしいこと”を修正する。", 66, 612, 820, 30, { fontSize: 21, bold: true, color: C.yellow });
    notes(s, "最初のプロンプトではスライドを作らせず、用途と判断条件だけを固定します。", [SRC.openai]);
  }

  // 17 — Ghost deck prompt
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    frame(s, 17, "PROMPT 02");
    text(s, "次に、タイトルだけで物語を作らせる。", 66, 92, 920, 62, { fontSize: 44, bold: true });
    shape(s, "rect", 66, 214, 694, 374, C.paper, C.light, 1);
    text(s, "COPY & PASTE", 94, 242, 180, 22, { fontSize: 13, bold: true, color: C.blue });
    text(s,
      "先ほどの設計ブリーフを使い、全ページのタイトルだけを作ってください。\n\n" +
      "条件：\n" +
      "・各タイトルは話題名ではなく、完全な結論文\n" +
      "・タイトルだけを順に読んで、問題→原因→解決→行動が通る\n" +
      "・同じ内容を繰り返さない\n" +
      "・各タイトルは1〜2行に収める\n\n" +
      "最後に、タイトルだけを読んだ時の論理の飛躍を指摘してください。",
      94, 290, 620, 250,
      { fontSize: 18, lineSpacing: 1.18 }
    );
    const titles = [
      "現状：資料は速く作れる",
      "問題：判断は進んでいない",
      "原因：主張が決まっていない",
      "解決：先に物語を設計する",
      "行動：1本で試して検証する",
    ];
    titles.forEach((t, i) => {
      text(s, String(i + 1).padStart(2, "0"), 822, 250 + i * 72, 40, 22, { fontSize: 13, bold: true, color: [C.red, C.red, C.yellow, C.blue, C.ink][i] });
      text(s, t, 878, 246 + i * 72, 300, 38, { fontSize: 19, bold: true });
      if (i < 4) rule(s, 878, 294 + i * 72, 296, C.light, 1);
    });
    notes(s, "タイトルだけで論理が通るかを確認するghost deckテストを、そのまま使えるプロンプトにしています。", [SRC.academic]);
  }

  // 18 — Slide spec prompt
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 18, "PROMPT 03");
    text(s, "最後に、1枚ごとの“設計図”を作らせる。", 66, 92, 960, 62, { fontSize: 44, bold: true });
    text(s, "PowerPointを作る前に、ここまで決めます。", 70, 168, 720, 30, { fontSize: 20, color: C.gray });
    shape(s, "rect", 66, 244, 1136, 326, C.white, C.light, 1);
    const specs = [
      ["ACTION TITLE", "このページの結論"],
      ["PROOF", "結論を支える根拠"],
      ["VISUAL TYPE", "hero / contrast / process / evidence / action"],
      ["LAYOUT", "視線の流れと余白"],
      ["SOURCE", "出典・要確認"],
      ["SPEAKER NOTE", "口頭で補う内容"],
    ];
    specs.forEach(([label, value], i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 96 + col * 548;
      const y = 274 + row * 88;
      text(s, label, x, y, 180, 20, { fontSize: 12, bold: true, color: [C.red, C.blue, C.yellow][row] });
      text(s, value, x + 188, y - 2, 330, 30, { fontSize: 18, bold: true });
      rule(s, x, y + 46, 500, C.light, 1);
    });
    shape(s, "rect", 66, 606, 1136, 38, C.blue);
    text(s, "AIには「タイトル＋本文」ではなく「主張＋根拠＋見せ方」を渡す。", 92, 614, 1080, 24, { fontSize: 18, bold: true, color: C.white });
    notes(s, "スライド本文より前に、主張・根拠・視覚タイプ・レイアウト・出典・話者ノートを定義します。", [SRC.layouts, SRC.academic]);
  }

  // 19 — Workflow + roles
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    frame(s, 19, "WORKFLOW", true);
    text(s, "AIと人の仕事を、交互にする。", 66, 92, 820, 62, { fontSize: 47, bold: true, color: C.white });
    text(s, "一括生成ではなく、判断 → 展開 → 判断のリズム。", 70, 170, 780, 30, { fontSize: 20, color: "#BDC1C6" });
    const flow = [
      ["人", "目的を決める", C.red],
      ["AI", "構成案を出す", C.blue],
      ["人", "主張を選ぶ", C.red],
      ["AI", "視覚案を出す", C.blue],
      ["人", "全ページを検査", C.yellow],
    ];
    flow.forEach(([who, task, color], i) => {
      const x = 66 + i * 224;
      const y = 310 + (i % 2) * 72;
      dot(s, x, y, 74, color);
      text(s, who, x + 18, y + 24, 38, 24, { fontSize: 18, bold: true, color: who === "AI" ? C.white : C.ink, alignment: "center" });
      text(s, task, x - 18, y + 102, 150, 48, { fontSize: 18, bold: true, color: C.white, alignment: "center" });
      if (i < 4) {
        rule(s, x + 82, y + 36, 118, "#62666C", 2);
        shape(s, "triangle", x + 188, y + 26, 22, 22, "#62666C");
      }
    });
    text(s, "人：意味と責任を持つ　　AI：選択肢と速度を増やす", 66, 600, 900, 32, { fontSize: 22, bold: true, color: C.yellow });
    notes(s, "AIに選択肢を広げさせ、人が目的・主張・公開可否を承認する分担です。", [SRC.fluid, SRC.openai]);
  }

  // 20 — QA
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    frame(s, 20, "FINAL QA");
    text(s, "完成条件は、“生成できた”ではない。", 66, 92, 940, 62, { fontSize: 45, bold: true });
    text(s, "全ページを画像で見て、5項目を通す。", 70, 170, 720, 30, { fontSize: 21, color: C.red, bold: true });
    const checks = [
      ["01", "STORY", "タイトルだけで話が通る"],
      ["02", "FOCUS", "1枚に主張が1つ"],
      ["03", "FIT", "文字切れ・重なりがない"],
      ["04", "PROOF", "数字・画像・出典を確認"],
      ["05", "ACCESS", "色だけに頼らず読みやすい"],
    ];
    checks.forEach(([num, head, body], i) => {
      const x = 66 + (i % 3) * 378;
      const y = 280 + Math.floor(i / 3) * 142;
      dot(s, x, y, 58, [C.red, C.blue, C.yellow, C.ink, C.red][i]);
      text(s, num, x + 17, y + 19, 24, 20, { fontSize: 13, bold: true, color: i === 1 || i === 3 ? C.white : C.ink, alignment: "center" });
      text(s, head, x + 82, y + 2, 190, 28, { fontSize: 23, bold: true });
      text(s, body, x + 82, y + 44, 250, 44, { fontSize: 17, color: C.gray, lineSpacing: 1.12 });
      rule(s, x + 82, y + 104, 250, C.light, 1);
    });
    shape(s, "rect", 822, 472, 380, 132, C.ink);
    text(s, "最後に見るもの", 850, 494, 190, 22, { fontSize: 13, bold: true, color: C.yellow });
    text(s, "スライド一覧\n→ 各ページを100%表示", 850, 532, 310, 54, { fontSize: 22, bold: true, color: C.white, lineSpacing: 1.12 });
    notes(s, "全ページのレンダー、個別表示、オーバーフロー検査、出典確認、アクセシビリティ確認を完成条件にします。", [SRC.anthropic, SRC.microsoft, SRC.fluid]);
  }

  // 21 — Master prompt
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    frame(s, 21, "MASTER PROMPT");
    text(s, "この1文から、制作を始められる。", 66, 88, 900, 62, { fontSize: 46, bold: true });
    shape(s, "rect", 66, 190, 1136, 402, C.ink);
    text(s, "AI PRESENTATION MASTER PROMPT", 94, 218, 440, 22, { fontSize: 13, bold: true, color: C.yellow });
    text(s,
      "あなたは、意思決定を設計するプレゼン編集者です。次の順番を飛ばさず進めてください。\n\n" +
      "① 読み手・決定・根拠・次の行動を確認する\n" +
      "② タイトルだけで全体の物語を作る\n" +
      "③ 各ページを1主張に絞る\n" +
      "④ 主張に合う visual type を選ぶ\n" +
      "⑤ 各ページの出典と要確認項目を示す\n" +
      "⑥ 全ページを画像で検査し、重なり・文字切れ・単調な反復を修正する\n\n" +
      "不足情報は勝手に埋めず、仮定として明示してください。",
      94, 268, 1040, 246,
      { fontSize: 18, color: C.white, lineSpacing: 1.14 }
    );
    text(s, "入力欄：目的 / 読み手 / 素材 / 制約 / 希望ページ数 / デザイン方向", 94, 544, 1040, 24, { fontSize: 16, bold: true, color: "#C8CCD1" });
    text(s, "重要：初稿を完成扱いしない。", 66, 624, 620, 28, { fontSize: 21, bold: true, color: C.red });
    notes(s, "教材の要点を一つの実務プロンプトに集約し、各工程を飛ばさない制約を入れています。", [SRC.openai, SRC.anthropic, SRC.academic, SRC.layouts]);
  }

  // 22 — CTA
  {
    const s = deck.slides.add();
    s.background.fill = C.ink;
    img(s, IMG.cta, 0, 0, W, H, "プレゼン検討後の上質な経営会議テーブル");
    shape(s, "rect", 0, 0, W, H, { color: C.ink, transparency: 44 });
    frame(s, 22, "NEXT", true);
    paperMock(s, 66, 88, 560, 556, C.red, "まず1本、\n自社資料で試す。", "", false);
    text(s, "汎用ノウハウを、自社の営業・採用・会議資料に\n移すところまで一緒に設計します。", 98, 274, 470, 52, { fontSize: 17, color: C.gray, lineSpacing: 1.12 });
    shape(s, "rect", 98, 376, 238, 44, C.yellow);
    text(s, "無料顧問1回分", 118, 386, 198, 26, { fontSize: 23, bold: true, color: C.ink, alignment: "center" });
    const ctas = ["資料の目的を1つに絞る", "最初のghost deckを作る", "AIに任せる範囲を決める"];
    ctas.forEach((item, i) => {
      dot(s, 104, 462 + i * 42, 18, [C.red, C.blue, C.yellow][i]);
      text(s, item, 138, 460 + i * 42, 410, 24, { fontSize: 17, bold: true, color: C.ink });
    });
    shape(s, "roundRect", 98, 588, 404, 42, C.ink);
    text(s, "自社資料を1本、持ってくる", 122, 600, 356, 20, { fontSize: 16, bold: true, color: C.white, alignment: "center" });
    text(s, "資料は、会議の前に始まっている。", 760, 570, 390, 30, { fontSize: 22, bold: true, color: C.white });
    notes(s, "最後は抽象的な相談ではなく、実物の自社資料を1本持ち込む具体的な次の行動を提示します。背景の会議テーブルは未来の実行場面、前景の紙面はその場へ持ち込む最初の一歩です。", [SRC.generated]);
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(`${OUT_DIR}/${stem}.png`, await deck.export({ slide, format: "png", scale: 1 }));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(`${OUT_DIR}/${stem}.layout.json`, await layout.text());
  }
  await writeBlob(`${OUT_DIR}/deck-montage.webp`, await deck.export({ format: "webp", montage: true, scale: 1 }));
  const inspected = await deck.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 50000 });
  await fs.writeFile(`${OUT_DIR}/inspect.ndjson`, inspected.ndjson ?? "");
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL_PPTX);
  console.log(JSON.stringify({ finalPptx: FINAL_PPTX, slideCount: deck.slides.items.length, outputDir: OUT_DIR }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
