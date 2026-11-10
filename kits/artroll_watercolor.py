"""아트롤 블로그 수채화 카드 부품 (2026-11-10 사용자 선택 B안).

쓰는 법
    import sys; sys.path.insert(0, "<clone 경로>/kits")
    from artroll_watercolor import *
    svg = page(body)                       # 1000x1000 SVG (종이 배경 + 질감 포함)
    render([svg, ...], ["card1.png", ...])  # playwright로 PNG 저장

색
    종이 PAPER #FDF8F0, 잉크 INK #5E4637, 보조 글자 SUB #8C7262
    물감 PINK #F3C9BF, SKY #BFD6E6, YELLOW #F4DCA6, GREEN #C6DDB7, APRICOT #F3D9CF,
         BOWL #A9C8DD, PUREE #F1C27D, WOOD #D8C1A8, CARROT #F0A35E, LEAF #8DBF7E
글꼴
    제목 SERIF ('Noto Serif CJK KR' 700), 설명 SANS ('Noto Sans CJK KR' 400~800)

부품
    wc(shape, color, op, edge)  수채 물감 칠. shape는 fill="{c}" 또는 stroke="{c}"를 쓴 SVG 조각
    ink(d, w)                   가는 잉크 선(path d)
    wrow(y, n, title, desc, color)  수채 동그라미 번호 + 제목 + 설명 한 줄
    title_block(title, sub)     위쪽 명조 제목 + 부제
    divider(y)                  점선 구분선
    sample_card()               견본 카드(이유식 시작 신호) 전체 SVG
사람은 이 부품으로 그리지 않는다(사람이 나오는 그림은 Canva).
"""
from playwright.sync_api import sync_playwright

PAPER, INK, SUB = "#FDF8F0", "#5E4637", "#8C7262"
PINK, SKY, YELLOW, GREEN, APRICOT = "#F3C9BF", "#BFD6E6", "#F4DCA6", "#C6DDB7", "#F3D9CF"
BOWL, PUREE, WOOD, CARROT, LEAF = "#A9C8DD", "#F1C27D", "#D8C1A8", "#F0A35E", "#8DBF7E"
SANS = "'Noto Sans CJK KR', sans-serif"
SERIF = "'Noto Serif CJK KR', serif"

WC_DEFS = '''
<filter id="wc" x="-20%" y="-20%" width="140%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency=".022" numOctaves="3" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="18" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="1.2" result="b"/>
  <feTurbulence type="fractalNoise" baseFrequency=".6" numOctaves="2" seed="3" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.45 1.08" result="ga"/>
  <feComposite in="b" in2="ga" operator="in"/>
</filter>
<filter id="wcEdge" x="-20%" y="-20%" width="140%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency=".022" numOctaves="3" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="18" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feMorphology in="d" operator="erode" radius="3" result="er"/>
  <feComposite in="d" in2="er" operator="out" result="edge"/>
  <feGaussianBlur in="edge" stdDeviation="1"/>
</filter>
<filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" seed="11"/>
<feColorMatrix values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .35  0 0 0 .09 0"/></filter>
'''


def wc(shape, color, op=.55, edge=.35):
    """수채 물감 칠: 번진 면 + 진한 가장자리."""
    return (f'<g filter="url(#wc)" opacity="{op}">{shape.format(c=color)}</g>'
            f'<g filter="url(#wcEdge)" opacity="{edge}">{shape.format(c=color)}</g>')


def ink(d, w=2.4):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity=".85"/>')


def title_block(title, sub, y=112):
    return (f'<text x="500" y="{y}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="64" fill="{INK}">{title}</text>'
            f'<text x="500" y="{y+50}" text-anchor="middle" font-family="{SANS}" font-weight="400" font-size="24" fill="{SUB}">{sub}</text>')


def divider(y=500):
    return (f'<line x1="110" y1="{y}" x2="890" y2="{y}" stroke="#E3D3C1" stroke-width="2" '
            f'stroke-dasharray="2 10" stroke-linecap="round"/>')


def wrow(y, n, title, desc, color):
    return f'''
{wc(f'<circle cx="150" cy="{y}" r="34" fill="{{c}}"/>', color, .85, .5)}
<text x="150" y="{y+12}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="34" fill="{INK}">{n}</text>
<text x="210" y="{y-2}" font-family="{SANS}" font-weight="800" font-size="31" fill="{INK}">{title}</text>
<text x="210" y="{y+34}" font-family="{SANS}" font-weight="400" font-size="22" fill="{SUB}">{desc}</text>'''


def page(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">'
            f'<defs>{WC_DEFS}</defs><rect width="1000" height="1000" fill="{PAPER}"/>{body}'
            f'<rect width="1000" height="1000" filter="url(#paper)"/></svg>')


def render(svgs, paths):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1000, "height": 1000})
        for svg, path in zip(svgs, paths):
            pg.set_content(f"<html><body style='margin:0'>{svg}</body></html>")
            pg.wait_for_timeout(300)
            pg.screenshot(path=path)
        b.close()


# ---------- 견본 그림: 이유식 그릇·숟가락·당근·브로콜리 ----------
def hero_babyfood():
    return ''.join([
        wc('<ellipse cx="500" cy="330" rx="330" ry="150" fill="{c}"/>', APRICOT, .55, .2),
        wc('<path d="M330 320 C340 450 660 450 670 320 Z" fill="{c}"/>', BOWL, .8, .5),
        wc('<ellipse cx="500" cy="320" rx="170" ry="34" fill="{c}"/>', PUREE, .85, .45),
        ink("M330 320 C340 450 660 450 670 320"),
        ink("M330 320 C330 300 670 300 670 320 C670 342 330 342 330 320 Z", 2),
        ink("M440 440 C460 452 540 452 560 440", 2),
        wc('<path d="M640 300 L800 160" stroke="{c}" stroke-width="16" stroke-linecap="round"/>', WOOD, .9, .4),
        wc('<ellipse cx="822" cy="140" rx="34" ry="22" fill="{c}" transform="rotate(-42 822 140)"/>', WOOD, .9, .4),
        ink("M640 300 L800 160", 2.2),
        ink("M800 160 C790 130 830 100 852 118 C872 136 842 176 800 160 Z", 2.2),
        wc('<path d="M190 330 L292 250 C306 238 322 254 310 268 Z" fill="{c}"/>', CARROT, .9, .5),
        wc('<path d="M298 252 C300 228 314 220 326 226 C318 236 312 244 306 250 Z M304 258 C326 246 338 254 340 262 C328 262 318 262 308 262 Z" fill="{c}"/>', LEAF, .9, .4),
        ink("M190 330 L292 250 C306 238 322 254 310 268 Z", 2),
        ink("M232 300 l-12 -10 M258 280 l-10 -9", 2),
        wc('<circle cx="760" cy="350" r="22" fill="{c}"/><circle cx="790" cy="336" r="20" fill="{c}"/><circle cx="782" cy="366" r="18" fill="{c}"/>', "#9CC58A", .85, .45),
        wc('<rect x="770" y="372" width="14" height="40" rx="6" fill="{c}"/>', "#B7D3A3", .9, .3),
        wc('<circle cx="250" cy="190" r="10" fill="{c}"/><circle cx="740" cy="230" r="8" fill="{c}"/><circle cx="420" cy="210" r="6" fill="{c}"/>', "#F2AE9E", .8, .2),
    ])


def sample_card():
    return page(
        title_block("이유식 시작 신호", "보통 생후 6개월 무렵, 이런 모습이 보이면 준비해요")
        + hero_babyfood()
        + divider(500)
        + wrow(578, "1", "목을 잘 가눠요", "엎드린 자세에서 고개를 안정적으로 들어요", PINK)
        + wrow(682, "2", "받쳐 주면 앉을 수 있어요", "등을 기대고 잠시 앉아 있을 수 있어요", SKY)
        + wrow(786, "3", "음식에 관심을 보여요", "어른이 먹는 걸 빤히 보거나 손을 뻗어요", YELLOW)
        + wrow(890, "4", "숟가락을 밀어내지 않아요", "혀로 밀어내는 반사가 줄어들어요", GREEN)
    )


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "sample-artroll-b.png"
    render([sample_card()], [out])
    print(out)
