"""Draw a labelled plan using object positions exported from the fixed 3D scene."""
from pathlib import Path
import json
import html
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'concepts/L1-living-dining/fixed-layout'
data=json.loads((OUT/'layout.json').read_text())
S=155
OX,OY=170,155
def pt(x,y): return OX+x*S, OY+y*S
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1150" viewBox="0 0 1100 1150">
<rect width="1100" height="1150" fill="#faf8f3"/>
<style>text{font-family:Arial,sans-serif;fill:#293239} .tiny{font-size:12px}.small{font-size:15px}.body{font-size:18px}.title{font-size:30px;font-weight:bold}</style>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="#1c7591" stroke-width="1.5"/></marker></defs>
<text x="60" y="55" class="title">L1 · fixed layout from your rough sketch</text>
<text x="60" y="88" class="body">Same coordinates in every render. Plan top stays at the top of this sheet.</text>
''']
def text(x,y,s,cls='small',anchor='middle'):
    px,py=pt(x,y); parts.append(f'<text x="{px:.2f}" y="{py:.2f}" class="{cls}" text-anchor="{anchor}">{html.escape(s)}</text>')
def rect(x,y,w,h,fill,stroke='#6e645a',sw=1,r=0):
    px,py=pt(x-w/2,y-h/2)
    parts.append(f'<rect x="{px:.2f}" y="{py:.2f}" width="{w*S:.2f}" height="{h*S:.2f}" rx="{r*S:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def line(x1,y1,x2,y2,color='#1c7591',width=2,dash='',arrow=False):
    a,b=pt(x1,y1);c,d=pt(x2,y2)
    parts.append(f'<line x1="{a:.2f}" y1="{b:.2f}" x2="{c:.2f}" y2="{d:.2f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" '+('marker-end="url(#arrow)"' if arrow else '')+'/>')
W,D=data['room_envelope']
points=' '.join(f'{pt(x,y)[0]},{pt(x,y)[1]}' for x,y in [(0,0),(W,0),(W,D),(1.16,D),(1.16,3.4),(0,3.4)])
parts.append(f'<polygon points="{points}" fill="#efe8dc" stroke="#bfb6a8"/>')
# Draw architectural solids at floor level only; lintels remain openings.
walls=['Plan top wall','Right wall above entry','Right wall below entry','B2 short wall','B2 TV WALL','Lower left notch wall','Notch wall stub','Kitchen left upper wall','Kitchen toilet dividing side','Top left pillar','Top right pillar','Lower right pillar']
for name in walls:
    o=data['objects'][name]; x,y,z=o['center']; w,h,d=o['size'];rect(x,y,w,h,'#4d5254','#4d5254')
for name in ['Living rug','Prayer mat']:
    o=data['objects'][name];x,y,z=o['center'];w,h,d=o['size'];rect(x,y,w,h,'#ddd3c1',r=.02)
# Furniture is sourced from the rendered scene, not redrawn by an image model.
for name,o in data['objects'].items():
    fill=None
    if name in ['Dining table','TV console','Singhasan base']: fill='#a48669'
    if name.startswith('Dining chair seat'): fill='#c4c7c7'
    if name in ['Sofa base','Sofa chaise base','Sofa back','Sofa left arm','Sofa right arm']: fill='#b5bcbc'
    if name=='TV frame': fill='#18252b'
    if name=='AC unit': fill='#fffefa'
    if name in ['P1 behind sofa lower panel','P2 below main entry lower panel']: fill='#704b2d'
    if name=='Side table stone top': fill='#f5eee2'
    if fill:
        x,y,z=o['center'];w,h,d=o['size'];rect(x,y,w,h,fill,r=.015)
text(1.72,1.29,'DINING')
text(1.72,1.46,'4 seats','tiny')
text(3.28,3.49,'L SOFA')
line(3.3,3.57,3.3,3.96,arrow=True)
text(3.24,4.64,'TV · B2 WALL','tiny')
text(3.94,2.30,'PUJA','tiny')
text(3.94,2.48,'Singhasan →','tiny')
text(3.91,1.90,'P2 · below main entry','tiny')
text(3.88,2.89,'P1 · behind sofa','tiny')
text(-.15,.87,'KITCHEN K1','small','end')
line(-.12,1.08,.25,1.08,arrow=True)
text(-.15,3.09,'T1','small','end')
line(-.12,3.20,.25,3.20,arrow=True)
text(.48,3.74,'SERVICE /','tiny');text(.48,3.91,'B1 SIDE','tiny')
text(5.00,1.12,'MAIN','small');text(5.00,1.29,'ENTRY','small')
line(4.95,1.45,4.37,1.45,arrow=True)
text(1.68,5.15,'B2 DOOR','small');line(1.68,5.02,1.68,4.69,arrow=True)
text(3.3,5.16,'B2 BEDROOM SIDE','small')
# Door leaves in the sketch are not evidence of a confirmed swing.
line(1.26,D,2.10,D,'#987b59',3)
text(W/2,-.20,'Approx. 15′2″ / 4.62 m','small')
text(5.12,3.45,'16′1″','small');text(5.12,3.63,'4.90 m','small')
# Camera dots and viewing arrows are taken from the saved camera transforms.
for key,label in [('02-entry-to-tv','A'),('03-tv-to-entry','B'),('04-dining-to-puja','C')]:
    x,wy,z=data['cameras'][key]['world_location'];y=-wy
    rx,ry,rz=data['cameras'][key]['rotation']
    dx=-(math.cos(rz)*math.sin(ry)*math.cos(rx)+math.sin(rz)*math.sin(rx))
    dy=math.sin(rz)*math.sin(ry)*math.cos(rx)-math.cos(rz)*math.sin(rx)
    norm=math.hypot(dx,dy);dx/=norm;dy/=norm
    px,py=pt(x,y)
    parts.append(f'<circle cx="{px}" cy="{py}" r="13" fill="#1c7591"/>')
    parts.append(f'<text x="{px}" y="{py+5}" text-anchor="middle" style="font:bold 15px Arial;fill:white">{label}</text>')
    line(x+dx*.11,y+dy*.11,x+dx*.55,y+dy*.55,arrow=True)
parts.append('''<text x="60" y="1020" class="body">A: entrance side → TV   ·   B: B2 side → entrance   ·   C: dining → puja</text>
<text x="60" y="1054" class="small">Room envelope uses the printed plan. Opening widths, pillars and ceiling height are provisional.</text>
<text x="60" y="1080" class="small">Puja and sofa-to-TV clearances are compact; verify on site before selecting furniture or joinery.</text>
<text x="60" y="1114" class="small">Top plan extracted from the same 3D model as the three room views.</text></svg>''')
(OUT/'00-labelled-plan.svg').write_text('\n'.join(parts))
print(OUT/'00-labelled-plan.svg')
