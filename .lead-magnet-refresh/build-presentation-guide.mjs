import fs from "node:fs/promises";
import fsSync from "node:fs";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/koki/Desktop/ai-komon2";
const OUT = `${ROOT}/materials/ai-komon-presentation-quality-playbook.pptx`;
const PREVIEW = `${ROOT}/.lead-magnet-refresh/preview/presentation-quality`;
const W = 1280, H = 720;
const C = { navy:"#071426", blue:"#102946", blue2:"#1B3B60", cream:"#F7F1E7", paper:"#FFFDF9", ink:"#142238", gold:"#E8B94A", mint:"#74D6C6", coral:"#F58A6D", grey:"#8592A7", pale:"#DFE8E8", white:"#F9FBFF", red:"#D75C58" };
const FONT = "Aptos";
const assets = {
  problem: "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-68800c66-6272-4525-953a-dff8f9d9ca9e.png",
  future: "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-ea32aa6e-ee59-4c3e-a9e7-96943812cd65.png",
  metaphor: "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-c915ef73-2c9e-453b-8617-e4ab799034b6.png",
  workflow: "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-6cd0b0b4-5d6b-4161-92e0-f270cd7df0e1.png",
  gifts: "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-51c9ca12-1074-4e64-90e6-b1d634866745.png",
};
const sources = {
  microsoft: "https://support.microsoft.com/en-us/powerpoint/tips-for-creating-and-delivering-an-effective-presentation",
  accessibility: "https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities",
  designer: "https://support.microsoft.com/en-us/PowerPoint/create-professional-slide-layouts-with-designer",
  titles: "https://support.microsoft.com/en-us/powerpoint/title-a-slide",
  openai: "https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices",
  openaiApi: "https://help.openai.com/en/articles/6654000-how-to-use-advanced-prompt-engineering",
  duarteStory: "https://www.duarte.com/training/visual-storytelling-training/",
  duarteBig: "https://www.duarte.com/training/duarte-big-idea/",
};

function addShape(slide, geometry, position, fill="none", lineFill="none", lineWidth=0, name="") {
  return slide.shapes.add({geometry, name, position, fill, line:{style:"solid", fill:lineFill, width:lineWidth}});
}
function rect(slide, position, fill, radius=0, lineFill="none", lineWidth=0, name="") { return addShape(slide, radius ? "roundRect" : "rect", position, fill, lineFill, lineWidth, name); }
function tx(slide, value, position, style={}, name="") {
  const s = addShape(slide, "textbox", position, "none", "none", 0, name);
  s.text = value;
  s.text.style = {typeface:FONT, fontSize:18, color:C.white, autoFit:"shrinkText", wrap:"square", lineSpacing:1.14, insets:{top:0,right:0,bottom:0,left:0}, ...style};
  return s;
}
function img(slide, path, position, alt, crop) { return slide.images.add({blob:new Uint8Array(fsSync.readFileSync(path)), contentType:"image/png", alt, fit:"cover", position, crop}); }
function title(slide, value, position, dark=false, size=38) { return tx(slide, value, position, {fontSize:size, bold:true, color:dark?C.white:C.ink, lineSpacing:1.02}, "slide-title"); }
function body(slide, value, position, dark=false, size=20, style={}) { return tx(slide, value, position, {fontSize:size, color:dark?C.grey:"#5F6B7A", lineSpacing:1.22, ...style}); }
function header(slide, number, dark=false, section="POWERPOINT PLAYBOOK") {
  tx(slide, `AI顧問室  /  ${section}`, {left:64,top:28,width:520,height:22}, {fontSize:14,bold:true,color:dark?C.gold:C.ink});
  tx(slide, String(number).padStart(2,"0"), {left:1130,top:676,width:86,height:20}, {fontSize:14,bold:true,color:dark?C.grey:"#6D7786",alignment:"right"});
}
function line(slide, position, fill) { return rect(slide, position, fill); }
function notes(slide, extra=[], asset=false) {
  const lines = ["[Sources]", "- AI顧問室オリジナル整理。例は教材用の仮想ケースで、実測値ではありません。"];
  if (asset) lines.push("- Illustrative image generated for this deck; no external stock asset used.");
  for (const s of extra) lines.push(`- ${s}`);
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}
function newSlide(p, bg, number, dark=false, section="POWERPOINT PLAYBOOK") { const s=p.slides.add(); s.background.fill=bg; header(s,number,dark,section); return s; }
function bulletList(slide, items, x, y, width, dark=false, accent=C.mint, step=54, size=21) {
  items.forEach((item,i)=>{ rect(slide,{left:x,top:y+i*step,width:16,height:16},i===0?accent:C.mint,8); tx(slide,item,{left:x+36,top:y-5+i*step,width,height:40},{fontSize:size,bold:i===0,color:dark?C.white:C.ink}); });
}
function card(slide, label, heading, copy, position, dark=false, accent=C.gold) {
  rect(slide,position,dark?C.blue:C.paper,24,dark?C.blue2:"#DED6C6",1);
  tx(slide,label,{left:position.left+24,top:position.top+22,width:position.width-48,height:22},{fontSize:14,bold:true,color:accent});
  tx(slide,heading,{left:position.left+24,top:position.top+58,width:position.width-48,height:46},{fontSize:24,bold:true,color:dark?C.white:C.ink});
  body(slide,copy,{left:position.left+24,top:position.top+120,width:position.width-48,height:position.height-142},dark,17);
}
function sectionSlide(p, number, no, heading, copy, dark=true) {
  const s=newSlide(p,dark?C.navy:C.cream,number,dark,"POWERPOINT PLAYBOOK");
  tx(s,no,{left:72,top:120,width:240,height:170},{fontSize:150,bold:true,color:dark?C.gold:C.coral,lineSpacing:.8});
  title(s,heading,{left:370,top:172,width:790,height:110},dark,48);
  line(s,{left:370,top:320,width:190,height:6},dark?C.mint:C.gold);
  body(s,copy,{left:370,top:370,width:650,height:100},dark,24);
  tx(s,"次の章で、具体的な作り方へ",{left:370,top:552,width:520,height:28},{fontSize:18,bold:true,color:dark?C.mint:C.coral});
  notes(s,[sources.duarteStory]); return s;
}
function cover(p) {
  const s=p.slides.add(); s.background.fill=C.navy; img(s,assets.metaphor,{left:720,top:0,width:560,height:H},"AIに資料作成を任せる前に、仕事の目的を揃える様子");
  rect(s,{left:0,top:0,width:850,height:H},"#071426/94");
  rect(s,{left:72,top:94,width:10,height:190},C.gold,5);
  tx(s,"AI顧問室｜実務リードマグネット",{left:112,top:96,width:520,height:26},{fontSize:16,bold:true,color:C.gold});
  tx(s,"クオリティの高い\nPowerPointの作り方",{left:112,top:176,width:640,height:150},{fontSize:56,bold:true,color:C.white,lineSpacing:.98});
  body(s,"見た目を整える前に、伝える順番を設計する。\nAIを使っても、最後は人が判断できる資料にする。",{left:112,top:390,width:560,height:88},true,23);
  tx(s,"構成 → 根拠 → 図解 → 生成 → レビュー → 出力確認",{left:112,top:630,width:680,height:24},{fontSize:16,bold:true,color:C.mint});
  notes(s,[sources.duarteStory,sources.duarteBig,sources.microsoft,sources.accessibility],true);
}
function imageSplit(p,number,eyebrow,heading,copy,imagePath,alt,extraSources=[]) {
  const s=newSlide(p,C.cream,number,false); img(s,imagePath,{left:670,top:0,width:610,height:H},alt); rect(s,{left:0,top:0,width:735,height:H},C.cream); rect(s,{left:640,top:0,width:55,height:H},C.cream);
  tx(s,eyebrow,{left:80,top:120,width:430,height:28},{fontSize:17,bold:true,color:C.coral}); title(s,heading,{left:80,top:174,width:510,height:150},false,42); body(s,copy,{left:80,top:368,width:510,height:120},false,21); tx(s,"AI顧問室",{left:80,top:662,width:240,height:20},{fontSize:13,bold:true,color:C.ink}); notes(s,[...extraSources],true); return s;
}
function close(p,number,heading,copy) {
  const s=newSlide(p,C.navy,number,true); img(s,assets.gifts,{left:700,top:0,width:580,height:H},"AI活用の実務教材を冊子とワークブックとして見せるブックローンチ型のビジュアル"); rect(s,{left:0,top:0,width:800,height:H},"#071426/94");
  tx(s,"AI顧問室から",{left:80,top:100,width:300,height:24},{fontSize:17,bold:true,color:C.gold}); title(s,heading,{left:80,top:164,width:560,height:150},true,46); body(s,copy,{left:80,top:350,width:540,height:96},true,22); rect(s,{left:80,top:520,width:430,height:66},C.gold,33); tx(s,"無料顧問1回分を受ける",{left:100,top:541,width:390,height:24},{fontSize:21,bold:true,color:C.ink,alignment:"center"}); tx(s,"面談後、業務に合わせて教材を送付",{left:84,top:612,width:440,height:22},{fontSize:15,bold:true,color:C.mint}); notes(s,[sources.microsoft,sources.accessibility],true); return s;
}

const p=Presentation.create({slideSize:{width:W,height:H}});
cover(p);

// 02 問題提起
{ const s=imageSplit(p,2,"問題提起","きれいな資料なのに、\nなぜ決まらないのか。","情報は増えているのに、相手が理解し、判断し、動くための順番がありません。デザインは問題の解決ではなく、問題を見えやすくする鏡です。",assets.problem,"情報と修正が増え、資料作成が迷路になる様子",[sources.microsoft,sources.duarteStory]); }
{ const s=newSlide(p,C.navy,3,true); title(s,"最悪の未来は、修正のたびに主張が弱くなること",{left:72,top:102,width:940,height:90},true,38); body(s,"上司・営業・現場の要望を全部足すと、1枚のスライドに複数の結論が同居します。結果、作る時間だけが増え、会議で決めたいことが残りません。",{left:72,top:210,width:900,height:72},true,21); bulletList(s,["誰向けかがぼやける","数字の出典が後回しになる","最後に『で、何を決めたいの？』が残る"],88,350,820,true,C.coral,62,23); rect(s,{left:1010,top:330,width:150,height:150},C.red,75); tx(s,"決まらない",{left:1020,top:384,width:130,height:34},{fontSize:18,bold:true,color:C.white,alignment:"center"}); notes(s,[sources.duarteStory,sources.microsoft]); }
{ const s=newSlide(p,C.cream,4,false); title(s,"前提をそろえる：PowerPointは『絵』ではなく判断を運ぶ道具",{left:72,top:98,width:1000,height:90},false,37); body(s,"スライドは、会議室の床に置く案内板です。見る人が迷わず、次の判断へ進める情報だけを載せます。",{left:72,top:208,width:860,height:60},false,22); card(s,"たとえ","案内板","目的地、現在地、次の分岐が見える。装飾は案内を邪魔しない範囲にする。",{left:72,top:340,width:330,height:230},false,C.coral); card(s,"定義","視覚的な階層","文字の大きさ、位置、余白、色で『最初に何を見るか』を決める。",{left:470,top:340,width:330,height:230},false,C.gold); card(s,"実務例","1枚の役割","このスライドを読んだ相手に、何を理解・判断・実行してほしいかを一つにする。",{left:868,top:340,width:330,height:230},false,C.mint); notes(s,[sources.microsoft,sources.duarteStory]); }

sectionSlide(p,5,"01","伝える順番をつくる","デザイン作業は、PowerPointを開く前から始まっています。",true);
{ const s=newSlide(p,C.paper,6,false); title(s,"最初に決めるのは、読後に相手がすること",{left:72,top:100,width:920,height:80},false,39); body(s,"資料の目的を『情報を伝える』で止めず、相手の行動まで書きます。",{left:72,top:198,width:800,height:42},false,22); rect(s,{left:72,top:316,width:1136,height:150},C.navy,28); tx(s,"この資料を読んだあと、誰が、何を、いつまでに判断する？",{left:118,top:365,width:1040,height:48},{fontSize:31,bold:true,color:C.white,alignment:"center"}); tx(s,"例：経営会議で、営業部長が、来月の実験予算を承認する",{left:72,top:536,width:900,height:30},{fontSize:20,bold:true,color:C.coral}); notes(s,[sources.duarteBig]); }
{ const s=newSlide(p,C.navy,7,true); title(s,"Big Ideaは、資料全体を束ねる一文",{left:72,top:102,width:900,height:78},true,39); body(s,"テーマは『AI導入について』。Big Ideaは『まず1業務・1指標で試すと、全社展開の失敗を減らせる』。",{left:72,top:200,width:980,height:62},true,22); rect(s,{left:72,top:338,width:1136,height:150},C.gold,26); tx(s,"主張  ＋  なぜ今それが重要か  ＋  行動した先の変化",{left:120,top:385,width:1040,height:48},{fontSize:30,bold:true,color:C.ink,alignment:"center"}); tx(s,"この一文を支えないスライドは、削るか別資料へ移す。",{left:72,top:548,width:850,height:28},{fontSize:20,bold:true,color:C.mint}); notes(s,[sources.duarteBig,sources.duarteStory]); }
{ const s=newSlide(p,C.cream,8,false); title(s,"物語は『現在 → ギャップ → 未来 → 依頼』で組む",{left:72,top:100,width:1000,height:78},false,38); body(s,"ギャップとは、今の状態と望ましい状態の差です。差が見えると、なぜ行動が必要かが伝わります。",{left:72,top:196,width:980,height:50},false,20); const labels=["現在","ギャップ","未来","依頼"]; const copies=["会議のたびに資料を作り直す","判断に必要な根拠と順番がない","再利用できる型で早く決める","1業務で小さく試す"]; labels.forEach((v,i)=>{const x=84+i*282;if(i<3) rect(s,{left:x+236,top:382,width:46,height:8},C.coral); rect(s,{left:x,top:330,width:220,height:150},i===3?C.coral:C.navy,24); tx(s,v,{left:x+20,top:356,width:180,height:24},{fontSize:17,bold:true,color:i===3?C.white:C.gold,alignment:"center"}); tx(s,copies[i],{left:x+20,top:402,width:180,height:54},{fontSize:18,bold:true,color:C.white,alignment:"center"});}); notes(s,[sources.duarteStory]); }
{ const s=newSlide(p,C.paper,9,false); title(s,"ストーリーボードは、スライドの設計図",{left:72,top:100,width:900,height:78},false,38); body(s,"本文を書く前に、各ページの『結論・根拠・次の問い』だけを並べます。",{left:72,top:196,width:900,height:48},false,21); rect(s,{left:72,top:318,width:1136,height:244},C.cream,28,"#DDD6C7",1); ["01 結論","02 なぜ今","03 事実","04 例","05 選択肢","06 次の一手"].forEach((v,i)=>{const x=100+(i%3)*360,y=350+Math.floor(i/3)*92; rect(s,{left:x,top:y,width:300,height:56},i===0?C.navy:C.paper,14,"#D6CCBB",1); tx(s,v,{left:x+20,top:y+16,width:260,height:22},{fontSize:19,bold:true,color:i===0?C.white:C.ink});}); tx(s,"ページ番号ではなく、判断の順番で並べる。",{left:72,top:618,width:680,height:28},{fontSize:19,bold:true,color:C.coral}); notes(s,[sources.duarteStory,sources.titles]); }
{ const s=newSlide(p,C.navy,10,true); title(s,"根拠は、スライドの足場",{left:72,top:104,width:780,height:78},true,40); body(s,"数字・引用・事例は、出典、基準日、使ってよい範囲を一緒に管理します。",{left:72,top:204,width:900,height:50},true,21); card(s,"SOURCE LEDGER","出典台帳","URL / 資料名 / ページ / 基準日 / 主張の強さ / 再確認日",{left:72,top:332,width:500,height:220},true,C.gold); card(s,"意味","主張の強さ","事実・推定・仮説を分ける。AIに空白を埋めさせない。",{left:622,top:332,width:500,height:220},true,C.mint); notes(s,[sources.microsoft,sources.accessibility]); }
{ const s=newSlide(p,C.cream,11,false); title(s,"事実・推定・仮説を、同じ見た目にしない",{left:72,top:100,width:920,height:78},false,38); body(s,"確度の違いをラベルと文章で明示すると、読み手は安心して次の判断に進めます。",{left:72,top:198,width:980,height:48},false,21); card(s,"FACT","事実","社内の実績、公開資料、確認済みの数値。出典と基準日を付ける。",{left:72,top:326,width:340,height:228},false,C.mint); card(s,"ESTIMATE","推定","仮の計算や見込み。前提と幅を明示し、断定しない。",{left:470,top:326,width:340,height:228},false,C.gold); card(s,"HYPOTHESIS","仮説","まだ検証していない説明。小さな実験で確かめる。",{left:868,top:326,width:340,height:228},false,C.coral); notes(s,[sources.microsoft]); }

sectionSlide(p,12,"02","1枚の役割を決める","情報を足すより先に、見る順番と1枚の仕事を決めます。",false);
{ const s=newSlide(p,C.navy,13,true); title(s,"1枚1メッセージは、情報を減らす技術",{left:72,top:100,width:950,height:78},true,39); body(s,"1枚に結論が3つあると、読み手は自分で優先順位を作らなければなりません。",{left:72,top:198,width:980,height:50},true,21); rect(s,{left:72,top:330,width:430,height:190},C.red,24); tx(s,"Before",{left:100,top:360,width:150,height:24},{fontSize:16,bold:true,color:C.white}); tx(s,"情報を全部載せる\n結論が3つ\n視線が迷う",{left:100,top:404,width:360,height:94},{fontSize:26,bold:true,color:C.white,lineSpacing:1.25}); rect(s,{left:660,top:330,width:430,height:190},C.mint,24); tx(s,"After",{left:688,top:360,width:150,height:24},{fontSize:16,bold:true,color:C.ink}); tx(s,"結論を1つにする\n根拠は2つまで\n視線が進む",{left:688,top:404,width:360,height:94},{fontSize:26,bold:true,color:C.ink,lineSpacing:1.25}); notes(s,[sources.microsoft,sources.duarteStory]); }
{ const s=newSlide(p,C.paper,14,false); title(s,"レイアウトは、内容に合わせて選ぶ",{left:72,top:100,width:900,height:78},false,39); body(s,"毎回同じ箱を並べるのではなく、内容の関係に合う型を使います。",{left:72,top:198,width:900,height:48},false,21); const items=[["HERO","強い1メッセージ"],["COMPARE","違いを見せる"],["PROCESS","順番を見せる"],["WORKSHEET","手を動かす"]]; items.forEach((it,i)=>{const x=74+i*285; rect(s,{left:x,top:330,width:245,height:170},i===0?C.navy:C.cream,22,"#D8D0C1",1); tx(s,it[0],{left:x+22,top:354,width:200,height:22},{fontSize:14,bold:true,color:i===0?C.gold:C.coral}); tx(s,it[1],{left:x+22,top:396,width:200,height:58},{fontSize:23,bold:true,color:i===0?C.white:C.ink});}); notes(s,[sources.designer,sources.microsoft]); }
{ const s=newSlide(p,C.cream,15,false); title(s,"図解は、関係を見えるようにする",{left:72,top:100,width:900,height:78},false,39); body(s,"図形を増やすのではなく、『順番』『比較』『分岐』『重なり』のどれを伝えるか決めます。",{left:72,top:198,width:1000,height:50},false,20); const labels=["順番","比較","分岐","重なり"]; const desc=["工程・ロードマップ","Before / After・選択肢","条件・判断フロー","役割・レイヤー"]; labels.forEach((v,i)=>{const x=96+i*270; rect(s,{left:x,top:340,width:210,height:145},i%2?C.navy:C.paper,20,"#D8D0C1",1); tx(s,v,{left:x+20,top:366,width:170,height:32},{fontSize:26,bold:true,color:i%2?C.white:C.ink,alignment:"center"}); tx(s,desc[i],{left:x+20,top:422,width:170,height:40},{fontSize:16,color:i%2?C.grey:"#5F6B7A",alignment:"center"});}); notes(s,[sources.designer,sources.duarteStory]); }
{ const s=imageSplit(p,16,"比喩","AIに任せる前に、\n『優秀な新人』として扱う","AIは速く下書きを作れますが、社内事情・例外・顧客との約束を自動では知りません。前提、禁止事項、完成条件を渡すほど安定します。",assets.metaphor,"人がAIに手順書を渡している編集イラスト",[sources.openai,sources.openaiApi]); }
{ const s=newSlide(p,C.navy,17,true); title(s,"写真は、主張を説明するために使う",{left:72,top:102,width:900,height:78},true,39); body(s,"写真を置くだけでは、視線は動いても理解は進みません。画像の役割を1つ決めます。",{left:72,top:200,width:980,height:48},true,21); const rows=["状況を見せる","感情をつくる","比喩を置く"]; const desc=["現場・人物・場所で、今の状態を伝える","変化の大きさや緊張感を伝える","複雑な概念を、身近な物に置き換える"]; rows.forEach((v,i)=>{const y=330+i*78; tx(s,String(i+1).padStart(2,"0"),{left:90,top:y+4,width:50,height:30},{fontSize:20,bold:true,color:C.gold}); tx(s,v,{left:170,top:y,width:240,height:32},{fontSize:24,bold:true,color:C.white}); tx(s,desc[i],{left:450,top:y+3,width:680,height:32},{fontSize:19,color:C.grey});}); notes(s,[sources.microsoft]); }
{ const s=newSlide(p,C.paper,18,false); title(s,"Before / Afterは、差分を1つに絞る",{left:72,top:100,width:900,height:78},false,39); body(s,"比較スライドでは、色・位置・数値のすべてで差を作らず、何が変わったかを一つ強調します。",{left:72,top:198,width:1000,height:50},false,20); rect(s,{left:72,top:328,width:500,height:210},C.cream,24,"#D8D0C1",1); tx(s,"Before｜会議前",{left:108,top:360,width:320,height:28},{fontSize:21,bold:true,color:C.ink}); tx(s,"資料を毎回ゼロから作る\n判断材料が散らばる",{left:108,top:420,width:380,height:70},{fontSize:24,bold:true,color:C.red,lineSpacing:1.2}); rect(s,{left:708,top:328,width:500,height:210},C.navy,24); tx(s,"After｜型を使う",{left:744,top:360,width:320,height:28},{fontSize:21,bold:true,color:C.gold}); tx(s,"結論から並べる\n根拠と次の一手が残る",{left:744,top:420,width:380,height:70},{fontSize:24,bold:true,color:C.mint,lineSpacing:1.2}); notes(s,[sources.duarteStory,sources.microsoft]); }
{ const s=newSlide(p,C.cream,19,false); title(s,"チャートは、問いに答えるために選ぶ",{left:72,top:100,width:920,height:78},false,39); body(s,"『何が多いか』『どう変わったか』『何が関係するか』で、向くチャートが変わります。",{left:72,top:198,width:1020,height:48},false,20); const items=[["比較","棒グラフ","項目の差"],["推移","折れ線","時間の変化"],["構成","積み上げ","全体の内訳"],["関係","散布図","2つの指標"]]; items.forEach((it,i)=>{const x=74+i*285; rect(s,{left:x,top:330,width:245,height:178},i===1?C.navy:C.paper,20,"#D8D0C1",1); tx(s,it[0],{left:x+22,top:354,width:200,height:22},{fontSize:15,bold:true,color:i===1?C.gold:C.coral}); tx(s,it[1],{left:x+22,top:394,width:200,height:32},{fontSize:27,bold:true,color:i===1?C.white:C.ink}); tx(s,it[2],{left:x+22,top:448,width:200,height:22},{fontSize:17,color:i===1?C.grey:"#5F6B7A"});}); notes(s,[sources.microsoft]); }
{ const s=newSlide(p,C.navy,20,true); title(s,"数字を置くなら、まず『だから何？』を書く",{left:72,top:102,width:980,height:78},true,39); body(s,"数値の羅列ではなく、見る人が持ち帰る意味をタイトルにします。",{left:72,top:200,width:900,height:48},true,21); rect(s,{left:72,top:330,width:500,height:180},C.blue,24,C.blue2,1); tx(s,"売上推移",{left:110,top:362,width:240,height:28},{fontSize:22,bold:true,color:C.white}); tx(s,"2024  100\n2025  120\n2026  125",{left:110,top:416,width:250,height:76},{fontSize:24,color:C.grey,lineSpacing:1.15}); rect(s,{left:700,top:330,width:500,height:180},C.gold,24); tx(s,"伸びは続くが、速度は鈍化",{left:738,top:362,width:420,height:34},{fontSize:24,bold:true,color:C.ink}); tx(s,"→ 次に確認するのは、\n新規と既存のどちらが要因か",{left:738,top:418,width:420,height:64},{fontSize:22,bold:true,color:C.ink,lineSpacing:1.2}); notes(s,[sources.microsoft,sources.duarteStory]); }
{ const s=newSlide(p,C.paper,21,false); title(s,"読みやすさは、デザインより先に守る",{left:72,top:100,width:900,height:78},false,39); body(s,"美しさは、読めることの上に乗ります。遠くから見ても、白黒にしても、順番が伝わるか確認します。",{left:72,top:198,width:1000,height:50},false,20); bulletList(s,["18pt以上を目安に、短い行で書く","背景と文字のコントラストを確保する","色だけに意味を持たせず、ラベルでも分ける","各スライドに固有のタイトルを付ける"],90,328,960,false,C.coral,54,21); notes(s,[sources.accessibility,sources.titles,sources.microsoft]); }
{ const s=newSlide(p,C.cream,22,false); title(s,"余白は、何もない場所ではなく順番をつくる場所",{left:72,top:100,width:1050,height:78},false,38); body(s,"要素の間隔を揃えると、読み手は『同じグループ』『次のグループ』を無意識に判別できます。",{left:72,top:198,width:980,height:48},false,20); rect(s,{left:72,top:330,width:470,height:160},C.paper,22,"#D8D0C1",1); tx(s,"詰め込む",{left:100,top:354,width:180,height:24},{fontSize:18,bold:true,color:C.red}); tx(s,"見出し\n説明\n数字\n注釈",{left:100,top:402,width:360,height:70},{fontSize:22,color:C.ink,lineSpacing:.9}); rect(s,{left:700,top:330,width:470,height:160},C.navy,22); tx(s,"呼吸させる",{left:728,top:354,width:180,height:24},{fontSize:18,bold:true,color:C.gold}); tx(s,"見出し\n\n説明        数字",{left:728,top:402,width:360,height:70},{fontSize:22,color:C.white,lineSpacing:1.05}); notes(s,[sources.accessibility,sources.microsoft]); }

sectionSlide(p,23,"03","AIに作らせる前に、工程を分ける","AIは便利な作業者。編集長の役割まで渡さない。",true);
{ const s=imageSplit(p,24,"AI WORKFLOW","AIに任せる範囲を、\n工程で切り分ける","AIには下書き、分類、候補出しを任せます。人は目的、事実、優先順位、最終承認を持ちます。",assets.workflow,"AIを使った業務工程と、人の確認ポイントを示すイラスト",[sources.openai,sources.openaiApi]); }
{ const s=newSlide(p,C.paper,25,false); title(s,"PowerPoint生成の前に、構成を出させる",{left:72,top:100,width:960,height:78},false,39); body(s,"いきなり『30枚作って』ではなく、まず章立てと各ページの役割を確認します。",{left:72,top:198,width:980,height:48},false,20); rect(s,{left:72,top:324,width:1136,height:244},C.navy,26); tx(s,"あなたは資料編集者です。\n目的 / 対象 / 相手にしてほしい判断 / 根拠 / 制約を読み、\n先に章立てと各スライドの結論を表で出してください。\n未確認の数字は作らず、『要確認』として残してください。",{left:112,top:356,width:1040,height:170},{fontSize:24,color:C.white,lineSpacing:1.22}); notes(s,[sources.openai,sources.openaiApi]); }
{ const s=newSlide(p,C.cream,26,false); title(s,"1枚分の指示には、完成条件まで入れる",{left:72,top:100,width:960,height:78},false,39); body(s,"役割・背景・入力・出力だけでなく、禁止事項と確認方法まで渡すと修正が減ります。",{left:72,top:198,width:1000,height:48},false,20); rect(s,{left:72,top:320,width:1136,height:260},C.paper,26,"#D8D0C1",1); const rows=[["役割","誰として考えるか"],["背景","何の判断につなげるか"],["出力","どんな構成・長さか"],["条件","使ってよい根拠・禁止事項"],["確認","人が何をチェックするか"]]; rows.forEach((r,i)=>{const y=346+i*43; tx(s,r[0],{left:106,top:y,width:90,height:22},{fontSize:18,bold:true,color:C.coral}); tx(s,r[1],{left:236,top:y,width:700,height:22},{fontSize:18,color:C.ink});}); notes(s,[sources.openai,sources.openaiApi]); }
{ const s=newSlide(p,C.navy,27,true); title(s,"AIの出力は、最初から採用するものではない",{left:72,top:100,width:1000,height:78},true,39); body(s,"レビュー用の指示を別に持ち、事実・論理・視認性・アクセシビリティを順に点検します。",{left:72,top:198,width:1000,height:48},true,20); const checks=["事実：出典と基準日はあるか","論理：結論と根拠はつながるか","視認性：3秒で主張が見えるか","利用性：PDF・投影・読み上げで壊れないか"]; checks.forEach((v,i)=>{const y=320+i*60; rect(s,{left:90,top:y,width:20,height:20},i===0?C.gold:C.mint,10); tx(s,v,{left:140,top:y-3,width:860,height:30},{fontSize:22,bold:i===0,color:C.white});}); notes(s,[sources.accessibility,sources.microsoft,sources.openai]); }
{ const s=newSlide(p,C.paper,28,false); title(s,"生成・編集・確認を、別のパスにする",{left:72,top:100,width:900,height:78},false,39); body(s,"一度に全部を直そうとせず、役割ごとに見ると、直すべき場所が明確になります。",{left:72,top:198,width:980,height:48},false,20); const steps=["1 構成","2 コピー","3 ビジュアル","4 事実","5 出力"]; steps.forEach((v,i)=>{const x=82+i*225; if(i<4) rect(s,{left:x+158,top:398,width:54,height:7},C.coral); rect(s,{left:x,top:350,width:170,height:100},i===4?C.coral:C.navy,22); tx(s,v,{left:x+14,top:387,width:142,height:24},{fontSize:21,bold:true,color:i===4?C.white:C.gold,alignment:"center"});}); notes(s,[sources.microsoft,sources.accessibility]); }
{ const s=newSlide(p,C.navy,29,true); title(s,"PPTXとPDFは、最後に実ファイルで確認する",{left:72,top:100,width:1000,height:78},true,39); body(s,"編集画面で見えていても、書き出し後にフォント、画像、改行、リンク、余白が変わることがあります。",{left:72,top:198,width:1020,height:48},true,20); card(s,"PPTX","編集できる状態","フォント、画像、配置、読み上げ順、リンク、ノートを確認。",{left:72,top:328,width:500,height:210},true,C.gold); card(s,"PDF","配布できる状態","ページ端の欠け、文字のにじみ、アクセシビリティタグ、ファイル容量を確認。",{left:700,top:328,width:500,height:210},true,C.mint); notes(s,[sources.accessibility,sources.microsoft]); }
{ const s=newSlide(p,C.cream,30,false); title(s,"提出前は、3つの距離で見る",{left:72,top:100,width:900,height:78},false,39); body(s,"近くで編集し、少し離れて読み、実際の投影・共有環境で確かめます。",{left:72,top:198,width:980,height:48},false,20); const items=[["近い","誤字・数字・揃え"],["中間","視線の順番・情報量"],["遠い","文字サイズ・コントラスト・端切れ"]]; items.forEach((it,i)=>{const x=90+i*370; rect(s,{left:x,top:330,width:300,height:170},i===2?C.coral:C.navy,24); tx(s,it[0],{left:x+26,top:360,width:240,height:28},{fontSize:18,bold:true,color:i===2?C.white:C.gold,alignment:"center"}); tx(s,it[1],{left:x+26,top:418,width:240,height:52},{fontSize:22,bold:true,color:C.white,alignment:"center"});}); notes(s,[sources.microsoft,sources.accessibility]); }
{ const s=newSlide(p,C.paper,31,false); title(s,"最後に、1枚ずつ『残す理由』を言えるか",{left:72,top:100,width:1000,height:78},false,39); body(s,"資料の質は、追加した要素の数ではなく、必要な要素だけを残す判断で決まります。",{left:72,top:198,width:980,height:48},false,20); rect(s,{left:72,top:330,width:1136,height:190},C.navy,26); tx(s,"このスライドは、相手の判断にどう役立つ？",{left:128,top:386,width:1024,height:44},{fontSize:31,bold:true,color:C.white,alignment:"center"}); tx(s,"答えられないなら、削る・移す・作り直す。",{left:128,top:454,width:1024,height:28},{fontSize:20,bold:true,color:C.mint,alignment:"center"}); notes(s,[sources.duarteBig,sources.microsoft]); }
close(p,32,"資料づくりを、\n属人的な作業から仕組みへ","AIを使うほど、目的・根拠・レビューの型が重要になります。無料顧問1回分の面談後、あなたの業務や資料用途に合わせた教材を送付します。");

await fs.mkdir(PREVIEW,{recursive:true});
async function writeBlob(path,blob){await fs.writeFile(path,new Uint8Array(await blob.arrayBuffer()));}
for (const [i,s] of p.slides.items.entries()) { await writeBlob(`${PREVIEW}/slide-${String(i+1).padStart(2,"0")}.png`, await p.export({slide:s,format:"png",scale:1})); }
await writeBlob(`${PREVIEW}/montage.webp`, await p.export({format:"webp",montage:true,scale:1}));
const pptx=await PresentationFile.exportPptx(p); await pptx.save(OUT);
console.log(JSON.stringify({output:OUT,slides:p.slides.items.length},null,2));
