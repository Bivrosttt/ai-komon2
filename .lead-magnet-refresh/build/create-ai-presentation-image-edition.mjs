import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/koki/Desktop/ai-komon2";
const ASSET_DIR = `${ROOT}/.lead-magnet-refresh/build/image-edition-assets`;
const OUT_DIR = `${ROOT}/.lead-magnet-refresh/build/image-edition-output`;
const FINAL_PPTX = `${ROOT}/materials/ai-komon-ai-presentation-image-edition.pptx`;
const W = 1152;
const H = 768;

const slideMeta = [
  ["AIで、良質なプレゼンをつくる。", ["https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md"]],
  ["AIは空白を埋め、人は何を捨てるか決める。", ["https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md"]],
  ["プレゼンは意思決定の設計である。", ["https://github.com/Gabberflast/academic-pptx-skill"]],
  ["良質な資料を構成する4層。", ["https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md", "https://github.com/tristan-mcinnis/pptx-from-layouts-skill"]],
  ["最初の10分で決める4つの条件。", ["https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices"]],
  ["話題タイトルを結論タイトルへ変える。", ["https://github.com/Gabberflast/academic-pptx-skill"]],
  ["1枚に1つの主張を置く。", ["https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md"]],
  ["主張に応じて5つの見せ方を選ぶ。", ["https://github.com/tristan-mcinnis/pptx-from-layouts-skill"]],
  ["装飾する前に情報を削る。", ["https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md"]],
  ["AIへの指示を3段階に分ける。", ["https://github.com/FluidForm-ai/fluiddocs-deck-builder", "https://github.com/Gabberflast/academic-pptx-skill"]],
  ["設計条件だけを作るプロンプト。", ["https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices"]],
  ["タイトルだけで物語を作るプロンプト。", ["https://github.com/Gabberflast/academic-pptx-skill"]],
  ["AIと人の仕事を交互にする。", ["https://github.com/FluidForm-ai/fluiddocs-deck-builder"]],
  ["生成後に通す5つの品質検査。", ["https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md", "https://support.microsoft.com/en-us/office/make-your-powerpoint-presentations-accessible-to-people-with-disabilities-6f7772b2-2f33-4bd2-8ca7-dae3b2b3ef25"]],
  ["1枚ごとの設計図を作るプロンプト。", ["https://github.com/tristan-mcinnis/pptx-from-layouts-skill"]],
  ["自社資料を1本持ち込むCTA。", []],
];

async function writeBlob(path, blob) {
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  for (let index = 0; index < slideMeta.length; index += 1) {
    const slide = deck.slides.add();
    const number = String(index + 1).padStart(2, "0");
    const path = `${ASSET_DIR}/slide-${number}.png`;
    slide.images.add({
      blob: new Uint8Array(readFileSync(path)),
      contentType: "image/png",
      alt: slideMeta[index][0],
      position: { left: 0, top: 0, width: W, height: H },
      geometry: "rect",
    });
    const sources = [
      "AI image generation via OpenAI image tool, 2026-07-28",
      ...slideMeta[index][1],
    ];
    slide.speakerNotes.textFrame.setText(
      `${slideMeta[index][0]}\n\n[Sources]\n${sources.map((source) => `- ${source}`).join("\n")}\n[/Sources]`,
    );
    slide.speakerNotes.setVisible(true);
    await writeBlob(`${OUT_DIR}/slide-${number}.png`, await deck.export({ slide, format: "png", scale: 1 }));
  }

  await writeBlob(`${OUT_DIR}/deck-montage.webp`, await deck.export({ format: "webp", montage: true, scale: 1 }));
  const inspection = await deck.inspect({ kind: "slide,image,notes", maxChars: 30000 });
  await fs.writeFile(`${OUT_DIR}/inspect.ndjson`, inspection.ndjson ?? "");
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(FINAL_PPTX);
  console.log(JSON.stringify({ finalPptx: FINAL_PPTX, slideCount: slideMeta.length, outputDir: OUT_DIR }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
