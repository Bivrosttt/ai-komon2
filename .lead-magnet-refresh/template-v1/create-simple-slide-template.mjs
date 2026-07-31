import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/koki/Desktop/ai-komon2";
const BUILD = path.join(ROOT, ".lead-magnet-refresh/template-v1");
const OUTPUT = path.join(BUILD, "output");
const FINAL_PPTX = path.join(ROOT, "materials/ai-komon-simple-slide-template.pptx");

const W = 1280;
const H = 720;
const C = {
  black: "#101010",
  ink: "#111111",
  white: "#FFFFFF",
  fog: "#F5F5F5",
  gray: "#6A6E75",
  line: "#D8DADF",
  red: "#EF3D38",
  redSoft: "#FCE9E8",
  blue: "#2458D7",
  blueSoft: "#E8EEFF",
  yellow: "#F5C43F",
  yellowSoft: "#FFF5CC",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function shape(slide, geometry, x, y, w, h, fill = "none", options = {}) {
  return slide.shapes.add({
    geometry,
    name: options.name,
    position: { left: x, top: y, width: w, height: h, rotation: options.rotation ?? 0 },
    fill,
    line: options.line ?? { style: "solid", fill: options.lineColor ?? "none", width: options.lineWidth ?? 0 },
    ...(geometry === "rect" || geometry === "roundRect" || geometry === "textbox"
      ? { borderRadius: options.radius ?? 0 }
      : {}),
    shadow: options.shadow ?? "shadow-none",
  });
}

function rect(slide, x, y, w, h, fill, options = {}) {
  return shape(slide, options.geometry ?? "rect", x, y, w, h, fill, options);
}

function text(slide, value, x, y, w, h, options = {}) {
  const box = shape(slide, "textbox", x, y, w, h, options.fill ?? "none", {
    name: options.name,
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
    radius: options.radius ?? 0,
  });
  box.text = value;
  box.text.style = {
    typeface: "Hiragino Kaku Gothic ProN",
    fontSize: options.size ?? 20,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
    lineSpacing: options.lineSpacing ?? 1.05,
    autoFit: "shrinkText",
    wrap: "square",
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return box;
}

function baseSlide(deck, page, labelText, options = {}) {
  const slide = deck.slides.add();
  slide.background.fill = C.black;
  rect(slide, 24, 14, 1232, 692, C.white, {
    geometry: "roundRect",
    radius: 18,
    lineColor: C.white,
    lineWidth: 0,
    shadow: "shadow-lg",
  });
  text(slide, labelText, 88, 36, 560, 24, {
    size: 15,
    bold: true,
    color: options.dark ? "#D5D7DC" : C.gray,
  });
  text(slide, String(page).padStart(2, "0"), 1176, 668, 38, 18, {
    size: 14,
    bold: true,
    align: "right",
    color: C.gray,
    name: `fixed-page-number-${page}`,
  });
  return slide;
}

function title(slide, value, options = {}) {
  return text(slide, value, options.x ?? 88, options.y ?? 70, options.w ?? 1100, options.h ?? 116, {
    name: options.name,
    size: options.size ?? 46,
    bold: true,
    color: options.color ?? C.ink,
    lineSpacing: 0.96,
  });
}

function card(slide, x, y, w, h, options = {}) {
  return rect(slide, x, y, w, h, options.fill ?? C.white, {
    geometry: "roundRect",
    radius: options.radius ?? 16,
    lineColor: options.lineColor ?? C.line,
    lineWidth: options.lineWidth ?? 1,
    shadow: options.shadow ?? "shadow-sm",
  });
}

function arrow(slide, x, y, w, h, fill = C.yellow) {
  return rect(slide, x, y, w, h, fill, {
    geometry: "rightArrow",
    line: { style: "solid", fill: "none", width: 0 },
  });
}

function note(slide, description) {
  slide.speakerNotes.textFrame.setText(`${description}\n\n[Sources]\n- AI顧問室のテンプレート設計\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}

function addCompareCard(slide, x, y, w, h, heading, body, caption, accent, fill) {
  text(slide, heading, x, y - 42, w, 28, { size: 19, bold: true, color: accent });
  card(slide, x, y, w, h, { fill });
  text(slide, body, x + 24, y + 64, w - 48, 100, { size: 29, bold: true, align: "center", valign: "middle" });
  text(slide, caption, x + 24, y + h - 54, w - 48, 28, { size: 16, bold: true, color: accent, align: "center" });
}

async function main() {
  await fs.mkdir(OUTPUT, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 01 Cover
  {
    const s = baseSlide(deck, 1, "TEMPLATE / COVER");
    text(s, "実務テンプレート", 88, 142, 360, 28, { size: 18, bold: true, color: C.blue });
    title(s, "これだけでOK。\nAIでクオリティの高い\nスライドを作る方法", { y: 182, w: 640, h: 210, size: 54 });
    text(s, "社長・決裁者が判断できる資料を、\nシンプルな構図でつくる。", 88, 448, 520, 72, { size: 25, color: C.gray, lineSpacing: 1.1 });
    rect(s, 88, 566, 160, 8, C.yellow, { geometry: "roundRect", radius: 4 });
    note(s, "表紙は大見出しと短い補足だけ。装飾を増やさず、最初の一枚で対象読者と約束を伝える。");
  }

  // 02 Compare / reference composition
  {
    const s = baseSlide(deck, 2, "TEMPLATE / VAGUE VS SPECIFIC");
    title(s, "曖昧な依頼では、\nどれだけ良いプロンプトでも資料がぶれる。", { y: 70, h: 118 });
    addCompareCard(s, 114, 286, 444, 246, "VAGUE", "経営者向けに\nAIの提案資料を作る", "読者も、決定も、場面も曖昧", C.red, "#FAFAFA");
    arrow(s, 584, 381, 116, 42, C.yellow);
    addCompareCard(s, 744, 286, 460, 246, "SPECIFIC", "従業員30〜100名の経営者が、\n問い合わせ対応で\n2週間の試験導入を承認する提案", "判断条件が具体的", C.blue, C.white);
    text(s, "具体化するのは文章量ではなく、判断条件。", 318, 620, 660, 36, { size: 25, bold: true, align: "center" });
    note(s, "参考画像の構図をテンプレート化。左右の比較、中央の単純な矢印、下部の結論だけで成立させる。");
  }

  // 03 One claim
  {
    const s = baseSlide(deck, 3, "TEMPLATE / ONE CLAIM");
    title(s, "1枚に1つの主張だけを置く。", { y: 72, h: 80 });
    text(s, "AIに作らせる前に、\nこのページで何を決めてほしいかを書く。", 88, 244, 640, 128, { size: 34, bold: true, lineSpacing: 1.08 });
    rect(s, 88, 418, 636, 1, C.line);
    text(s, "主張", 88, 448, 100, 24, { size: 16, bold: true, color: C.red });
    text(s, "次回、担当部署で2週間の検証を始める。", 88, 480, 620, 42, { size: 24, bold: true });
    card(s, 820, 244, 330, 236, { fill: C.fog });
    text(s, "余白を残す\n＝読み手の視線を\n主張に集める", 850, 294, 270, 128, { size: 30, bold: true, align: "center", valign: "middle" });
    note(s, "主張を大きく、補足を少なく。複雑な図解の代わりに、余白と文字のサイズ差で焦点をつくる。");
  }

  // 04 Two columns
  {
    const s = baseSlide(deck, 4, "TEMPLATE / TWO COLUMNS");
    title(s, "問題と解決策を、左右に分けて見せる。", { y: 72, h: 80 });
    text(s, "問題", 114, 226, 460, 28, { size: 19, bold: true, color: C.red });
    card(s, 114, 268, 460, 250, { fill: C.redSoft, lineColor: C.redSoft });
    text(s, "資料は完成しているのに、\n会議の判断が進まない。", 146, 332, 396, 108, { size: 32, bold: true, align: "center", valign: "middle" });
    text(s, "解決策", 706, 226, 460, 28, { size: 19, bold: true, color: C.blue });
    card(s, 706, 268, 460, 250, { fill: C.blueSoft, lineColor: C.blueSoft });
    text(s, "決めることを先に固定し、\n1枚1主張で資料をつくる。", 738, 332, 396, 108, { size: 32, bold: true, align: "center", valign: "middle" });
    text(s, "色は左右の役割を伝えるためだけに使う。", 364, 620, 552, 36, { size: 23, bold: true, align: "center" });
    note(s, "左右2カラムは問題と解決策の対比に限定する。カード内の情報量を増やさない。");
  }

  // 05 Three-step process
  {
    const s = baseSlide(deck, 5, "TEMPLATE / THREE STEPS");
    title(s, "作業は3段階に分ける。", { y: 72, h: 80 });
    const steps = [
      ["01", "決める", "読者・決定・根拠を固定", C.blue],
      ["02", "並べる", "タイトルだけで流れを作る", C.yellow],
      ["03", "整える", "本文・見せ方・QAを行う", C.red],
    ];
    steps.forEach((step, i) => {
      const x = 108 + i * 362;
      card(s, x, 252, 300, 218, { fill: C.white });
      text(s, step[0], x + 26, 276, 70, 28, { size: 18, bold: true, color: step[3] });
      text(s, step[1], x + 26, 326, 248, 48, { size: 34, bold: true });
      text(s, step[2], x + 26, 398, 248, 42, { size: 18, color: C.gray, lineSpacing: 1.1 });
      if (i < 2) arrow(s, x + 312, 340, 42, 28, C.line);
    });
    text(s, "先に構図を決めると、AIに任せる範囲が明確になる。", 282, 592, 716, 36, { size: 23, bold: true, align: "center" });
    note(s, "工程を3つに単純化。矢印は一方向に一つだけ置き、読者の視線を迷わせない。");
  }

  // 06 Image placeholder
  {
    const s = baseSlide(deck, 6, "TEMPLATE / IMAGE + MESSAGE");
    title(s, "画像は雰囲気ではなく、\n主張を理解する舞台として置く。", { y: 72, h: 116 });
    card(s, 88, 262, 622, 292, { fill: C.fog, lineColor: C.line });
    text(s, "IMAGE\nここに背景写真を置く", 132, 350, 534, 100, { size: 30, bold: true, color: C.gray, align: "center", valign: "middle" });
    text(s, "写真の上に長文を直接置かない。\n白い前景カードに主張を置く。", 792, 300, 330, 104, { size: 28, bold: true, lineSpacing: 1.08 });
    rect(s, 792, 466, 300, 72, C.yellowSoft, { geometry: "roundRect", radius: 10 });
    text(s, "文字の居場所を先につくる", 816, 486, 252, 30, { size: 18, bold: true, color: C.ink, align: "center", valign: "middle" });
    note(s, "画像枠はあくまで置き場所。画像と文字の役割を分離し、背景画像に依存した読みにくいレイアウトを避ける。");
  }

  // 07 CTA
  {
    const s = baseSlide(deck, 7, "TEMPLATE / CTA");
    title(s, "まず1本、自社資料で試す。", { y: 72, h: 80 });
    text(s, "教材だけで進められる方は、そのまま実践してください。", 88, 202, 660, 34, { size: 21, color: C.gray });
    const actions = ["自社資料を1本選ぶ", "決めることを1つ書く", "1枚だけ作り直す"];
    actions.forEach((item, i) => {
      const y = 292 + i * 72;
      rect(s, 88, y, 42, 42, C.blue, { geometry: "ellipse" });
      text(s, String(i + 1), 88, y, 42, 42, { size: 18, bold: true, color: C.white, align: "center", valign: "middle" });
      text(s, item, 158, y + 2, 540, 36, { size: 25, bold: i === 0, valign: "middle" });
    });
    card(s, 820, 260, 340, 240, { fill: C.black, lineColor: C.black, shadow: "shadow-md" });
    text(s, "無料顧問\n1回分", 858, 306, 264, 88, { size: 35, bold: true, color: C.white, lineSpacing: 0.98 });
    text(s, "自社資料を持ち込み、\n迷う工程だけ一緒に整理する", 858, 418, 264, 48, { size: 17, color: "#D5D7DC", lineSpacing: 1.08 });
    note(s, "CTAは教材の価値を下げず、次の一歩として置く。黒いカードは一つだけ。");
  }

  const inspect = await deck.inspect({ kind: "slide,textbox,shape,notes", maxChars: 100000 });
  await fs.writeFile(path.join(OUTPUT, "template-inspect.ndjson"), inspect.ndjson);
  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(OUTPUT, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(path.join(OUTPUT, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }
  await writeBlob(path.join(OUTPUT, "template-montage.webp"), await deck.export({ format: "webp", montage: true, scale: 0.5 }));
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL_PPTX);
  console.log(FINAL_PPTX);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
