# -*- coding: utf-8 -*-
"""A/B/C の絵コンテ SVG を生成（構図ラフ）。ボトルは矩形＋ラベル枠の記号で表現し、ラベル内容は描かない（改変禁止のため）。"""
import html
BL="#FDCBD7"; PT="#FCDDE5"; MW="#FFF8F6"; CH="#6A6664"; RS="#C12844"; DK="#3a3535"

def bottle(x,y,w,h,tilt=0):
    cx=x+w/2; cy=y+h/2
    return f'''<g transform="rotate({tilt} {cx} {cy})">
  <rect x="{x+w*0.36}" y="{y-h*0.16}" width="{w*0.28}" height="{h*0.16}" rx="3" fill="#fff" stroke="{CH}" stroke-width="1"/>
  <rect x="{x+w*0.30}" y="{y-h*0.26}" width="{w*0.34}" height="{h*0.06}" rx="3" fill="#fff" stroke="{CH}" stroke-width="1"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{CH}" stroke-width="1.2"/>
  <rect x="{x+w*0.14}" y="{y+h*0.12}" width="{w*0.72}" height="{h*0.76}" fill="none" stroke="{CH}" stroke-width="0.8" stroke-dasharray="3 3"/>
  <text x="{cx}" y="{y+h*0.52}" font-size="9" fill="{CH}" text-anchor="middle" font-family="sans-serif">正式画像</text>
</g>'''

def frame(ix, title, bg, elems, caption, note, dark=False):
    W,H=216,384; x0=ix*(W+24)+16; y0=40
    tc = MW if dark else CH
    s=f'<g transform="translate({x0},{y0})">'
    s+=f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="{bg}" stroke="{CH}" stroke-width="1"/>'
    # safe zones
    s+=f'<rect x="0" y="0" width="{W}" height="{H*220/1920}" fill="#c12844" opacity="0.10"/>'
    s+=f'<rect x="0" y="{H-H*430/1920}" width="{W}" height="{H*430/1920}" fill="#c12844" opacity="0.10"/>'
    s+=f'<rect x="{W-W*120/1080}" y="0" width="{W*120/1080}" height="{H}" fill="#c12844" opacity="0.10"/>'
    s+=elems
    if caption:
        s+=f'<text x="{W/2}" y="{H*0.62}" font-size="10.5" fill="{tc}" text-anchor="middle" font-family="sans-serif">{html.escape(caption)}</text>'
    s+=f'<text x="0" y="-8" font-size="11" font-weight="bold" fill="{CH}" font-family="sans-serif">{html.escape(title)}</text>'
    # note wrap
    lines=[note[i:i+22] for i in range(0,len(note),22)][:4]
    for k,l in enumerate(lines):
        s+=f'<text x="0" y="{H+18+k*13}" font-size="9.5" fill="{CH}" font-family="sans-serif">{html.escape(l)}</text>'
    s+='</g>'; return s

def person_leg(x,y,scale=1):
    return f'<path d="M{x} {y} q {30*scale} {-40*scale} {90*scale} {-20*scale}" stroke="#e7b7a6" stroke-width="{18*scale}" fill="none" stroke-linecap="round"/>'
def hand(x,y,r=14):
    return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.7}" fill="#e7b7a6" opacity="0.9"/>'
def lamp(x,y,on=True):
    c="#ffd9a0" if on else "#7a6a5a"
    return f'<circle cx="{x}" cy="{y}" r="16" fill="{c}" opacity="0.9"/><rect x="{x-3}" y="{y+16}" width="6" height="28" fill="{CH}"/>'
def text(x,y,t,size=12,col=CH,fam="serif",anchor="middle"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-family="{fam}">{html.escape(t)}</text>'
def bokeh(pts):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd9a0" opacity="0.35"/>' for x,y,r in pts)

def doc(title, frames, w):
    body="".join(frames)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="520" viewBox="0 0 {w} 520" font-family="sans-serif">
<rect width="100%" height="100%" fill="{MW}"/>
<text x="16" y="22" font-size="14" font-weight="bold" fill="{CH}">{html.escape(title)}</text>
<text x="{w-16}" y="22" font-size="10" fill="{CH}" text-anchor="end">赤帯＝UIセーフゾーン外（上220/下430/右120px）。ボトルは記号表示、実際は正式画像を改変なしで使用。</text>
{body}
</svg>'''

# ---- A ----
A=[]
A.append(frame(0,"A#1 0.0–1.4 玄関POV",DK,
  f'<rect x="0" y="0" width="60" height="384" fill="#b58a5a" opacity="0.25"/>{hand(110,300)}{hand(140,290,10)}<path d="M95 330 l40 -10 l30 12" stroke="#a88" stroke-width="6" fill="none"/>',
  "", "ストラップを外す手元。床の光だけ。SE：カッ", dark=True))
A.append(frame(1,"A#2 1.4–2.6 足元",DK,
  f'<path d="M60 300 q 50 -30 100 0 q -50 40 -100 0z" fill="#e7b7a6"/>',"", "素足が床に。ため息。暖色寄り", dark=True))
A.append(frame(2,"A#3 2.6–4.4 点灯",PT,
  f'{lamp(170,90)}{hand(160,120)}<rect x="0" y="0" width="216" height="384" fill="{DK}" opacity="0.35"/>',
  "今日、何時間立ってた？", "手持ち追従。カチッで暖色。BGM IN"))
A.append(frame(3,"A#4 4.4–6.2 座る",BL,
  f'{person_leg(20,300)}<rect x="130" y="250" width="70" height="8" fill="{MW}"/>{bottle(150,200,32,52)}',
  "靴、脱いだ。", "膝下のみ。ボトル初出（右1/3・正対）"))
A.append(frame(4,"A#5 6.2–7.6 ポンプ",BL,
  f'{bottle(88,150,40,66)}{hand(108,240,22)}<circle cx="108" cy="228" r="7" fill="#fff"/>',
  "", "60fps→50%。置いたまま押す。SE：しゅ・とろ"))
A.append(frame(5,"A#6 7.6–10.4 ほぐほぐ",BL,
  f'{person_leg(10,320,1.6)}{hand(90,262,16)}{hand(130,250,16)}{bokeh([(180,60,10),(150,40,7)])}',
  "今日は、ここまで。", "両手で包む。1往復2.5秒。強く押さない"))
A.append(frame(6,"A#7 10.4–12.4 顔",BL,
  f'{bokeh([(170,60,12),(190,110,8),(150,30,6)])}<circle cx="120" cy="120" r="34" fill="#f0c9b8"/><path d="M106 124 q14 8 28 0" stroke="{CH}" stroke-width="1.5" fill="none"/><path d="M108 112 h10 M130 112 h10" stroke="{CH}" stroke-width="1.5"/>',
  "明日の私に、ちょっとだけ。", "唯一の顔。目を閉じ→開けて小さく笑う。45°"))
A.append(frame(7,"A#8–9 12.4–15.0 締め",BL,
  f'{lamp(60,80)}{bottle(90,170,40,66)}'+text(108,140,"Coming back soon",13,RS),
  "", "ボトル静止、push-in 3%。英語 Rose 96px。ロゴは出さない"))
open("04_scripts/storyboards/A_storyboard.svg","w",encoding="utf-8").write(doc("案A「靴、脱いだ。」絵コンテ（構図ラフ）",A,8*240+16))

# ---- B ----
B=[]
B.append(frame(0,"B#1 0.0–0.8 黒",DK,f'{lamp(170,70,False)}{hand(150,110,12)}',"", "ほぼ黒（Charcoal 5%）。手がランプへ", dark=True))
B.append(frame(1,"B#2 0.8–2.4 点灯→ボトル",BL,
  f'{lamp(160,90)}<rect x="0" y="260" width="216" height="124" fill="{MW}"/>{bottle(70,190,42,70)}<rect x="30" y="230" width="20" height="26" fill="#fff" stroke="{CH}" stroke-width="0.8"/><circle cx="40" cy="228" r="4" fill="#ffd9a0"/><ellipse cx="170" cy="245" rx="22" ry="8" fill="#fff" stroke="{CH}" stroke-width="0.8"/>',
  "", "正式画像01の構図を再現。ボトル初出0.8秒。SE：カチッ"))
B.append(frame(2,"B#3 2.4–4.6 ポンプ",BL,f'{bottle(88,120,40,66)}{hand(108,225,24)}<circle cx="108" cy="210" r="8" fill="#fff"/>',
  "夜の3分。", "60fps→40%。しゅ→とろ。テロップ3.0秒IN"))
B.append(frame(3,"B#4 4.6–6.4 手のひら",BL,f'{hand(80,200,34)}{hand(136,200,34)}<ellipse cx="108" cy="200" rx="14" ry="9" fill="#fff"/>',
  "", "マクロ。白飛び注意 −0.3EV"))
B.append(frame(4,"B#5 6.4–9.6 ふくらはぎ",BL,f'{person_leg(10,320,1.6)}{hand(90,262,16)}{hand(130,250,16)}{bokeh([(180,60,10)])}',
  "", "包む。親指で円。60%スロー。1往復"))
B.append(frame(5,"B#6 9.6–11.4 足首→甲",BL,f'<path d="M40 260 q 60 -20 130 10 q -60 30 -130 0z" fill="#e7b7a6"/>{hand(120,262,14)}',
  "今日より明日。", "指先まで、手を離す。ラベルと同じ言葉"))
B.append(frame(6,"B#7 11.4–12.8 ティー",BL,
  f'<g opacity="0.45">{bottle(150,150,30,50)}</g><ellipse cx="90" cy="230" rx="30" ry="12" fill="#f3e2a8"/><rect x="60" y="200" width="60" height="30" fill="none" stroke="{CH}"/>{hand(60,245,14)}<path d="M85 190 q5 -10 0 -20 M95 190 q5 -10 0 -20" stroke="#ccc" fill="none"/>',
  "", "カップ中央、湯気。ボトルは奥ボケ（形は正しく）"))
B.append(frame(7,"B#8–9 12.8–15.0 消灯→英語",DK,
  f'<g opacity="0.15">{bottle(88,240,40,66)}</g>'+text(108,150,"Stay tuned",15,MW),
  "", "カチッで暗転。英語 Milk White 92px。ボトルの影8%", dark=True))
open("04_scripts/storyboards/B_storyboard.svg","w",encoding="utf-8").write(doc("案B「夜の3分 ASMR」絵コンテ（構図ラフ）",B,8*240+16))

# ---- C ----
def bubble(t):
    return f'<rect x="18" y="58" width="180" height="40" rx="10" fill="#fff" opacity="0.92" stroke="{CH}" stroke-width="0.6"/><circle cx="34" cy="78" r="8" fill="{BL}"/>'+text(112,82,t,8.5,CH,"sans-serif")
C=[]
C.append(frame(0,"C#1 0.0–1.6 吹き出し",BL,f'{bubble("見つけたと思ったら売り切れてた、、、")}{bottle(88,170,40,66)}{hand(90,250,16)}{hand(126,250,16)}',
  "", "両手でそっと持つ。ボトル初出0.0秒。実在コメントのみ"))
C.append(frame(1,"C#2 1.6–3.4 傾け",BL,f'{bubble("見つけたと思ったら売り切れてた、、、")}{bottle(88,170,40,66,8)}{hand(90,250,16)}{hand(126,250,16)}',
  "ごめんね、、、／うん、いま在庫切れ", "±10°以内。VO小声"))
C.append(frame(2,"C#3 3.4–5.6 ラベルマクロ",MW,f'<rect x="20" y="60" width="176" height="260" fill="none" stroke="{CH}" stroke-dasharray="4 3"/>'+text(108,150,"（ラベル：正式画像そのまま）",9)+text(108,175,"商品名→イラストへピント送り",9),
  "ラベルの子、かわいいでしょ", "カメラ側のみ動く。加工なし。偏光フィルタ"))
C.append(frame(3,"C#4 5.6–7.8 置く",BL,f'<rect x="0" y="270" width="216" height="114" fill="{MW}"/>{bottle(140,200,36,62)}{hand(150,300,14)}',
  "いま、ちょっとお休み中。", "置いて手を離す。右1/3"))
C.append(frame(4,"C#5 7.8–10.2 棚パン",MW,
  f'<rect x="20" y="90" width="176" height="6" fill="{CH}" opacity="0.5"/><rect x="20" y="190" width="176" height="6" fill="{CH}" opacity="0.5"/><rect x="20" y="290" width="176" height="6" fill="{CH}" opacity="0.5"/>'
  f'<rect x="30" y="50" width="24" height="40" fill="#eee" stroke="{CH}" stroke-width="0.6"/><rect x="150" y="60" width="30" height="30" fill="#eee" stroke="{CH}" stroke-width="0.6"/>'
  f'<rect x="30" y="160" width="22" height="30" fill="#eee" stroke="{CH}" stroke-width="0.6"/><rect x="88" y="130" width="40" height="60" fill="none" stroke="{RS}" stroke-dasharray="3 3"/><rect x="150" y="150" width="34" height="40" fill="#eee" stroke="{CH}" stroke-width="0.6"/>',
  "でも、戻ってくるから", "中段中央が空き（赤点線）。無地の瓶のみ。他社製品NG"))
C.append(frame(5,"C#6 10.2–12.0 置かれる",MW,
  f'<rect x="20" y="190" width="176" height="6" fill="{CH}" opacity="0.5"/>{bottle(90,130,36,60)}{hand(108,205,14)}',
  "戻ってくる日が決まったら、いちばんに。", "実写で置く。SE：コト。字幕2行まで"))
C.append(frame(6,"C#7 12.0–13.6 英語",MW,f'<rect x="20" y="190" width="176" height="6" fill="{CH}" opacity="0.5"/>{bottle(90,130,36,60)}'+text(108,90,"Coming back soon",13,RS),
  "", "push-in 3%。Rose 96px Y=1100"))
C.append(frame(7,"C#8 13.6–15.0 通知",MW,f'<rect x="20" y="190" width="176" height="6" fill="{CH}" opacity="0.5"/>{bottle(90,130,36,60)}'+text(108,80,"Coming back soon",13,RS)+text(108,262,"Get notified",10,CH)+text(108,278,"再販のお知らせはプロフィールから",7,CH,"sans-serif"),
  "", "購入導線なし。下430pxに入れない"))
open("04_scripts/storyboards/C_storyboard.svg","w",encoding="utf-8").write(doc("案C「売り切れてた…」絵コンテ（構図ラフ）",C,8*240+16))
print("svg ok")
