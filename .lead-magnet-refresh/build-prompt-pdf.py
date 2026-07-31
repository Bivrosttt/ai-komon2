import json, os
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

ROOT = "/Users/koki/Desktop/ai-komon2"
OUT = f"{ROOT}/materials/ai-komon-prompt-100-field-guide.pdf"
DATA = f"{ROOT}/.lead-magnet-refresh/prompts.json"
GIFT = "/Users/koki/.codex/generated_images/019f9da0-a334-7a60-9a87-f9e6a3a57afa/exec-51c9ca12-1074-4e64-90e6-b1d634866745.png"
W, H = A4
NAVY, BLUE = colors.HexColor("#071426"), colors.HexColor("#102946")
CREAM, PAPER = colors.HexColor("#F7F1E7"), colors.HexColor("#FFFDF9")
INK, MUTED = colors.HexColor("#142238"), colors.HexColor("#68768A")
GOLD, MINT, CORAL = colors.HexColor("#E8B94A"), colors.HexColor("#74D6C6"), colors.HexColor("#F58A6D")
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
FONT = "HeiseiKakuGo-W5"
with open(DATA, encoding="utf-8") as f: prompts = json.load(f)

def P(name, size, leading, color): return ParagraphStyle(name, fontName=FONT, fontSize=size, leading=leading, textColor=color, wordWrap="CJK")
BODY, SMALL = P("body",11.5,17,INK), P("small",9.5,13,MUTED)

def para(c, text, style, x, top, width, height):
    p=Paragraph(text,style); _, h=p.wrap(width,height); p.drawOn(c,x,top-h); return h

def hf(c, page, dark=False):
    c.saveState(); c.setFont(FONT,8.5); c.setFillColor(GOLD if dark else INK)
    c.drawString(18*mm,H-14*mm,"AI顧問室  /  実務で使えるパターン別プロンプト集100選")
    c.setFillColor(colors.HexColor("#9AA6B6") if dark else MUTED); c.drawRightString(W-18*mm,12*mm,f"{page:03d}"); c.restoreState()

def cover(c):
    c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
    try:
        c.drawImage(ImageReader(GIFT), W*.52,0,width=W*.48,height=H,preserveAspectRatio=True,mask="auto",anchor="c")
        c.setFillColor(colors.Color(.027,.078,.149,alpha=.88)); c.rect(0,0,W*.62,H,fill=1,stroke=0)
    except Exception: pass
    c.setFillColor(GOLD); c.roundRect(18*mm,H-47*mm,4*mm,28*mm,2*mm,fill=1,stroke=0)
    c.setFont(FONT,12); c.drawString(29*mm,H-33*mm,"AI顧問室｜実務リードマグネット")
    para(c,"実務で使える<br/>パターン別プロンプト集<br/>100選",P("cover",29,38,colors.white),29*mm,H-54*mm,90*mm,95*mm)
    para(c,"営業、顧客対応、会議、採用、バックオフィス、経営企画まで。<br/>入力欄を埋めて、そのまま仕事の下書きに使える形にしています。",SMALL,29*mm,94*mm,91*mm,40*mm)
    c.setFillColor(MINT); c.setFont(FONT,10); c.drawString(29*mm,25*mm,"10カテゴリ × 10パターン  /  説明つき・コピペ用"); c.showPage()

def intro(c):
    c.setFillColor(CREAM); c.rect(0,0,W,H,fill=1,stroke=0); hf(c,2)
    para(c,"この本の使い方",P("title",24,31,INK),18*mm,H-32*mm,170*mm,20*mm)
    para(c,"プロンプトは、呪文ではなく仕事の依頼書です。<br/>誰として、何のために、どんな条件で、どんな形にするかを渡すと、出力を確認しやすくなります。",BODY,18*mm,H-58*mm,170*mm,38*mm)
    rows=[("01","目的を決める","何を終わらせたいかを1文にする"),("02","入力欄を埋める","[[  ]] の部分を自社の情報に置き換える"),("03","出力を読む","事実、推測、抜けを人が確認する"),("04","自社の型にする","よく使うものをチームのテンプレに保存する")]
    y=H-110*mm
    for no,head,copy in rows:
        c.setFillColor(NAVY); c.roundRect(18*mm,y-20*mm,16*mm,16*mm,8*mm,fill=1,stroke=0); c.setFillColor(GOLD); c.setFont(FONT,10); c.drawCentredString(26*mm,y-14*mm,no)
        para(c,head,P("h",15,19,INK),42*mm,y,48*mm,12*mm); para(c,copy,SMALL,93*mm,y,85*mm,14*mm); y-=25*mm
    c.setFillColor(BLUE); c.roundRect(18*mm,30*mm,170*mm,30*mm,6*mm,fill=1,stroke=0); para(c,"注意：機密情報、個人情報、未確認の数字はそのまま入力せず、匿名化・要確認化してから使ってください。",P("warn",10,14,colors.white),25*mm,52*mm,156*mm,22*mm); c.showPage()

def structure(c):
    c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0); hf(c,3)
    para(c,"良い依頼は、6つの部品でできている",P("title2",24,31,INK),18*mm,H-32*mm,170*mm,20*mm)
    para(c,"毎回すべてを長く書く必要はありません。迷ったら、この順番で足します。",BODY,18*mm,H-58*mm,170*mm,20*mm)
    parts=[("役割","誰として考えるか"),("背景","何のために使うか"),("入力","何を材料にするか"),("依頼","何を作るか"),("条件","守るルール"),("出力","どんな形か")]
    for i,(a,b) in enumerate(parts):
        x=18*mm+(i%2)*88*mm; y=H-100*mm-(i//2)*31*mm; dark=i%2==0
        c.setFillColor(NAVY if dark else CREAM); c.roundRect(x,y-20*mm,78*mm,23*mm,5*mm,fill=1,stroke=0)
        para(c,a,P("part",14,18,GOLD if dark else CORAL),x+6*mm,y-4*mm,25*mm,10*mm); para(c,b,P("part2",11,14,colors.white if dark else INK),x+32*mm,y-4*mm,40*mm,12*mm)
    c.setFillColor(CORAL); c.setFont(FONT,12); c.drawString(18*mm,54*mm,"この本のプロンプトは、すべてこの考え方で設計しています。"); c.showPage()

def contents(c):
    c.setFillColor(CREAM); c.rect(0,0,W,H,fill=1,stroke=0); hf(c,4); para(c,"目次",P("title3",24,31,INK),18*mm,H-32*mm,170*mm,20*mm)
    cats=[]
    for item in prompts:
        if item["category"] not in cats: cats.append(item["category"])
    y=H-62*mm
    for i,cat in enumerate(cats):
        c.setFillColor(NAVY if i%2==0 else BLUE); c.roundRect(18*mm,y-11*mm,170*mm,10*mm,3*mm,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont(FONT,11); c.drawString(24*mm,y-7*mm, f"{i+1:02d}  {cat}"); c.setFillColor(GOLD); c.drawRightString(181*mm,y-7*mm,f"No.{i*10+1:03d} - {i*10+10:03d}"); y-=15*mm
    para(c,"Web版では、カテゴリとキーワードで検索し、プロンプトをコピーできます。",SMALL,18*mm,38*mm,170*mm,15*mm); c.showPage()

def prompt_page(c,item,page):
    dark=item["id"]%2==0; c.setFillColor(NAVY if dark else PAPER); c.rect(0,0,W,H,fill=1,stroke=0); hf(c,page,dark); accent=GOLD if dark else CORAL
    c.setFillColor(accent); c.setFont(FONT,10); c.drawString(18*mm,H-31*mm,item["category"]); c.drawRightString(W-18*mm,H-31*mm,f"No.{item['id']:03d}")
    para(c,escape(item["title"]),P("ptitle",22,28,colors.white if dark else INK),18*mm,H-43*mm,170*mm,27*mm)
    para(c,escape(item["description"]),P("pdesc",11.5,16,colors.HexColor("#AAB6C6") if dark else MUTED),18*mm,H-69*mm,170*mm,20*mm)
    c.setFillColor(BLUE if dark else CREAM); c.roundRect(18*mm,42*mm,170*mm,104*mm,6*mm,fill=1,stroke=0); c.setFillColor(MINT if dark else CORAL); c.setFont(FONT,9.5); c.drawString(25*mm,137*mm,"PROMPT  /  入力欄を埋めて使う")
    html=escape(item["prompt"]).replace("\n","<br/>"); p=Paragraph(html,P("prompt",10.3,14.2,colors.white if dark else INK)); _,ph=p.wrap(156*mm,88*mm); p.drawOn(c,25*mm,132*mm-ph)
    c.setFillColor(accent); c.setFont(FONT,9); c.drawString(18*mm,30*mm,"使う前に：機密情報は匿名化し、出力の事実と推測を確認する"); c.setFillColor(colors.HexColor("#7D8A9C") if dark else MUTED); c.setFont(FONT,8.5); c.drawRightString(W-18*mm,30*mm,"  ".join("#"+x for x in item.get("tags",[]))[:100]); c.showPage()

os.makedirs(os.path.dirname(OUT),exist_ok=True); c=canvas.Canvas(OUT,pagesize=A4); cover(c); intro(c); structure(c); contents(c)
for i,item in enumerate(prompts,start=5): prompt_page(c,item,i)
c.save(); print(json.dumps({"output":OUT,"pages":4+len(prompts)},ensure_ascii=False))
