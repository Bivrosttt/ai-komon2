import crypto from "node:crypto";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = "/Users/koki/Desktop/ai-komon2";
const SOURCE_PPTX = path.join(ROOT, "materials/ai-komon-ai-presentation-masterclass.pptx");
const GUIDE_DIR = path.join(ROOT, "lead-magnets/ai-work-kit/ai-presentation-guide");
const SLIDE_DIR = path.join(GUIDE_DIR, "slides");
const MANIFEST_PATH = path.join(GUIDE_DIR, "presentation-guide-manifest.json");
const PDF_PATH = path.join(ROOT, "materials/ai-komon-ai-presentation-masterclass.pdf");
const RENDER_SCRIPT = "/Users/koki/.cache/codex-runtimes/codex-primary-runtime/plugins/openai-primary-runtime/plugins/presentations/skills/presentations/container_tools/render_slides.py";
const BUNDLED_PYTHON = "/Users/koki/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const previews = [
  { sourceSlide: 1, file: "slide-01-cover.png", role: "cover", alt: "AIで良質なプレゼンをつくる実務教材の表紙" },
  { sourceSlide: 3, file: "slide-03-problem.png", role: "problem", alt: "資料は完成しているのに会議の判断が進まない問題を示すスライド" },
  { sourceSlide: 8, file: "slide-05-decision.png", role: "decision", alt: "プレゼンはページ制作ではなく意思決定の設計だと説明するスライド" },
  { sourceSlide: 9, file: "slide-06-model.png", role: "model", alt: "理解、比較、納得、行動の順に相手が動くことを示すスライド" },
  { sourceSlide: 14, file: "slide-08-story.png", role: "story", alt: "現状、問題、転換、根拠、行動の順で物語に圧力を作るスライド" },
  { sourceSlide: 19, file: "slide-11-visual.png", role: "visual", alt: "主張に合わせて選ぶ5つの見せ方を紹介するスライド" },
  { sourceSlide: 21, file: "slide-15-workflow.png", role: "workflow", alt: "背景画像の上に前景モックを置いて文字の居場所を作るスライド" },
  { sourceSlide: 10, file: "slide-16-prompt-brief.png", role: "prompt-brief", alt: "読者、決定、根拠、次の行動を固定するBriefのスライド" },
  { sourceSlide: 12, file: "slide-17-prompt-story.png", role: "prompt-story", alt: "タイトルだけで資料の流れを設計するGhost Deckのスライド" },
  { sourceSlide: 18, file: "slide-18-prompt-spec.png", role: "prompt-spec", alt: "各ページの主張、根拠、見せ方、出典を固定するSlide Specのスライド" },
  { sourceSlide: 26, file: "slide-20-qa.png", role: "qa", alt: "物語、焦点、収まり、根拠、読みやすさを確認するスライド" },
  { sourceSlide: 28, file: "slide-22-cta.png", role: "cta", alt: "自社資料で試し迷う工程だけ無料顧問を使う案内スライド" },
];

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: "utf8", stdio: "pipe", ...options });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  }
  return result;
}

async function copyRenderedSlides(renderDir) {
  await fs.mkdir(SLIDE_DIR, { recursive: true });
  for (const preview of previews) {
    const source = path.join(renderDir, `slide-${preview.sourceSlide}.png`);
    const target = path.join(SLIDE_DIR, preview.file);
    await fs.access(source);
    await fs.copyFile(source, target);
  }
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fsSync.readFileSync(filePath)).digest("hex");
}

async function main() {
  await fs.access(SOURCE_PPTX);
  await fs.access(PDF_PATH);
  await fs.mkdir(GUIDE_DIR, { recursive: true });
  const runDir = await fs.mkdtemp(path.join(os.tmpdir(), "ai-komon-presentation-sync-"));
  const renderDir = path.join(runDir, "slides");

  const python = fsSync.existsSync(BUNDLED_PYTHON) ? BUNDLED_PYTHON : "python3";
  run(python, [RENDER_SCRIPT, PDF_PATH, "--output_dir", renderDir, "--width", "1600", "--height", "900"]);
  await copyRenderedSlides(renderDir);

  const manifest = {
    source: "../../../../materials/ai-komon-ai-presentation-masterclass.pptx",
    sourceSha256: sha256(SOURCE_PPTX),
    pdf: "../../../../materials/ai-komon-ai-presentation-masterclass.pdf",
    pdfSha256: sha256(PDF_PATH),
    slideCount: 28,
    previewPolicy: "HTMLはPowerPointから書き出した正本PDFの代表12枚を表示する。",
    previews,
  };
  await fs.writeFile(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`);

  console.log(JSON.stringify({
    source: SOURCE_PPTX,
    manifest: MANIFEST_PATH,
    previewCount: previews.length,
    slideCount: manifest.slideCount,
    pdf: PDF_PATH,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
