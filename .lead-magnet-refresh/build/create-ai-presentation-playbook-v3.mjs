import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT_DIR = "/Users/koki/Desktop/ai-komon2/.lead-magnet-refresh/build/output-v3";
const FINAL_PPTX = "/Users/koki/Desktop/ai-komon2/materials/ai-komon-ai-presentation-playbook-v2.pptx";
const IMG_PAIN = "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-1be79562-7a12-4238-9b89-c1cfaad58ab8.png";
const IMG_PATH = "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-c8c65556-97b8-4e22-b4b1-b183a0005d44.png";
const IMG_CALM = "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-dbaff0df-551a-49fe-bb21-1d29ac469299.png";

const W = 1280;
const H = 720;
const C = {
  black: "#111111",
  charcoal: "#232526",
  white: "#FFFFFF",
  paper: "#FAFAF7",
  gray: "#686C70",
  line: "#D9D9D4",
  yellow: "#F4D84D",
  blue: "#8ED7F0",
  coral: "#FF8B7B",
  paleBlue: "#EAF7FB",
  paleYellow: "#FFF8D1",
  paleCoral: "#FFF0ED",
};

function addShape(slide, geometry, left, top, width, height, fill = "none", lineFill = "none", lineWidth = 0) {
  return slide.shapes.add({
    geometry,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
  });
}

function addText(slide, value, left, top, width, height, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    typeface: "Arial",
    fontSize: 20,
    color: C.black,
    verticalAlignment: "top",
    wrap: "square",
    autoFit: "shrinkText",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
    ...style,
  };
  return shape;
}

function circle(slide, left, top, size, fill, lineFill = "none", lineWidth = 0) {
  return addShape(slide, "ellipse", left, top, size, size, fill, lineFill, lineWidth);
}

function line(slide, left, top, width, fill = C.line, height = 2) {
  return addShape(slide, "rect", left, top, width, height, fill);
}

function image(slide, path, left, top, width, height, alt, fit = "cover") {
  return slide.images.add({
    blob: new Uint8Array(readFileSync(path)),
    contentType: "image/png",
    alt,
    fit,
    position: { left, top, width, height },
    geometry: "rect",
  });
}

function header(slide, page, stage, dark = false, active = 0) {
  const ink = dark ? C.white : C.black;
  const muted = dark ? "#A5A8A8" : C.gray;
  addText(slide, "AI顧問室", 72, 30, 140, 20, { fontSize: 14, bold: true, color: ink });
  addText(slide, stage, 220, 31, 240, 18, { fontSize: 12, bold: true, color: muted });
  addText(slide, String(page).padStart(2, "0"), 1160, 30, 48, 20, { fontSize: 13, bold: true, color: muted, alignment: "right" });
  const colors = dark ? ["#4B4D4E", "#4B4D4E", "#4B4D4E", "#4B4D4E"] : [C.line, C.line, C.line, C.line];
  colors[active] = dark ? C.yellow : C.black;
  colors.forEach((color, i) => addShape(slide, "rect", 72 + i * 22, 676, i === active ? 16 : 8, 3, color));
}

function notes(slide, text, sources = []) {
  const sourceLines = sources.map((s) => `- ${s}`).join("\n");
  slide.speakerNotes.textFrame.setText(`${text}\n\n[Sources]\n${sourceLines}\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}

function check(slide, x, y, label, color, dark = false) {
  circle(slide, x, y + 2, 22, color);
  addText(slide, "✓", x + 4, y + 1, 16, 20, { fontSize: 16, bold: true, color: C.black, alignment: "center" });
  addText(slide, label, x + 38, y, 300, 26, { fontSize: 18, color: dark ? C.white : C.black, bold: true });
}

function slideBox(slide, x, y, w, h, accent, heading, body, fill = C.paper) {
  addShape(slide, "rect", x, y, w, h, fill, C.line, 1);
  addShape(slide, "rect", x, y, 10, h, accent);
  addText(slide, heading, x + 28, y + 24, w - 50, 30, { fontSize: 24, bold: true });
  addText(slide, body, x + 28, y + 72, w - 52, h - 92, { fontSize: 16, color: C.gray, lineSpacing: 1.1 });
}

async function writeBlob(path, blob) {
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: W, height: H } });
  const sources = {
    layouts: "https://github.com/tristan-mcinnis/pptx-from-layouts-skill",
    codex: "https://github.com/ningzimu/codex-ppt-skill",
    prompt: "https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices",
    story: "https://www.duarte.com/training/visual-storytelling-training/",
    accessible: "https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities",
    generated: "AI image generation via OpenAI image tool, 2026-07-28",
  };

  // 01: pain hook
  {
    const s = deck.slides.add();
    s.background.fill = C.black;
    image(s, IMG_PAIN, 0, 0, W, H, "散らかった資料に囲まれた経営者のビジュアル");
    addShape(s, "rect", 0, 0, 650, H, C.black);
    header(s, 1, "気づく", true, 0);
    addText(s, "AIを使うほど、\n資料が増える。", 72, 132, 570, 145, { fontSize: 60, bold: true, color: C.white, lineSpacing: 0.96 });
    addText(s, "なのに、会議の判断は進まない。", 78, 316, 430, 32, { fontSize: 23, color: "#D5D7D7" });
    addShape(s, "rect", 78, 420, 220, 6, C.yellow);
    addText(s, "伝わるPowerPointを設計する", 78, 454, 420, 24, { fontSize: 17, bold: true, color: C.yellow });
    notes(s, "最初は情報を説明せず、読者の痛みを一文で言い当てます。", [sources.generated, sources.codex]);
  }

  // 02: identify the problem
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    header(s, 2, "気づく", false, 0);
    addText(s, "その資料は、誰が\n何を決めるためのものですか？", 72, 116, 650, 120, { fontSize: 46, bold: true, lineSpacing: 0.98 });
    addText(s, "ここが言えない資料は、AIに作らせても迷走します。", 76, 270, 650, 28, { fontSize: 19, color: C.gray });
    // visual diagnosis: a blank target with three floating problems
    circle(s, 908, 188, 206, C.yellow);
    addText(s, "目的", 958, 248, 110, 32, { fontSize: 28, bold: true, alignment: "center" });
    addText(s, "？", 965, 298, 94, 70, { fontSize: 62, bold: true, alignment: "center" });
    const tags = [["情報が多い", 794, 426, C.blue], ["結論がない", 1016, 392, C.coral], ["読者が不明", 1046, 520, C.blue]];
    tags.forEach(([label, x, y, color]) => {
      addShape(s, "roundRect", x, y, 150, 44, color, "none", 0);
      addText(s, label, x + 12, y + 12, 126, 20, { fontSize: 15, bold: true, alignment: "center" });
    });
    addText(s, "まず、目的を1つに絞る。", 76, 566, 500, 34, { fontSize: 24, bold: true });
    notes(s, "読者が自分の資料を診断できるよう、問題を目的・情報量・読者の3点に絞って提示します。", [sources.layouts]);
  }

  // 03: amplify the cost
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    header(s, 3, "深める", false, 1);
    addText(s, "1枚の曖昧さが、\n会議全体を長くする。", 72, 110, 620, 106, { fontSize: 48, bold: true, lineSpacing: 0.98 });
    addText(s, "作成 → 修正 → 再説明。\n本来の仕事が、資料の手戻りに置き換わります。", 76, 250, 520, 54, { fontSize: 20, color: C.gray, lineSpacing: 1.12 });
    // large journey arrows / causal chain
    const steps = [["作る", "AIが初稿を出す", C.yellow], ["直す", "主張が揃わない", C.coral], ["説明する", "会議で戻る", C.blue]];
    steps.forEach(([head, body, color], i) => {
      const x = 74 + i * 382;
      if (i > 0) addText(s, "→", x - 60, 404, 50, 44, { fontSize: 42, bold: true, color: C.gray, alignment: "center" });
      circle(s, x, 350, 104, color);
      addText(s, String(i + 1), x + 34, 370, 36, 24, { fontSize: 16, bold: true, alignment: "center" });
      addText(s, head, x + 130, 356, 190, 32, { fontSize: 28, bold: true });
      addText(s, body, x + 130, 402, 200, 28, { fontSize: 16, color: C.gray });
    });
    addShape(s, "rect", 74, 590, 1060, 2, C.line);
    addText(s, "速く作るだけでは、速く進めない。", 74, 616, 760, 34, { fontSize: 24, bold: true });
    notes(s, "生成速度ではなく、手戻りまで含めたカスタマージャーニー上のコストを見せます。", [sources.codex]);
  }

  // 04: worst future
  {
    const s = deck.slides.add();
    s.background.fill = C.charcoal;
    header(s, 4, "深める", true, 1);
    addText(s, "このまま、\n“量産できる迷子”になる。", 72, 116, 640, 118, { fontSize: 50, bold: true, color: C.white, lineSpacing: 0.98 });
    addText(s, "AIが速くするほど、間違った方向への資料だけが増えていく。", 78, 272, 620, 30, { fontSize: 19, color: "#D0D2D2" });
    // visual: funnel into a black hole
    addShape(s, "triangle", 830, 182, 292, 330, C.black);
    circle(s, 918, 426, 120, C.coral);
    addText(s, "手戻り", 942, 468, 72, 24, { fontSize: 18, bold: true, color: C.black, alignment: "center" });
    [0, 1, 2, 3].forEach((i) => {
      const x = 774 + i * 90;
      addShape(s, "rect", x, 152 + i * 44, 78, 42, i % 2 === 0 ? C.yellow : C.blue);
    });
    addText(s, "生成", 786, 586, 100, 24, { fontSize: 18, bold: true, color: C.yellow, alignment: "center" });
    addText(s, "説明", 1012, 586, 100, 24, { fontSize: 18, bold: true, color: C.coral, alignment: "center" });
    notes(s, "最悪の未来を、煽りではなく、量産→迷走→手戻りの因果で見せます。", [sources.codex]);
  }

  // 05: self-diagnosis
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    header(s, 5, "自分ごと化", false, 1);
    addText(s, "あなたの資料、\nこの3つに当てはまりませんか？", 72, 110, 760, 106, { fontSize: 46, bold: true, lineSpacing: 0.98 });
    addText(s, "1つでも当てはまるなら、AI導入の最初の改善点は“作り方”です。", 76, 248, 760, 28, { fontSize: 19, color: C.gray });
    const qs = [
      ["タイトルを読んでも、結論が分からない", C.yellow],
      ["1枚に、言いたいことが3つ以上ある", C.blue],
      ["出典や要確認の数字が、最後に残る", C.coral],
    ];
    qs.forEach(([q, color], i) => {
      const y = 334 + i * 86;
      addShape(s, "rect", 78, y, 12, 48, color);
      addText(s, q, 118, y + 8, 760, 30, { fontSize: 23, bold: true });
      addText(s, "YES?", 1010, y + 8, 120, 28, { fontSize: 18, bold: true, color: color, alignment: "right" });
      line(s, 118, y + 60, 1012, C.line, 1);
    });
    addText(s, "読む人の迷いは、作る人の手戻りになる。", 78, 624, 760, 30, { fontSize: 22, bold: true });
    notes(s, "途中で読者自身の状況を点検させ、次の解決策を読みたくなる接続を作ります。", [sources.story]);
  }

  // 06: best future
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    header(s, 6, "未来を見せる", false, 2);
    image(s, IMG_PATH, 590, 0, 690, H, "散乱した資料から明るい道へ進む抽象ビジュアル");
    addShape(s, "rect", 0, 0, 660, H, C.white);
    addText(s, "資料ができる。\n会議が進む。", 72, 140, 520, 118, { fontSize: 54, bold: true, lineSpacing: 0.98 });
    addText(s, "AIを使う目的は、\nスライドを増やすことではない。\n次の判断を、早くすることです。", 78, 320, 450, 86, { fontSize: 20, color: C.gray, lineSpacing: 1.08 });
    addShape(s, "rect", 78, 462, 214, 6, C.yellow);
    addText(s, "ここから、解決策。", 78, 498, 300, 28, { fontSize: 19, bold: true });
    notes(s, "最悪の未来の反対側に、読み手が欲しい状態を一枚で提示します。", [sources.generated, sources.story]);
  }

  // 07: solution reveal
  {
    const s = deck.slides.add();
    s.background.fill = C.black;
    header(s, 7, "解決策", true, 2);
    addText(s, "AIの前に、\n3つだけ決める。", 72, 110, 650, 108, { fontSize: 50, bold: true, color: C.white, lineSpacing: 0.98 });
    addText(s, "これが決まると、AIは“作業者”として強くなる。", 78, 250, 600, 28, { fontSize: 19, color: "#D0D2D2" });
    const pillars = [["01", "目的", "誰に、何を決めてもらうか", C.yellow], ["02", "結論", "1枚ごとに何を言うか", C.blue], ["03", "検証", "何を確認してから出すか", C.coral]];
    pillars.forEach(([num, head, body, color], i) => {
      const x = 78 + i * 376;
      circle(s, x, 356, 94, color);
      addText(s, num, x + 24, 386, 46, 20, { fontSize: 15, bold: true, alignment: "center" });
      addText(s, head, x + 124, 360, 170, 34, { fontSize: 30, bold: true, color: C.white });
      addText(s, body, x + 124, 410, 196, 36, { fontSize: 16, color: "#D0D2D2" });
    });
    addText(s, "先に人が決める。あとからAIに任せる。", 78, 592, 760, 32, { fontSize: 24, bold: true, color: C.yellow });
    notes(s, "解決策を一度に広げず、目的・結論・検証の3点に絞って提示します。", [sources.prompt, sources.codex]);
  }

  // 08: practical sequence
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    header(s, 8, "解決策", false, 2);
    addText(s, "作る順番を変える。\nそれだけで、手戻りは減る。", 72, 110, 700, 112, { fontSize: 48, bold: true, lineSpacing: 0.98 });
    addText(s, "スライドを描く前に、判断の道筋を置きます。", 76, 254, 650, 28, { fontSize: 19, color: C.gray });
    // staircase / workflow, intentionally non-card layout
    const steps = [["01", "Brief", "目的・相手", C.yellow], ["02", "Outline", "結論の順番", C.blue], ["03", "Visual", "図解の型", C.coral], ["04", "Build", "AIで初稿", C.yellow], ["05", "Check", "根拠と表示", C.blue]];
    steps.forEach(([num, head, body, color], i) => {
      const x = 84 + i * 210;
      const y = 470 - i * 42;
      addShape(s, "rect", x, y, 170, 100, color);
      addText(s, num, x + 16, y + 16, 32, 18, { fontSize: 14, bold: true });
      addText(s, head, x + 16, y + 44, 130, 24, { fontSize: 22, bold: true });
      addText(s, body, x + 16, y + 74, 130, 18, { fontSize: 14, color: C.black });
      if (i < 4) addText(s, "→", x + 174, y + 42, 32, 28, { fontSize: 28, bold: true, color: C.gray, alignment: "center" });
    });
    addText(s, "AIに作らせるのは、4番目。", 84, 604, 600, 30, { fontSize: 22, bold: true });
    notes(s, "制作工程を、作業順ではなく判断順に並べ直しています。", [sources.layouts, sources.codex]);
  }

  // 09: before/after prompt
  {
    const s = deck.slides.add();
    s.background.fill = C.white;
    header(s, 9, "解決策", false, 2);
    addText(s, "“いい感じに”を、\n“この判断をして”に変える。", 72, 108, 720, 110, { fontSize: 46, bold: true, lineSpacing: 0.98 });
    addText(s, "AIの出力を変えるのは、デザイン指定より先にある一文です。", 76, 250, 760, 28, { fontSize: 19, color: C.gray });
    addShape(s, "rect", 76, 340, 420, 190, C.paleCoral);
    addText(s, "NG", 106, 368, 80, 22, { fontSize: 15, bold: true, color: C.coral });
    addText(s, "営業資料を\nいい感じにして。", 106, 418, 330, 70, { fontSize: 29, bold: true, lineSpacing: 1.05 });
    addText(s, "→", 522, 396, 70, 58, { fontSize: 46, bold: true, color: C.yellow, alignment: "center" });
    addShape(s, "rect", 634, 340, 566, 190, C.black);
    addText(s, "OK", 668, 368, 80, 22, { fontSize: 15, bold: true, color: C.yellow });
    addText(s, "経営者が今月の\n営業施策を1つ選べる資料にする。", 668, 412, 470, 68, { fontSize: 27, bold: true, color: C.white, lineSpacing: 1.05 });
    addText(s, "対象 / 結論 / 制約 / 確認事項", 76, 594, 600, 24, { fontSize: 18, bold: true, color: C.gray });
    notes(s, "プロンプトを長くするのではなく、意思決定の条件を具体化する例です。", [sources.prompt]);
  }

  // 10: personalize value
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    header(s, 10, "自社に移す", false, 3);
    addText(s, "自社の資料に移すと、\nまずここが変わる。", 72, 110, 740, 108, { fontSize: 48, bold: true, lineSpacing: 0.98 });
    addText(s, "汎用ノウハウを、そのまま配るだけでは終わりません。", 76, 250, 660, 28, { fontSize: 19, color: C.gray });
    const rows = [["会議", "説明が短くなる", "結論が先に見える", C.yellow], ["提案", "比較がしやすくなる", "相手の判断軸が揃う", C.blue], ["社内", "再利用しやすくなる", "型がチームに残る", C.coral]];
    rows.forEach(([a, b, c, color], i) => {
      const y = 350 + i * 88;
      circle(s, 86, y + 2, 28, color);
      addText(s, a, 136, y, 120, 26, { fontSize: 22, bold: true });
      addText(s, b, 314, y, 260, 26, { fontSize: 20, bold: true });
      addText(s, c, 700, y + 2, 310, 22, { fontSize: 16, color: C.gray });
      line(s, 136, y + 54, 980, C.line, 1);
    });
    addText(s, "だから、最後に必要なのは“自社向けの設計”です。", 86, 626, 880, 30, { fontSize: 22, bold: true });
    notes(s, "無料相談への価値を、抽象的な相談ではなく、自社資料への移植と具体的な変化として提示します。", [sources.story]);
  }

  // 11: CTA bridge
  {
    const s = deck.slides.add();
    s.background.fill = C.black;
    header(s, 11, "申し込む理由", true, 3);
    addText(s, "自社で詰まる場所は、\n会社ごとに違う。", 72, 112, 700, 108, { fontSize: 50, bold: true, color: C.white, lineSpacing: 0.98 });
    addText(s, "だから、まず1本の資料を持ってきてください。", 78, 254, 700, 28, { fontSize: 20, color: "#D0D2D2" });
    const points = [["資料", "何を残し、何を捨てるか", C.yellow], ["業務", "どこまでAIに任せるか", C.blue], ["人", "誰が確認し、使い続けるか", C.coral]];
    points.forEach(([h, b, color], i) => {
      const x = 86 + i * 350;
      circle(s, x, 364, 64, color);
      addText(s, String(i + 1), x + 20, 386, 24, 20, { fontSize: 16, bold: true, alignment: "center" });
      addText(s, h, x + 94, 366, 120, 28, { fontSize: 25, bold: true, color: C.white });
      addText(s, b, x + 94, 410, 210, 28, { fontSize: 16, color: "#D0D2D2" });
    });
    addShape(s, "rect", 86, 566, 520, 3, C.yellow);
    addText(s, "面談で、あなたの“最初の一歩”を決める。", 86, 600, 760, 28, { fontSize: 23, bold: true, color: C.yellow });
    notes(s, "CTA直前で、相談の中身と具体的な持ち込み物を明確にし、申し込みの心理的負担を下げます。", [sources.codex]);
  }

  // 12: CTA
  {
    const s = deck.slides.add();
    s.background.fill = C.yellow;
    image(s, IMG_CALM, 690, 0, 590, H, "整った資料と次の一歩を示すワークテーブル");
    addShape(s, "rect", 0, 0, 760, H, C.yellow);
    header(s, 12, "申し込む", false, 3);
    addText(s, "無料顧問1回分", 72, 132, 570, 72, { fontSize: 54, bold: true, color: C.black });
    addText(s, "あなたの資料1本を、\n使える形に整える。", 78, 244, 560, 110, { fontSize: 44, bold: true, lineSpacing: 0.98 });
    addText(s, "面談で扱うこと", 82, 410, 220, 24, { fontSize: 16, bold: true, color: C.black });
    check(s, 82, 454, "目的と読者を決める", C.white);
    check(s, 82, 502, "最初の構成をつくる", C.white);
    check(s, 82, 550, "次の一手を決める", C.white);
    addShape(s, "roundRect", 82, 626, 400, 56, C.black);
    addText(s, "無料顧問1回分を受ける", 112, 643, 340, 22, { fontSize: 17, bold: true, color: C.white, alignment: "center" });
    notes(s, "最後は、無料相談という抽象語ではなく、1回分で何が変わるかを具体化し、今申し込む理由を提示します。", [sources.generated, sources.codex]);
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await writeBlob(`${OUT_DIR}/${stem}.png`, png);
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(`${OUT_DIR}/${stem}.layout.json`, await layout.text());
  }
  const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
  await writeBlob(`${OUT_DIR}/deck-montage.webp`, montage);
  const snapshot = await deck.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 20000 });
  await fs.writeFile(`${OUT_DIR}/inspect.ndjson`, snapshot.ndjson ?? "");
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL_PPTX);
  console.log(JSON.stringify({ finalPptx: FINAL_PPTX, slides: deck.slides.items.length, outputDir: OUT_DIR }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
