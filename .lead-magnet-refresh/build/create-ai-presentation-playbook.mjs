import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT_DIR = "/Users/koki/Desktop/ai-komon2/.lead-magnet-refresh/build/output";
const FINAL_PPTX = "/Users/koki/Desktop/ai-komon2/materials/ai-komon-ai-presentation-playbook-v2.pptx";
const HERO_IMAGE = "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-547ab70f-7306-477a-8fa6-44fe62dc7f33.png";

const W = 1280;
const H = 720;
const C = {
  ink: "#111111",
  muted: "#5D6168",
  line: "#D9D9D4",
  soft: "#F3F3EF",
  paper: "#FAFAF7",
  yellow: "#F4D84D",
  blue: "#8ED7F0",
  coral: "#FF8B7B",
  white: "#FFFFFF",
};

async function writeBlob(path, blob) {
  await fs.mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

function box(slide, left, top, width, height, fill = "none", lineFill = "none", lineWidth = 0, geometry = "rect") {
  return slide.shapes.add({
    geometry,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
  });
}

function text(slide, value, left, top, width, height, style = {}) {
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
    color: C.ink,
    verticalAlignment: "top",
    wrap: "square",
    autoFit: "shrinkText",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
    ...style,
  };
  return shape;
}

function dot(slide, x, y, size, fill) {
  return box(slide, x, y, size, size, fill, "none", 0, "ellipse");
}

function rule(slide, x, y, width, color = C.line, height = 2) {
  return box(slide, x, y, width, height, color);
}

function chrome(slide, page, kicker, dark = false) {
  const ink = dark ? C.white : C.ink;
  const muted = dark ? "#B5B8B8" : C.muted;
  text(slide, "AI顧問室", 72, 34, 140, 20, { fontSize: 14, bold: true, color: ink });
  text(slide, kicker, 220, 35, 520, 18, { fontSize: 12, bold: true, color: muted });
  text(slide, String(page).padStart(2, "0"), 1160, 34, 48, 20, { fontSize: 13, bold: true, color: muted, alignment: "right" });
}

function title(slide, value, sub = "", dark = false) {
  const ink = dark ? C.white : C.ink;
  text(slide, value, 72, 92, 920, 84, { fontSize: 40, bold: true, color: ink, lineSpacing: 1.02 });
  if (sub) text(slide, sub, 74, 184, 720, 32, { fontSize: 18, color: dark ? "#D6D8D8" : C.muted });
}

function note(slide, body, sources) {
  const sourceLines = sources.map((s) => `- ${s}`).join("\n");
  slide.speakerNotes.textFrame.setText(`${body}\n\n[Sources]\n${sourceLines}\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}

function label(slide, value, x, y, color = C.ink, fill = C.yellow) {
  box(slide, x, y + 3, 10, 10, fill, "none", 0, "ellipse");
  text(slide, value, x + 20, y, 300, 18, { fontSize: 13, bold: true, color });
}

function miniSlide(slide, x, y, w, h, headline, accent, variant = 0) {
  box(slide, x, y, w, h, C.white, C.line, 1);
  box(slide, x, y, w, 8, accent);
  text(slide, headline, x + 16, y + 18, w - 32, 22, { fontSize: 15, bold: true, color: C.ink });
  if (variant === 0) {
    box(slide, x + 16, y + 58, w * 0.54, 11, C.ink);
    box(slide, x + 16, y + 78, w * 0.78, 7, C.line);
    box(slide, x + 16, y + 94, w * 0.65, 7, C.line);
    box(slide, x + w * 0.66, y + 56, w * 0.22, 54, C.soft);
  } else if (variant === 1) {
    box(slide, x + 16, y + 58, w - 32, 62, C.soft);
    box(slide, x + 28, y + 74, w * 0.4, 12, accent);
    box(slide, x + 28, y + 95, w * 0.58, 8, C.line);
  } else {
    box(slide, x + 16, y + 56, 20, 64, accent);
    box(slide, x + 48, y + 60, w * 0.58, 10, C.ink);
    box(slide, x + 48, y + 80, w * 0.68, 7, C.line);
    box(slide, x + 48, y + 98, w * 0.44, 7, C.line);
  }
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const heroBytes = new Uint8Array(await fs.readFile(HERO_IMAGE));
  const external = {
    layouts: "https://github.com/tristan-mcinnis/pptx-from-layouts-skill",
    codexPpt: "https://github.com/ningzimu/codex-ppt-skill",
    openaiPrompt: "https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices",
    microsoft: "https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities",
    duarte: "https://www.duarte.com/training/visual-storytelling-training/",
  };

  // 01 Cover
  {
    const s = presentation.slides.add();
    s.background.fill = C.ink;
    chrome(s, 1, "AI SLIDE PLAYBOOK", true);
    text(s, "AIに、\n作らせる前に。", 72, 130, 620, 190, { fontSize: 64, bold: true, color: C.white, lineSpacing: 0.95 });
    text(s, "伝わるPowerPointを設計する\n実務の型", 78, 350, 430, 70, { fontSize: 24, color: "#D6D8D8", lineSpacing: 1.12 });
    box(s, 720, 118, 470, 470, C.white, "none", 0, "roundRect");
    s.images.add({ blob: heroBytes, contentType: "image/png", alt: "ラフな構成が整理されたスライドへ変わる様子", fit: "cover", position: { left: 734, top: 132, width: 442, height: 442 }, geometry: "roundRect", borderRadius: "rounded-2xl" });
    box(s, 72, 612, 188, 6, C.yellow);
    text(s, "AI顧問室 / LEAD MAGNET", 72, 642, 320, 18, { fontSize: 13, bold: true, color: C.yellow });
    note(s, "このデッキは、AIにスライドを作らせる前に、目的・構造・判断基準を揃えるための実務ガイドです。", [external.layouts, external.codexPpt]);
  }

  // 02 Problem
  {
    const s = presentation.slides.add();
    s.background.fill = C.white;
    chrome(s, 2, "PROBLEM / WHY NOW");
    title(s, "AIで速く作れるのに、\nなぜ資料は伝わらないのか？", "問題は、生成速度ではなく設計の順番にあります。");
    label(s, "よくある3つの詰まり", 74, 258);
    const items = [
      ["目的が曖昧", "「いい感じの資料」では、AIは判断できない。", C.yellow],
      ["情報が多すぎる", "1枚に複数の結論を詰め込み、読む人が迷う。", C.blue],
      ["検証が最後", "数字・出典・PDF化の崩れを、提出直前に発見する。", C.coral],
    ];
    items.forEach(([head, body, accent], i) => {
      const y = 310 + i * 112;
      dot(s, 76, y + 6, 22, accent);
      text(s, head, 118, y, 220, 30, { fontSize: 24, bold: true });
      text(s, body, 360, y + 2, 430, 28, { fontSize: 17, color: C.muted });
      rule(s, 118, y + 58, 670, C.line, 1);
    });
    // visual: misaligned slide fragments
    text(s, "出力はある。でも、\n意思決定につながらない。", 862, 280, 300, 72, { fontSize: 22, bold: true, color: C.ink });
    miniSlide(s, 858, 392, 280, 150, "市場データまとめ", C.yellow, 0);
    miniSlide(s, 894, 438, 280, 150, "施策の方向性", C.blue, 1);
    note(s, "ここではAI導入の失敗を、生成品質ではなく、目的・情報量・検証順序の設計問題として整理しています。", [external.layouts, external.codexPpt]);
  }

  // 03 Worst future
  {
    const s = presentation.slides.add();
    s.background.fill = C.ink;
    chrome(s, 3, "STAKE / WORST CASE", true);
    title(s, "自力で急いだ先にあるのは、\n“速いけれど使えない”資料です。", "作成時間が短くなっても、判断時間が伸びれば、全体では遅くなります。", true);
    const steps = [
      ["生成", "数分で見た目は整う", C.yellow],
      ["迷走", "主張・数字・出典が混ざる", C.blue],
      ["手戻り", "会議で説明し直し、作り直す", C.coral],
    ];
    steps.forEach(([h, b, accent], i) => {
      const x = 88 + i * 368;
      box(s, x, 340, 300, 170, "#1D1D1D", "#3E4142", 1);
      dot(s, x + 26, 368, 24, accent);
      text(s, `0${i + 1}`, x + 62, 364, 52, 28, { fontSize: 16, bold: true, color: accent });
      text(s, h, x + 26, 412, 240, 32, { fontSize: 28, bold: true, color: C.white });
      text(s, b, x + 26, 456, 244, 36, { fontSize: 16, color: "#C7C9C9" });
      if (i < 2) text(s, "→", x + 316, 400, 50, 40, { fontSize: 28, bold: true, color: C.yellow, alignment: "center" });
    });
    text(s, "速さだけを最適化すると、\n手戻りが利益を食います。", 88, 580, 660, 62, { fontSize: 24, bold: true, color: C.yellow });
    note(s, "最悪の未来を、作成速度ではなく意思決定までの総時間で捉えています。", [external.codexPpt]);
  }

  // 04 Best future
  {
    const s = presentation.slides.add();
    s.background.fill = C.paper;
    chrome(s, 4, "OUTCOME / BEST CASE");
    title(s, "先に“判断の型”を置けば、\nAIは作業を加速できます。", "人が決めるところと、AIに任せるところを分けます。");
    box(s, 74, 290, 1130, 2, C.ink);
    const rows = [
      ["人が決める", "誰に / 何を / どの判断を促すか", "目的・結論・制約", C.yellow],
      ["AIに任せる", "候補出し / 要約 / 変換 / 比較", "量を出す・抜けを探す", C.blue],
      ["人が確認する", "根拠 / 文脈 / 読みやすさ", "提出できる品質にする", C.coral],
    ];
    rows.forEach(([a, b, c, accent], i) => {
      const y = 320 + i * 100;
      dot(s, 88, y + 5, 18, accent);
      text(s, a, 128, y, 190, 28, { fontSize: 22, bold: true });
      text(s, b, 360, y, 430, 28, { fontSize: 19 });
      text(s, c, 850, y + 2, 320, 24, { fontSize: 16, color: C.muted });
      rule(s, 128, y + 60, 1036, C.line, 1);
    });
    text(s, "AIは“考える人”の代わりではなく、\n考える人の手数を減らす道具。", 74, 624, 620, 52, { fontSize: 21, bold: true, color: C.ink });
    note(s, "AIを人の代替ではなく、判断前の作業を圧縮する補助役として置くことで、実務に導入しやすい分業になります。", [external.codexPpt]);
  }

  // 05 Story before slides
  {
    const s = presentation.slides.add();
    s.background.fill = C.white;
    chrome(s, 5, "PRINCIPLE 01 / STORY FIRST");
    title(s, "スライドより先に、\n“相手の頭の中の変化”を設計する。", "ストーリーとは、出来事の順番ではなく、理解が変わる順番です。");
    const cols = [
      ["現在地", "いま何が起きている？", "見えている課題", C.blue],
      ["ギャップ", "なぜ、このままでは困る？", "放置したコスト", C.coral],
      ["未来", "何が変われば前に進める？", "選ぶべき一手", C.yellow],
    ];
    cols.forEach(([h, q, b, accent], i) => {
      const x = 74 + i * 374;
      box(s, x, 304, 314, 194, C.soft, "none", 0);
      box(s, x, 304, 314, 12, accent);
      text(s, `0${i + 1}`, x + 24, 338, 42, 28, { fontSize: 16, bold: true, color: C.muted });
      text(s, h, x + 24, 378, 240, 32, { fontSize: 27, bold: true });
      text(s, q, x + 24, 424, 258, 24, { fontSize: 16, bold: true });
      text(s, b, x + 24, 462, 258, 20, { fontSize: 15, color: C.muted });
      if (i < 2) text(s, "→", x + 328, 386, 48, 40, { fontSize: 28, bold: true, color: C.ink, alignment: "center" });
    });
    text(s, "資料の構成は、情報の棚卸しではなく、\n相手を一歩動かすための道筋です。", 74, 566, 720, 56, { fontSize: 23, bold: true });
    note(s, "この3段階は、Duarteのストーリーテリングにある現在地・ギャップ・望ましい未来という考え方を、業務資料向けに簡略化したものです。", [external.duarte]);
  }

  // 06 One message per slide
  {
    const s = presentation.slides.add();
    s.background.fill = C.paper;
    chrome(s, 6, "PRINCIPLE 02 / ONE MESSAGE");
    title(s, "1枚に1つの結論。\n見出しだけで、言いたいことが伝わる状態へ。", "タイトルを“話題”ではなく“結論”にすると、読む負担が下がります。");
    miniSlide(s, 86, 310, 320, 170, "市場について", C.line, 0);
    text(s, "話題は分かる。\nでも、何を判断すればいい？", 86, 502, 300, 48, { fontSize: 18, color: C.muted });
    text(s, "→", 430, 360, 90, 64, { fontSize: 42, bold: true, color: C.yellow, alignment: "center" });
    miniSlide(s, 552, 310, 490, 170, "今期は、既存顧客向けの提案を先に強化する", C.yellow, 1);
    text(s, "結論が見える。\n本文は、その理由を支える役に変わる。", 552, 502, 460, 48, { fontSize: 18, color: C.muted });
    box(s, 1092, 310, 92, 170, C.ink);
    text(s, "1\nIDEA", 1110, 350, 56, 78, { fontSize: 18, bold: true, color: C.yellow, alignment: "center" });
    note(s, "action title（結論型タイトル）は、スライドの内容を見出しだけで先に伝えるための考え方です。", [external.duarte, external.layouts]);
  }

  // 07 Workflow
  {
    const s = presentation.slides.add();
    s.background.fill = C.white;
    chrome(s, 7, "METHOD / FIVE-PHASE WORKFLOW");
    title(s, "AIに任せる前に、5つのゲートを通す。", "各ゲートで“次へ進む条件”を決めると、手戻りが小さくなります。");
    const phases = [
      ["01", "Brief", "目的・相手・判断", C.yellow],
      ["02", "Outline", "結論の順番", C.blue],
      ["03", "Visual", "図解・レイアウト", C.coral],
      ["04", "Build", "AIで初稿化", C.yellow],
      ["05", "QA", "根拠・表示・出力", C.blue],
    ];
    phases.forEach(([num, head, body, accent], i) => {
      const x = 82 + i * 222;
      if (i < 4) rule(s, x + 148, 390, 78, C.line, 3);
      box(s, x, 318, 154, 148, C.paper, C.line, 1);
      dot(s, x + 20, 340, 28, accent);
      text(s, num, x + 58, 340, 46, 22, { fontSize: 14, bold: true, color: C.muted });
      text(s, head, x + 20, 386, 110, 30, { fontSize: 22, bold: true });
      text(s, body, x + 20, 428, 116, 32, { fontSize: 14, color: C.muted });
    });
    text(s, "ゲートの目的は、AIを遅くすることではなく、\n間違った方向への大量生成を止めること。", 82, 548, 760, 60, { fontSize: 23, bold: true });
    note(s, "`pptx-from-layouts`のプロファイル→作成→レンダーという工程と、`codex-ppt`の大綱→スタイル→サンプル→全体生成→QAというゲート設計を、編集可能PPTX向けに統合したフローです。", [external.layouts, external.codexPpt]);
  }

  // 08 Prompt anatomy
  {
    const s = presentation.slides.add();
    s.background.fill = C.ink;
    chrome(s, 8, "METHOD / PROMPT ANATOMY", true);
    title(s, "プロンプトは“お願い文”ではなく、\n制作ブリーフです。", "AIが迷わないように、判断材料を先に並べます。", true);
    const lines = [
      ["ROLE", "あなたは、経営会議向け資料を作る編集者です。", C.yellow],
      ["AUDIENCE", "中小企業の経営者。専門用語は初出で説明する。", C.blue],
      ["DECISION", "今月、営業のどの施策を優先するか決めてもらう。", C.coral],
      ["CONSTRAINT", "12枚 / 1枚1メッセージ / 未確認の数字は作らない。", C.yellow],
      ["OUTPUT", "各ページに結論・根拠・図解案・確認事項を付ける。", C.blue],
    ];
    lines.forEach(([tag, body, accent], i) => {
      const y = 292 + i * 58;
      box(s, 86, y, 156, 40, accent);
      text(s, tag, 104, y + 10, 110, 18, { fontSize: 13, bold: true, color: C.ink });
      text(s, body, 278, y + 7, 820, 24, { fontSize: 18, color: C.white });
      rule(s, 278, y + 42, 820, "#3C3E3E", 1);
    });
    note(s, "プロンプトの構造は、OpenAIの公式ガイドにある明確な指示、文脈、制約、出力形式の考え方を、スライド制作向けのブリーフに落とし込んだものです。", [external.openaiPrompt]);
  }

  // 09 Before after prompt
  {
    const s = presentation.slides.add();
    s.background.fill = C.paper;
    chrome(s, 9, "METHOD / BEFORE & AFTER");
    title(s, "“いい感じに作って”をやめると、\n初稿の方向が揃います。", "依頼の良し悪しは、長さではなく判断材料の有無で決まります。");
    box(s, 78, 300, 500, 238, C.white, C.line, 1);
    text(s, "NG / ふわっとした依頼", 108, 328, 280, 24, { fontSize: 16, bold: true, color: C.coral });
    text(s, "営業資料を、\nいい感じのデザインで\n10枚くらいにして。", 108, 386, 410, 114, { fontSize: 30, bold: true, color: C.ink, lineSpacing: 1.08 });
    box(s, 634, 300, 568, 238, C.ink);
    text(s, "OK / 判断を埋めた依頼", 664, 328, 280, 24, { fontSize: 16, bold: true, color: C.yellow });
    text(s, "経営者が今月の営業施策を\n1つ選べる、12枚の資料にする。", 664, 378, 480, 56, { fontSize: 24, bold: true, color: C.white });
    text(s, "対象：既存顧客 / 結論先行 / 数字は出典付き /\n未確認は「要確認」と表示 / 各ページに図解案", 664, 460, 480, 46, { fontSize: 16, color: "#D6D8D8" });
    note(s, "良い依頼では、聴衆・目的・出力形式・制約・不確実性の扱いを明示します。", [external.openaiPrompt]);
  }

  // 10 Visual grammar
  {
    const s = presentation.slides.add();
    s.background.fill = C.white;
    chrome(s, 10, "METHOD / VISUAL GRAMMAR");
    title(s, "情報の種類に合わせて、\nレイアウトを選びます。", "レイアウトは飾りではなく、情報の関係を見せる道具です。");
    const cards = [
      ["結論", "Hero", "一つの主張を大きく", C.yellow, 0],
      ["比較", "Contrast", "違いを左右で見せる", C.blue, 1],
      ["手順", "Process", "順番を左から右へ", C.coral, 2],
      ["根拠", "Evidence", "数字を主役にする", C.yellow, 1],
      ["行動", "CTA", "次の一歩を絞る", C.blue, 0],
    ];
    cards.forEach(([kind, head, body, accent, variant], i) => {
      const x = 74 + i * 231;
      box(s, x, 320, 198, 222, C.paper, C.line, 1);
      text(s, kind, x + 18, 340, 70, 20, { fontSize: 13, bold: true, color: C.muted });
      text(s, head, x + 18, 372, 150, 24, { fontSize: 22, bold: true });
      // compact visual grammar
      if (variant === 0) {
        box(s, x + 18, 424, 158, 12, C.ink);
        box(s, x + 18, 448, 112, 8, C.line);
      } else if (variant === 1) {
        box(s, x + 18, 420, 72, 54, accent);
        box(s, x + 102, 420, 74, 54, C.soft);
        rule(s, x + 94, 420, 2, C.ink, 54);
      } else {
        rule(s, x + 28, 448, 122, C.ink, 3);
        [0, 1, 2].forEach((n) => dot(s, x + 22 + n * 58, 436, 24, n === 1 ? accent : C.ink));
      }
      text(s, body, x + 18, 494, 158, 34, { fontSize: 14, color: C.muted });
    });
    note(s, "スライドごとの情報構造に合わせて、hero・comparison・process・evidence・CTAのシルエットを使い分けています。", [external.layouts]);
  }

  // 11 Evidence
  {
    const s = presentation.slides.add();
    s.background.fill = C.paper;
    chrome(s, 11, "METHOD / EVIDENCE");
    title(s, "数字は、強い言葉より先に\n“根拠の置き場所”を決めます。", "AIに数字を作らせない。数字を使うなら、出典・基準日・定義を添えます。");
    const rows = [
      ["主張", "営業の初回返信を早める", "何を変える？", C.yellow],
      ["根拠", "自社の問い合わせログ / 直近90日", "どこから来た？", C.blue],
      ["注意", "対象期間と母数を脚注に置く", "どこまで言える？", C.coral],
    ];
    rows.forEach(([a, b, c, accent], i) => {
      const y = 312 + i * 86;
      dot(s, 86, y + 8, 18, accent);
      text(s, a, 124, y, 120, 24, { fontSize: 20, bold: true });
      text(s, b, 280, y, 450, 24, { fontSize: 19 });
      text(s, c, 820, y + 2, 280, 20, { fontSize: 15, color: C.muted });
      rule(s, 124, y + 54, 978, C.line, 1);
    });
    box(s, 84, 594, 1020, 48, C.ink);
    text(s, "要確認のまま残すことは、弱さではなく、信頼性を守る編集判断です。", 112, 608, 930, 22, { fontSize: 18, bold: true, color: C.white });
    note(s, "数字・引用・出典を、生成の後ではなく依頼と構成の段階から扱う設計です。", [external.openaiPrompt, external.microsoft]);
  }

  // 12 QA
  {
    const s = presentation.slides.add();
    s.background.fill = C.white;
    chrome(s, 12, "METHOD / QA BEFORE DELIVERY");
    title(s, "完成とは、生成できたことではなく\n“提出しても崩れない”こと。", "AIスライドは、内容・見た目・書き出しの3方向から確認します。");
    const qa = [
      ["CONTENT", "結論は1枚1つか", "数字と出典は追えるか", C.yellow],
      ["VISUAL", "タイトルだけで意味が伝わるか", "図解が主張を補助しているか", C.blue],
      ["EXPORT", "PPTXとPDFを両方開いたか", "文字切れ・順序・余白は安全か", C.coral],
    ];
    qa.forEach(([head, l1, l2, accent], i) => {
      const x = 84 + i * 366;
      box(s, x, 310, 306, 230, C.paper, C.line, 1);
      box(s, x, 310, 306, 12, accent);
      text(s, head, x + 24, 350, 220, 22, { fontSize: 15, bold: true, color: C.muted });
      text(s, "✓", x + 24, 402, 34, 34, { fontSize: 26, bold: true, color: accent });
      text(s, l1, x + 72, 405, 206, 22, { fontSize: 17, bold: true });
      text(s, "✓", x + 24, 462, 34, 34, { fontSize: 26, bold: true, color: accent });
      text(s, l2, x + 72, 465, 206, 38, { fontSize: 17, bold: true });
    });
    text(s, "全ページを画像で見る。\nコードや作成ログだけを信じない。", 86, 594, 650, 52, { fontSize: 22, bold: true });
    note(s, "取得したスキルとCodex標準ルートが共通して重視する、レンダー後の視覚検査・テキスト切れ・出典・出力確認をまとめています。", [external.layouts, external.codexPpt, external.microsoft]);
  }

  // 13 Starter prompt
  {
    const s = presentation.slides.add();
    s.background.fill = C.ink;
    chrome(s, 13, "TAKEAWAY / STARTER PROMPT", true);
    title(s, "そのまま使える、\n最初の1本。", "まずはAIに、ページを作らせる前の設計をさせます。", true);
    box(s, 76, 292, 1128, 280, "#1D1D1D", "#3E4142", 1);
    text(s, "あなたは、経営者向け資料の編集者です。\n\n目的：［誰に］［何を判断してほしいか］\n前提：［現状 / 根拠 / 制約］\n出力：①全体の結論 ②ページごとの役割 ③図解案 ④確認が必要な点\nルール：1ページ1メッセージ。未確認の数字は作らず「要確認」と書く。", 112, 334, 1010, 196, { fontSize: 21, color: C.white, lineSpacing: 1.22 });
    box(s, 76, 604, 262, 6, C.yellow);
    text(s, "先に構造。あとからデザイン。", 76, 638, 440, 24, { fontSize: 19, bold: true, color: C.yellow });
    note(s, "読者が自分の業務に置き換えやすいよう、汎用のスライド設計ブリーフを提示しています。", [external.openaiPrompt]);
  }

  // 14 CTA
  {
    const s = presentation.slides.add();
    s.background.fill = C.yellow;
    chrome(s, 14, "NEXT / FREE ADVISORY SESSION");
    text(s, "ここまでを、\n自社の仕事に落とし込む。", 76, 130, 680, 150, { fontSize: 52, bold: true, color: C.ink, lineSpacing: 0.98 });
    text(s, "無料顧問1回分", 80, 342, 580, 74, { fontSize: 52, bold: true, color: C.ink });
    text(s, "用途・既存資料・業務フローを伺い、\nAIに任せる範囲と、最初の一歩を一緒に決めます。", 82, 438, 620, 60, { fontSize: 21, color: C.ink, lineSpacing: 1.16 });
    box(s, 858, 154, 286, 286, C.ink, "none", 0, "ellipse");
    text(s, "01\n相談\n02\n設計\n03\n実行", 937, 206, 130, 170, { fontSize: 25, bold: true, color: C.yellow, alignment: "center", lineSpacing: 1.1 });
    box(s, 858, 500, 286, 60, C.ink, "none", 0, "roundRect");
    text(s, "無料顧問1回分を受ける", 890, 518, 220, 22, { fontSize: 17, bold: true, color: C.white, alignment: "center" });
    text(s, "AI顧問室", 80, 640, 160, 22, { fontSize: 16, bold: true, color: C.ink });
    note(s, "面談後に、相談内容に合わせた資料や次のアクションを案内する想定です。", [external.codexPpt]);
  }

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await writeBlob(`${OUT_DIR}/${stem}.png`, png);
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(`${OUT_DIR}/${stem}.layout.json`, await layout.text());
  }
  const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
  await writeBlob(`${OUT_DIR}/deck-montage.webp`, montage);
  const snapshot = await presentation.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 20000 });
  await fs.writeFile(`${OUT_DIR}/inspect.ndjson`, snapshot.ndjson ?? "");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);
  console.log(JSON.stringify({ finalPptx: FINAL_PPTX, slides: presentation.slides.items.length, outputDir: OUT_DIR }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
