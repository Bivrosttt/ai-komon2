import fs from "node:fs/promises";
import vm from "node:vm";

const source = await fs.readFile("/Users/koki/Desktop/ai-komon2/lead-magnets/ai-work-kit/prompt-data.js", "utf8");
const sandbox = { window: {} };
vm.runInNewContext(source, sandbox);
const prompts = sandbox.window.AI_KOMON_PROMPTS || [];
if (prompts.length !== 100) throw new Error(`Expected 100 prompts, found ${prompts.length}`);
await fs.writeFile("/Users/koki/Desktop/ai-komon2/.lead-magnet-refresh/prompts.json", JSON.stringify(prompts, null, 2));
console.log(JSON.stringify({count:prompts.length,categories:[...new Set(prompts.map(x=>x.category))]},null,2));
