"""Original SVG interface art: lacquer rim, silk paper, cloud fret and a sword."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/ui/dialogue'
OUT.mkdir(parents=True, exist_ok=True)

def svg(name, width, height, content):
    (OUT / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n{content}\n</svg>\n', encoding='utf8')

defs = '''<defs>
  <linearGradient id="paper" x2="0" y2="1"><stop stop-color="#e9dfc6"/><stop offset=".48" stop-color="#e0d1ae"/><stop offset="1" stop-color="#cbbc98"/></linearGradient>
  <linearGradient id="rim" x2="0" y2="1"><stop stop-color="#535545"/><stop offset=".34" stop-color="#292f29"/><stop offset="1" stop-color="#41382c"/></linearGradient>
  <linearGradient id="bronze" x2="0" y2="1"><stop stop-color="#c7b286"/><stop offset=".46" stop-color="#a08b62"/><stop offset="1" stop-color="#6c573a"/></linearGradient>
  <linearGradient id="wash"><stop stop-color="#8c8165" stop-opacity=".22"/><stop offset=".36" stop-color="#b4aa8d" stop-opacity="0"/><stop offset="1" stop-color="#85795e" stop-opacity=".12"/></linearGradient>
  <pattern id="weave" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 1H6M1 0V6" stroke="#685638" stroke-opacity=".045" stroke-width=".5"/></pattern>
  <g id="corner">
    <path d="M0 42V8L8 0H60L51 8H19L8 19V42Z" fill="#343b31" stroke="#a99671" stroke-width="1.4"/>
    <path d="M6 38V18L18 6H49M13 30V20L22 12H35V20H23V29H32" fill="none" stroke="#c1ab7f" stroke-width="1.3"/>
    <path d="M2 3L10 3L3 10Z" fill="#dbca9d"/>
    <path d="M36 5L45 0L51 4L45 8Z" fill="#827152"/>
  </g>
  <g id="cloud" fill="none" stroke="#7d7055" stroke-width="1">
    <path d="M0 40C17 40 13 20 34 20C34 6 57 4 65 17C84 8 102 24 95 38C105 48 126 36 131 26C147 12 170 24 162 40C152 57 140 37 149 34"/>
    <path d="M11 45C30 45 25 29 40 29C46 17 59 23 59 30C65 42 79 37 78 27M27 52C50 52 49 45 67 45H126C140 45 144 53 159 53"/>
  </g>
</defs>'''

body = defs + '''
<path d="M14 9H1106L1118 21V179L1106 191H14L2 179V21Z" fill="#0c201e" opacity=".28"/>
<path d="M14 2H1106L1118 14V174L1106 186H14L2 174V14Z" fill="url(#rim)" stroke="#19251f" stroke-width="2"/>
<path d="M19 7H1101L1112 18V170L1101 181H19L8 170V18Z" fill="none" stroke="url(#bronze)" stroke-width="2"/>
<path d="M25 14H1095L1104 23V165L1095 174H25L16 165V23Z" fill="url(#paper)" stroke="#161c16" stroke-width="2"/>
<path d="M25 14H1095L1104 23V165L1095 174H25L16 165V23Z" fill="url(#weave)"/>
<path d="M25 14H1095L1104 23V165L1095 174H25L16 165V23Z" fill="url(#wash)"/>
<path d="M29 20H1091L1097 26V162L1091 168H29L23 162V26Z" fill="none" stroke="#a28f68" stroke-width=".8"/>
<path d="M270 20V168" stroke="#8b7957" stroke-opacity=".30"/>
<path d="M274 32V156" stroke="#faf0cf" stroke-opacity=".45"/>
<g opacity=".12"><use href="#cloud" transform="translate(900 77) scale(1.05)"/><use href="#cloud" transform="translate(755 108) scale(.8)"/></g>
<path d="M450 179H520L529 175H543L551 179H569L577 175H591L600 179H670" fill="none" stroke="#baa477" stroke-width="1"/>
<path d="M555 179L560 175L565 179L560 183Z" fill="#b9a17a"/>
<use href="#corner" transform="translate(7 7)"/>
<use href="#corner" transform="translate(1113 7) scale(-1 1)"/>
<use href="#corner" transform="translate(7 181) scale(1 -1)"/>
<use href="#corner" transform="translate(1113 181) scale(-1 -1)"/>
'''
svg('silk_dialogue_frame.svg', 1120, 194, body)

svg('speaker_plaque.svg', 198, 52, defs + '''
<path d="M15 4H183L195 26L183 48H15L3 26Z" fill="#14241e" opacity=".3" transform="translate(0 3)"/>
<path d="M15 2H183L195 24L183 46H15L3 24Z" fill="url(#rim)" stroke="#1c261f" stroke-width="2"/>
<path d="M19 7H179L188 24L179 41H19L10 24Z" fill="none" stroke="url(#bronze)" stroke-width="1.5"/>
<path d="M26 11H172M26 37H172" stroke="#c6b181" stroke-opacity=".4"/>
<path d="M17 24L22 19L27 24L22 29ZM171 24L176 19L181 24L176 29Z" fill="#b89d6e"/>
''')

# Shape rather than lettering communicates advancement. Broad transparent hit area.
for state in ['normal', 'hover', 'pressed']:
    light = '#edf0d8' if state == 'hover' else '#ced6c0'
    bronze = '#d4b675' if state == 'hover' else '#a8915f'
    transform = 'translate(2 2)' if state == 'pressed' else 'translate(0 0)'
    svg(f'sword_{state}.svg', 128, 66, f'''<defs>
<linearGradient id="blade" x2="0" y2="1"><stop stop-color="{light}"/><stop offset=".47" stop-color="#e1e2c8"/><stop offset=".51" stop-color="#8a9e90"/><stop offset="1" stop-color="#5b756f"/></linearGradient>
</defs><g transform="{transform}">
<path d="M9 51C15 62 35 55 31 42C27 33 19 39 22 45C25 50 36 50 38 45" fill="none" stroke="#413225" stroke-width="4" opacity=".2"/>
<path d="M7 49C13 60 33 53 29 40C25 31 17 37 20 43C23 48 34 48 36 43" fill="none" stroke="#7e382b" stroke-width="3"/>
<path d="M7 49L5 59M9 50L8 60M11 51L12 59" stroke="#9d5036" stroke-width="1.7"/>
<path d="M42 30L106 10L124 11L110 23L46 42Z" fill="url(#blade)" stroke="#37463d" stroke-width="1.4"/>
<path d="M46 35L122 11" fill="none" stroke="{light}" stroke-width="1.2"/>
<path d="M47 37L109 18" stroke="#546e64" stroke-width=".8"/>
<path d="M40 24Q44 29 49 26L54 28Q49 34 51 42L47 47Q43 40 38 40Z" fill="{bronze}" stroke="#463c27" stroke-width="1.4"/>
<path d="M42 29L46 40" stroke="#e0c78c" stroke-width="1.2"/>
<path d="M20 40L38 34L42 42L24 48Z" fill="#39453b" stroke="#27342c" stroke-width="1.3"/>
<path d="M24 39L30 46M29 38L35 44M34 36L40 42" stroke="#9d8b60" stroke-width="1.5"/>
<path d="M17 40L23 38L27 48L21 51L15 47Z" fill="{bronze}" stroke="#4e482e" stroke-width="1.4"/>
<path d="M18 42L21 47" stroke="#e0c78c"/>
<circle cx="43.8" cy="35" r="2.1" fill="#688c78" stroke="#394e43" stroke-width=".7"/>
</g>''')
print('Authored dialogue frame, name plaque and three sword states.')
