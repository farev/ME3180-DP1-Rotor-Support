"""Create the review packet, an editable Markdown trace, and 2-D DXF/PDF drawing.
Run calculate.py first. Requires reportlab, numpy, matplotlib, pypdf.
"""
from pathlib import Path
import json, math, html, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from pypdf import PdfReader, PdfWriter
import calculate as calc

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent.parent
OUT=WORK/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
CAD=ROOT/'cad'; CAD.mkdir(exist_ok=True)
O=json.loads((ROOT/'data/results.json').read_text()); I=O['inputs']; R=O['reactions_N']
S=O['sections']; G=O['groove']; K=O['key']; P=O['pin']; C=O['screw']; Q=O['ring']
Y=O['yield_check_conventions']
f=lambda x: f'{x:,.2f}'

# Reproducible load plot: hub contact is represented by two bearing bands.
ys=np.linspace(-250,303.5,1200)
loads=[(-240,0,2380),(-160,0,-1820),(-50,R['Fx'],R['Fz']),
       (R['yL'],R['RLx'],R['RLz']),(R['yU'],R['RUx'],R['RUz'])]
mx=[];mz=[]
for y in ys:
    mx.append(sum((p-y)*fz for p,fx,fz in loads if p<=y)/1000)
    mz.append(sum(-(p-y)*fx for p,fx,fz in loads if p<=y)/1000)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(3,1,figsize=(7.1,5.6),sharex=True,layout='constrained')
ax[0].plot(ys,mx,label='Mx');ax[0].plot(ys,mz,label='Mz');ax[0].legend(ncol=2)
ax[0].set_ylabel('Signed M (N m)')
ax[1].plot(ys,np.hypot(mx,mz),color='#146a78');ax[1].set_ylabel('Resultant M (N m)')
ax[2].plot([-250,-180,-180,-36,-36,303.5],[0,0,19.63,19.63,0,0],color='#ae6821')
ax[2].set_ylabel('Torque (N m)');ax[2].set_xlabel('y from lower outside support face (mm)')
for a in ax:
    a.grid(alpha=.2)
    for y in [R['yL'],R['yU']]:a.axvline(y,color='grey',ls=':',lw=.8)
    a.axvspan(-250,-150,color='#dddddd',alpha=.4)
ax[0].set_title('Hub transfer model and bearing-midplane resultants; shaded region = rotor hub',loc='left',fontsize=10)
fig.savefig(FIG/'moments.png',dpi=190);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.1,5.6),layout='constrained')
ax.plot([0,0],[-250,303.5],color='#394c56',lw=7)
for y,lab in [(R['yU'],'Upper bearing'),(R['yL'],'Lower bearing')]:
    ax.scatter(0,y,marker='s',s=90,color='#146a78',zorder=4)
    ax.text(-1.7,y,lab,va='center',fontsize=9)
for y,lab in [(-50,'Chain: Fx = 161.25 N; Fz = 13.35 N'),(-500,'Water drag: Fz = 560 N')]:
    ax.annotate('',xy=(1.15,y),xytext=(0,y),arrowprops=dict(arrowstyle='->',lw=1.7,color='#ae6821'))
    ax.text(1.2,y,lab,va='center',fontsize=8.5)
ax.plot([0,0],[-250,-500],ls='--',color='grey')
ax.text(.15,-390,'Rigid rotor/hub load extension\n(not extra shaft length)',fontsize=8.5)
ax.plot([-.23,.23,.23,-.23,-.23],[-150,-150,-250,-250,-150],color='#617078')
ax.scatter(0,-180,color='#ae6821',zorder=5);ax.text(-1.7,-180,'Pin center y = -180',va='center',fontsize=9)
ax.text(-1.7,-350,'Rotor weight 120 N in -y',fontsize=9)
ax.text(-1.7,-75,'Sprocket weight 35 N in -y',fontsize=9)
ax.set_ylim(-530,335);ax.set_xlim(-1.85,4.35);ax.set_yticks([293.65,6.35,-50,-150,-250,-350,-500])
ax.set_xticks([]);ax.set_ylabel('y (mm)');ax.spines[['top','right','bottom']].set_visible(False)
ax.set_title('Station map and transverse loading (arrows are schematic)',loc='left',fontsize=11)
fig.savefig(FIG/'load_map.png',dpi=190);plt.close(fig)

# The CAD source and drawing PDF share vector primitives. Geometry is true scale;
# paper annotations are in mm. DXF is AutoCAD R12 ASCII, suitable for 2-D CAD.
entities=[]
def line(x1,y1,x2,y2,layer='OUTLINE'):
    entities.append(('LINE',layer,(x1,y1,x2,y2)))
def circle(x,y,r,layer='OUTLINE'):entities.append(('CIRCLE',layer,(x,y,r)))
def arc(x,y,r,a,b,layer='OUTLINE'):entities.append(('ARC',layer,(x,y,r,a,b)))
def txt(x,y,t,h=2.5,layer='TEXT'):entities.append(('TEXT',layer,(x,y,t,h)))
def rect(x,y,w,h,layer='OUTLINE'):
    line(x,y,x+w,y,layer);line(x+w,y,x+w,y+h,layer);line(x+w,y+h,x,y+h,layer);line(x,y+h,x,y,layer)
def dim(x1,x2,y,ref,label):
    for x in [x1,x2]:line(x,ref,x,y+1,'DIM')
    line(x1,y,x2,y,'DIM')
    for x,sgn in [(x1,1),(x2,-1)]:
        line(x,y,x+sgn*2,y+.7,'DIM');line(x,y,x+sgn*2,y-.7,'DIM')
    txt((x1+x2)/2-len(label)*.65,y+1.5,label,2.3)

# A3-equivalent landscape drawing, shaft view at 1:2 (paper mm).
W,H=420,297
rect(10,10,400,277)
txt(17,277,'DP2 ROTOR SHAFT - REV P3 / FOR REVIEW AND QUOTATION',4)
txt(17,270,'Shaft properties: Piazza-approved set for 1566 at HRC25 (Sy = 88 ksi). Dimensions control; do not scale.',2.6)
sx=40; sy=208; scale=.5; D=38.1
xx=lambda s:sx+scale*s
rr=D*scale/2
line(sx-8,sy,xx(554)+8,sy,'CENTER')
line(sx,sy-rr,xx(554),sy-rr);line(sx,sy+rr,xx(554),sy+rr)
line(sx,sy-rr,sx,sy+rr);line(xx(554),sy-rr,xx(554),sy+rr)
for st in [249.6126,550.6000]:
    for p in [st,st+.7874]:line(xx(p),sy-rr,xx(p),sy+rr)
    txt(xx(st)+2,sy-rr-7,'G',2.5)
circle(xx(70.5),sy,6.363*scale/2)
line(xx(70.5)-5,sy,xx(70.5)+5,sy,'CENTER')
line(xx(70.5),sy-5,xx(70.5),sy+5,'CENTER')
# Keyseat shown as hidden edges in side view, with independent top view below.
for p in [214.5-22.45/2,214.5+22.45/2]:line(xx(p),sy-rr,xx(p),sy+rr,'HIDDEN')
dim(sx,xx(554),247,sy+rr,'554.00 +/-0.10')
dim(sx,xx(70.5),235,sy+rr,'70.50 +/-0.10')
dim(sx,xx(214.5),180,sy-rr,'214.50 +/-0.10 (KEY CENTER)')
dim(sx,xx(249.6126),165,sy-rr,'249.6126 +/-0.05 (GROOVE NEAR WALL)')
dim(sx,xx(550.6),151,sy-rr,'550.6000 +/-0.05 (GROOVE NEAR WALL)')
txt(325,220,'STOCK OD:',2.6);txt(325,214,'37.9984 - 38.1000',2.8)
txt(325,208,'(1.500 in +0/-0.004)',2.5)
txt(325,199,'PIN HOLE:',2.6);txt(325,193,'DIA 6.363 +0.012/-0 THRU',2.6)
txt(325,187,'Axis perpendicular to keyseat',2.3)
txt(325,181,'symmetry plane, +/-1 deg.',2.3)
txt(325,172,'Ends: C0.25 +/-0.10 x45 deg',2.3)
txt(325,166,'End faces square to shaft',2.3)
txt(325,160,'axis within 0.05 mm.',2.3)
txt(30,132,'DETAIL G - BOTH RING GROOVES (NTS)',3)
# Enlarged cut profile; the two rounded roots are visible, not a sharp notch.
line(33,91,103,91);line(33,91,33,121);line(103,91,103,121)
line(33,121,56,121);line(80,121,103,121)
line(56,121,56,111);arc(64,111,8,180,270)
line(64,103,72,103);arc(72,111,8,270,360);line(80,111,80,121)
txt(108,118,'Root DIA 37.0586 - 37.0840',2.6)
txt(108,112,'[1.4590 - 1.4600 in]',2.4)
txt(108,106,'Width 0.7874 - 0.8382',2.6)
txt(108,100,'[0.0310 - 0.0330 in]',2.4)
txt(108,94,'Both root corners R0.2489 - 0.2540',2.5)
txt(108,88,'[R0.0098 - 0.0100 in]. NO SHARP ROOTS.',2.4)
txt(33,82,'Groove mouths square; deburr without rounding load edges.',2.4)
txt(245,132,'KEYSEAT - TOP VIEW / SECTION (NTS)',3)
line(250,113,286,113);line(250,125,286,125)
arc(250,119,6,90,270);arc(286,119,6,270,450)
txt(304,125,'Overall length 22.45 +/-0.05',2.5)
txt(304,119,'Width 9.525 +0.0254/-0',2.5)
txt(304,113,'Depth 4.7625 +/-0.0254',2.5)
txt(304,107,'Depth measured from OD crown.',2.5)
txt(304,101,'End radius = half slot width',2.5)
# Transverse section at the slot center; show the radial floor explicitly.
ex,ey,er=263,96,8
eh=er/4;etop=math.sqrt(er*er-eh*eh);efloor=er-er/4
ea=math.degrees(math.acos(eh/er))
arc(ex,ey,er,180-ea,360+ea)
line(ex-eh,ey+etop,ex-eh,ey+efloor)
line(ex-eh,ey+efloor,ex+eh,ey+efloor)
line(ex+eh,ey+efloor,ex+eh,ey+etop)
txt(277,92,'Section at slot center',2.4)
txt(245,82,'Floor corner R0.13-0.25; Ra <=3.2 um; symmetry to axis <=0.05.',2.4)
notes=[
 '1. Blank: McMaster 1346K534, 1566 steel precision rotary shaft, HRC25, 1-1/2 x 24 in. Cut to length; keep supplied OD.',
 '2. All dimensions in mm; bracketed inch limits are exact conversions. Do not apply general tolerances to limits.',
 '3. Groove / hole surfaces Ra <=3.2 um. Remove burrs; do not grind away specified groove radii.',
 '4. OD straightness as supplied: 0.012 in per foot. Do not add a second keyway or any extra grooves.',
 '5. Corrosion protection under $100 allowance: paint exposed surfaces; protect fits with a thin compatible film.',
 '   Keep paint off fitting surfaces and preserve final dimensions. Maintain mu >=0.10 at the clamped key interfaces.',
 '6. Critical inspection: groove root diameter, minimum radius, edge margins, pin-hole clearance, keyseat location.',
 '7. Radius and diameter limits are essential to the reported yield safety factor. Substitute hardware only after recalculation.',
]
for j,n in enumerate(notes):txt(18,72-j*5.2,n,2.5)
rect(10,10,400,20);line(245,10,245,30);line(330,10,330,30)
txt(16,22,'PART: DP2-SHAFT-01   REV: P3   MATERIAL: 1566 STEEL, HRC25',2.8)
txt(16,15,'STATUS: FOR REVIEW / PROPERTIES PER PIAZZA LIST',2.8)
txt(250,22,'MAIN VIEW 1:2   /   DETAILS NTS',2.5);txt(250,15,'UNITS mm   |   SHEET 1 OF 1',2.5)
txt(335,22,'2026-11-10',2.8);txt(335,15,'DXF source included',2.5)

def write_dxf(path):
    data=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','0','ENDSEC','0','SECTION','2','ENTITIES']
    def add(*p):data.extend(str(v) for v in p)
    for typ,layer,v in entities:
        add(0,typ,8,layer)
        if typ=='LINE':add(10,v[0],20,v[1],30,0,11,v[2],21,v[3],31,0)
        elif typ=='CIRCLE':add(10,v[0],20,v[1],30,0,40,v[2])
        elif typ=='ARC':add(10,v[0],20,v[1],30,0,40,v[2],50,v[3]%360,51,v[4]%360)
        else:add(10,v[0],20,v[1],30,0,40,v[3],1,v[2],7,'STANDARD')
    add(0,'ENDSEC',0,'EOF');path.write_text('\n'.join(data)+'\n')
write_dxf(CAD/'DP2_shaft_P3.dxf')
drawpath=OUT/'DP2_shaft_drawing_PROVISIONAL.pdf'
cv=canvas.Canvas(str(drawpath),pagesize=(W*72/25.4,H*72/25.4))
cv.setTitle('DP2 shaft drawing P3 - 1566 HRC25 shaft 1346K534')
cv.scale(72/25.4,72/25.4)
for typ,layer,v in entities:
    cv.setLineWidth(.25 if layer=='OUTLINE' else .15)
    cv.setDash([2,.8] if layer in ['CENTER','HIDDEN'] else [])
    if typ=='LINE':cv.line(*v)
    elif typ=='CIRCLE':cv.circle(*v,stroke=1,fill=0)
    elif typ=='ARC':
        x,y,r,a,b=v;cv.arc(x-r,y-r,x+r,y+r,startAng=a,extent=b-a)
    else:
        x,y,t,h=v;cv.setFont('Helvetica',h);cv.drawString(x,y,t)
cv.showPage();cv.save()

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyDP',fontName='Helvetica',fontSize=9.5,leading=13,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallDP',fontName='Helvetica',fontSize=8.2,leading=11,spaceAfter=5))
styles.add(ParagraphStyle(name='TitleDP',fontName='Helvetica-Bold',fontSize=20,leading=24,spaceAfter=12,textColor=colors.HexColor('#173b4b')))
styles.add(ParagraphStyle(name='H2DP',fontName='Helvetica-Bold',fontSize=12,leading=16,spaceBefore=8,spaceAfter=7,textColor=colors.HexColor('#173b4b')))
styles.add(ParagraphStyle(name='EqDP',fontName='Courier',fontSize=8.4,leading=12,spaceBefore=3,spaceAfter=7,backColor=colors.HexColor('#f1f4f6'),borderPadding=5))
story=[]; md=[]; page_sections=[]
def heading(t):story.append(Paragraph(html.escape(t),styles['TitleDP']));md.append('# '+t+'\n')
def sub(t):story.append(Paragraph(html.escape(t),styles['H2DP']));md.append('## '+t+'\n')
def p(t,small=False):
    story.append(Paragraph(t,styles['SmallDP' if small else 'BodyDP']))
    mt=t.replace('<b>','**').replace('</b>','**').replace('<br/>','\n')
    mt=re.sub(r'<link href="([^"]+)" color="[^"]+">([^<]+)</link>',r'[\2](\1)',mt)
    md.append(mt+'\n')
def eq(t):
    story.append(Paragraph(html.escape(t).replace('\n','<br/>'),styles['EqDP']));md.append('```text\n'+t+'\n```\n')
def table(headers,rows,widths=None):
    data=[[Paragraph(str(c),styles['SmallDP']) for c in row] for row in [headers]+rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6edf1')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#8eabb8')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d7e0e5')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.extend([t,Spacer(1,8)])
    md.append('| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(str(c) for c in row)+' |' for row in rows)+'\n')
def newpage():story.append(PageBreak());md.append('\n---\n')
def pic(path,w,h):story.append(Image(str(path),width=w,height=h));md.append(f'![{path.stem}]({path})\n')

heading('Shaft design | 1. Recommendation and assumptions')
p('<b>Recommended design, Rev P3.</b> All checks use one diameter, 1.500 in (38.10 mm), from McMaster 1346K534: a 1566 carbon-steel precision rotary shaft, Rockwell C25, bought as a 24 in stick and cut to 554.0 mm. Estimated assignment cost: <b>$'+f(O['total_cost_USD'])+'</b>, including the full price of the stock and the mandatory $100 non-stainless allowance.')
table(['Property / decision','Basis'],[
 ['Shaft material','1566 carbon-steel precision rotary shaft, Rockwell C25; turned, ground and polished; OD 1.496-1.500 in; 24 in stock. [2]'],
 ['Sy = 88 ksi = '+f(I['Sy_MPa'])+' MPa','Approved on Piazza for 1566 at Rockwell C25, shaft diameters up to and including 1.5 in. [7]'],
 ['Sut = '+f(I['Sut_MPa'])+' MPa','Not listed on Piazza. Shigley Eq. (2-36), Sut = 3.4 HB, with HRC25 = HB 253 (ASTM E140): 3.4(253) = '+f(I['Sut_MPa'])+' MPa, the minimum the hardness rule allows.'],
 ['Hardness cap','Rockwell C25 is exactly the Rev2 cap; no strength beyond C25 is claimed.'],
 ],[140,370])
sub('Explicit assumptions')
p('A1. Rev2 governs, with the existing P2 class constraint that the key be longer than it is wide. A2. The 300 mm dimension is between the two outside support/bearing faces. Bearings are each 12.7 mm wide, with radial reactions at their midplanes. A3. Water and chain loads are steady in the stationary frame; shaft bending is fully reversed, torque and weights are steady. The given safety factors cover the specified overload objective; no additional shock multiplier is invented.')
p('A4. Rotor/hub bore contact carries transverse drag and its bending couple. The pin carries torque and the 120 N rotor weight. A snug hub bore and contact bands near the hub ends are assumed. A5. Ambient-temperature, low-speed operation below critical speed; the ring rotational rating must not be exceeded. No required operating speed is supplied. A6. Upper ring/bearing carries all downward thrust; both rings are checked for the entire thrust, including conservative unmachined shaft self-weight.')
p('A7. Report both Shigley\'s Kf/Kfs shaft yield check and a supplemental Kt/Kts local elastic check; the latter is an added criterion, not a PDF requirement. Use modified Goodman fatigue, machined surface factors at machined features and reliability factor 0.814 (99%). Maintained corrosion protection is assumed. A8. Assembly clearances/axial float are allowed; section moments are taken directly from the moment diagram, as in Shigley Example 7-2, with no added moment margin. A9. Specified dimensions and tolerances control the result; a sharper groove invalidates it.')
p('A10. Price basis follows Rev2 item 4: the full price of the shortest stock of the selected part that is long enough to make the shaft (24 in, $112.69), plus per-item prorated hardware, without tax or freight. Key stock is cut and deburred to length on this material-only basis. Pin is selected to span the 3 in rotor-hub OD for straightforward installation/removal. These assumptions delimit the cost comparison; an absolute global minimum across every possible joint configuration has not been proved.',small=True)
newpage()

heading('Shaft design | 2. Bearing reactions')
eq('Fx = 161.8 cos(4.732 deg) = 161.2485 N\nFz = +161.8 sin(4.732 deg) = 13.3477 N\nyL = 6.35 mm; yU = 293.65 mm; L = 287.30 mm')
p('A negative rotation about +y takes +x toward +z under the right-hand convention. Thus the chain z component is positive. Use y = 0 at the lower outside face, y positive upward. Chain station: -50 mm; rotor hub: -150 to -250 mm; rotor CG: -350 mm; water COP: -500 mm.')
eq('RUx = Fx(56.35)/287.30\nRLx = -Fx - RUx\nRUz = [560(506.35) + Fz(56.35)]/287.30\nRLz = -560 - Fz - RUz')
table(['Bearing','Rx (N)','Rz (N)','Radial resultant (N)'],[
 ['Upper',f(R['RUx']),f(R['RUz']),f(math.hypot(R['RUx'],R['RUz']))],
 ['Lower',f(R['RLx']),f(R['RLz']),f(math.hypot(R['RLx'],R['RLz']))],
 ],[130,110,110,160])
p(f"The x and z force sums and both bearing moment balances close numerically. Wshaft = rho g pi D^2 L/4 = {f(O['shaft_weight_N'])} N. Total downward thrust = 120 + 35 + Wshaft = {f(O['total_thrust_N'])} N. Using the full cylinder slightly overestimates the machined shaft weight.")
pic(FIG/'load_map.png',470,330)
newpage()

heading('Shaft design | 3. Moments and critical sections')
p('Above the rotor-hub top, the water load can be represented by a 560 N force at y = -500 mm. Below the sprocket, T = 19.63 N m; above its torque-transfer region, T = 0. A conservative full-torque envelope is used throughout the keyseat. The largest nominal bending occurs at the lower bearing, but the lower retaining-ring groove creates the largest local elastic stress.')
eq('For -150 <= y < -50: |Mx| = 560(y+500); Mz = 0\nFor -50 <= y <= yL:\n  |Mx| = 560(y+500) + Fz(y+50)\n  |Mz| = Fx(y+50)\nM = sqrt(Mx^2 + Mz^2)  [N mm]')
table(['Section','y (mm)','M (N m)','T (N m)'],[
 ['Lower bearing center',f(R['yL']),f(S[3]['M_Nm']),'0'],
 ['Lower groove center',f(I['lower_groove_y_mm']),f(S[0]['M_Nm']),'0'],
 ['Keyseat upper end',f(calc.keyY),f(S[1]['M_Nm']),'19.63'],
 ['Pin hole, upper edge (cantilever envelope)',f(I['pin_y_mm']+calc.hole/2),f(S[2]['M_Nm']),'19.63'],
 ['Upper groove',f(I['upper_groove_y_mm']),'0','0'],
 ],[200,90,110,110])
pic(FIG/'moments.png',480,330)
p('For a statically consistent diagram within the hub, use -1820 N at y=-160 mm and +2380 N at y=-240 mm. Their sum is 560 N and their moment about y=0 is -280 N m. This avoids pretending the shaft physically extends to the COP. The pin stress check instead uses the larger full-load cantilever envelope at the hole\'s upper edge. A 10 mm contact band has average bearing pressure at most 2380/(37.9984 x 10)=6.26 MPa; the shaft-hole mean-stress allowance is 12 MPa.',small=True)
newpage()

heading('Shaft design | 4. Groove, fatigue and yield method')
p('Use identical 93576A210 single-turn spiral rings. Catalog groove: diameter 1.456 +/-0.004 in and width 0.031 +0.002/-0 in. The design deliberately uses a tighter, shallower interval within those limits: <b>diameter 1.4590-1.4600 in, radius 0.0098-0.0100 in</b>. Smalley permits a maximum 0.010 in groove-bottom radius for diameters over 1 in. Its VS-150 dimensions match this catalog ring geometry. [3,8,9]')
eq(f"dmin = 37.0586 mm\ntmax = (38.1000 - 37.0586)/2 = {G['t_max_mm']:.4f} mm\na/t = {G['a_over_t']:.4f}; r/t = {G['r_over_t']:.4f}\nKt = 3.50 (upper rounded chart estimate, Fig. A-15-16 [10])")
p('Chart factors use the groove-root diameter. Kt relates nominal stress to the theoretical local elastic peak; Kf=1+q(Kt-1) accounts for notch sensitivity in fatigue. Shigley Eq. (7-15) also uses Kf/Kfs for its shaft yield check. Report that check as primary and retain Kt/Kts as a separate elastic check. The PDF does not expressly require the added criterion. [15]')
eq('sqrt(a_N) = 0.246 - 0.00308 Sut + 1.51e-5 Sut^2 - 2.67e-8 Sut^3\nq = 1 / [1 + sqrt(a_N)/sqrt(r)]\nSut = '+format(I['Sut_MPa']/6.894757293,'.4f')+' ksi; r = 0.0098 in\nq = '+f(G['q'])+'; Kf = '+f(G['Kf']))
eq('Se\' = 0.5 Sut\nka = 4.51 Sut^(-0.265) [Sut in MPa, machined]\nkb = 1.24 D^(-0.107) [D in mm]\nkc = kd = 1; ke = 0.814; miscellaneous = 1\nSe = 0.5('+f(I['Sut_MPa'])+')('+f(G['ka'])+')('+f(G['kb'])+')(0.814) = '+f(G['Se_MPa'])+' MPa')
p('Using the full nominal diameter in kb is slightly conservative relative to the smaller groove root. Plain stock alone uses a ground-surface factor. Fatigue at the keyseat and transverse hole conservatively takes Kf=Kt, avoiding notch-sensitivity credit at those features.')
eq('sigma_b = 32 M/(pi d^3); tau_t = 16 T/(pi d^3)\nsigma_N = 4 N/(pi d^2); sigma_m = Kt sigma_N + contact allowance\nsigma_max,S = sqrt[(Kf sigma_b + sigma_m)^2 + 3(Kfs tau_t)^2]\nsigma_max,E = sqrt[(Kt sigma_b + sigma_m)^2 + 3(Kts tau_t)^2]\nny,S = Sy/sigma_max,S; ny,E = Sy/sigma_max,E\n1/nf = sigma_a/Se + sigma_mean,eq/Sut; sigma_a = Kf sigma_b')
p('Eq. (7-15) itself omits axial force. Both checks here retain the same small Kt-amplified axial stress and contact allowance as an explicit conservative extension. Kfs=Kts at the keyseat and pin hole; groove torque is zero. The fatigue calculation is unchanged: sigma_mean,eq=sqrt[sigma_m^2+3(Kts tau_t)^2].',small=True)
p('The keyway model uses deliberately increased factors Kt=3.0 and Kts=4.0, compared with common nominal end-milled-keyseat estimates 2.14 and 3.0. A key-bearing normal-stress allowance is added to the mean stress. The hole uses the net-section coefficients and matching Kt from Table A-16 [10], with hole/shaft='+format(calc.ratio,'.5f')+'; bending A='+f(calc.Ab)+', Kt='+f(calc.Ktb)+'; torsion A='+f(calc.At)+', Kts='+f(calc.Ktt)+'. The net section is applied once only.')
newpage()

heading('Shaft design | 5. Both yield checks and sensitivity')
eq(f"Groove: sigma_b = 32({S[0]['M_Nm']*1000:.0f})/(pi x 37.0586^3) = {S[0]['nominal_bending_MPa']:.3f} MPa\nRetained axial term sigma_m = {S[0]['mean_eq_MPa']:.3f} MPa; T = 0\nShigley: sigma_max,S = {G['Kf']:.5f} sigma_b + sigma_m = {S[0]['shigley_max_equivalent_MPa']:.3f}\n  ny,S = {I['Sy_MPa']:.2f}/{S[0]['shigley_max_equivalent_MPa']:.3f} = {S[0]['ny_shigley']:.4f}\nElastic: sigma_max,E = 3.5 sigma_b + sigma_m = {S[0]['elastic_peak_von_Mises_MPa']:.3f}\n  ny,E = {I['Sy_MPa']:.2f}/{S[0]['elastic_peak_von_Mises_MPa']:.3f} = {S[0]['ny_elastic']:.4f}")
table(['Location','ny Shigley','ny elastic','nf'],[[s['name'],f(s['ny_shigley']),f(s['ny_elastic']),f(s['nf'])] for s in S],[255,85,85,85])
table(['Required Sy for ny=3 (MPa)','Shigley Kf/Kfs','Elastic Kt/Kts'],[
 ['Lower groove',f(S[0]['minimum_Sy_shigley_for_n3_MPa']),f(S[0]['minimum_Sy_elastic_for_n3_MPa'])],
 ['Keyseat',f(S[1]['minimum_Sy_shigley_for_n3_MPa']),f(S[1]['minimum_Sy_elastic_for_n3_MPa'])],
 ['Governing shaft requirement',f(Y['minimum_Sy_shigley_MPa']),f(Y['minimum_Sy_elastic_MPa'])],
 ],[270,120,120])
p('<b>The keyseat controls Shigley yielding and fatigue; the lower groove controls the supplemental elastic check.</b> Its Kf=Kt=3.0 and Kfs=Kts=4.0 make the keyseat result identical in both yield methods. The shaft needs Sy >= '+f(Y['minimum_Sy_shigley_MPa'])+' MPa under the Shigley method and Sy >= '+f(Y['minimum_Sy_elastic_MPa'])+' MPa under the added elastic check; the approved '+f(I['Sy_MPa'])+' MPa satisfies both. These thresholds hold Sut='+f(I['Sut_MPa'])+' MPa and all geometry/contact assumptions fixed.')
table(['Sensitivity','Result / implication'],[
 ['Sy = 82 ksi = 565.4 MPa (1566 value for D > 1.5 in)','Shigley minimum ny='+f(82*6.894757293/S[1]['shigley_max_equivalent_MPa'])+' (passes); elastic groove ny='+f(82*6.894757293/S[0]['elastic_peak_von_Mises_MPa'])+' (fails added check). Not applicable: D = 1.500 in is within the 88 ksi range.'],
 ['Notch sensitivity q at the groove','q = '+f(G['q'])+'. Fatigue and Shigley yield still pass up to q = 0.91 (Kf = 3.28). With Kf = Kt everywhere, groove nf falls below 1.2.'],
 ['Use unrestricted catalog root tolerance','The root may shrink to 1.452 in, and the notch factor changes. Do not use the current safety factor.'],
 ['Use an unspecified sharp root','Kt may be substantially higher. The drawing specifies a MINIMUM radius.'],
 ],[180,330])
p('If the approved set changes, rerun the calculations. A lower Sy does not automatically require a larger shaft: first compare it with the threshold for the chosen method. A change in Sut also changes endurance strength and notch sensitivity. No heat treatment has been added to the manufacturing plan.',small=True)
newpage()

heading('Shaft design | 6. Approved shaft properties')
p('Rev2 allows only shaft properties approved on Piazza. The instructor posted the approved yield strengths below (10 Nov 2026). No tensile strengths were listed, so each Sut here is the hardness-based minimum required by item 5, Shigley Eq. (2-36): Sut = 3.4 HB, with Rockwell values converted by ASTM E140 and capped at HRC25 (HB 253).')
table(['Approved material (Piazza)','Sy (ksi / MPa)','Sut = 3.4 HB (MPa)','McMaster use'],[
 ['1045, Brinell 197','75 / 517.1','669.8','4138N plain rotary shafts'],
 ['1045, Brinell 190, D <= 2 in','75 / 517.1','646.0','6117K partially keyed shafts'],
 ['<b>1566, Rockwell C25, D <= 1.5 in</b>','<b>88 / 606.7</b>','<b>860.2</b>','<b>1346K plain rotary shafts (selected 1346K534)</b>'],
 ['1566, Rockwell C25, D > 1.5 in','82 / 565.4','860.2','-'],
 ['4140, Rockwell C28, D <= 1 in / larger','120 / 827.4; 110 / 758.4','860.2 (HRC25 cap)','2672N high-strength alloy shafts'],
 ],[160,95,95,160])
p('The earlier proposal (Marks handbook averages Sut=703, Sy=598 MPa for 1045) is superseded: the approved 1045 value is 517 MPa. At 517 MPa the previous 1045 design passes the Shigley check (3.11) but not the added elastic check (2.62), and it is sold only as a 120 in stick. The selected 1566 shaft has the same 1.500 in geometry and passes both checks.')
sub('Hardware properties are separate assumptions')
p('For the 18-8 key and screw, use the annealed 304-class baseline Sut=515 MPa and Sy=205 MPa published by ATI for its flat products [12] as a conservative classroom assumption, not a fastener certification. Only the key receives the PDF exception Sy=0.8Sut=412 MPa. For the HRC36 minimum 416 pin, use Sy=760 MPa from Swiss Steel\'s lower-hardness condition-T range [11]. The pin calculation explicitly identifies this as a typical-property assumption. Ring capacity comes directly from the selected supplier rating.')
newpage()

heading('Shaft design | 7. Cost search and selection')
p('Every McMaster precision rotary shaft from 1-1/4 to 3 in and 30 to 50 mm was read from the catalog on 10 Nov 2026, with the shortest stock at least 21.8 in long. Each was paired with every stainless retaining ring sold for its diameter and run through the same equations as this report (DP2/solver/solver.py; its regression check reproduces this calculation). Groove Kt comes from Fig. A-15-16, digitized, times 1.06, the same rounding used here (3.31 to 3.5). Cost = full stock price + $100 if not stainless + hardware.')
table(['Shaft (stock)','Stock price','Total','Result'],[
 ['1045, 1-7/16 in, 4138N22 (24 in)','$55.85','$168.39','Fails fatigue at the deeper groove (nf 1.06)'],
 ['1566, 1-1/4 in, 1346K45 (24 in)','$62.74','$171.48','Fails fatigue (nf 0.81)'],
 ['1045, 35 mm, 4138N66 (1000 mm)','$80.56','$194.08','Fails fatigue (nf 0.79)'],
 ['1045, 1-11/16 in, 4138N27 (24 in)','$76.03','$202.18','Passes Shigley (ny 3.87, nf 1.37); fails added elastic check (2.69)'],
 ['<b>1566, 1-1/2 in, 1346K534 (24 in)</b>','<b>$112.69</b>','<b>$'+f(O['total_cost_USD'])+'</b>','<b>Selected: passes both yield checks and fatigue</b>'],
 ['1045, 1-15/16 in, 4138N33 (24 in)','$97.65','$306.55','Passes; heavy-duty rings $49.11 each'],
 ['1045, 1-1/2 in, 4138N14 (120 in only)','$306.52','$415.90','Passes Shigley only at Sy = 517 MPa'],
 ],[165,65,60,220])
p('Excluded without a stress check: keyed shafts (the full-length keyway, or the 4 in and 14 in end keyways on 24 in stock, run through the bearing seats and ring grooves); D-profile shafts (full-length flat); nitride-coated shafts (only the HRC60 case hardness is listed, so no property set can meet item 5); chrome-plated shafts (excluded by Rev2). Plain stainless stops at 1-1/4 in and fails fatigue by a wide margin.')
sub('What the cost claim means')
p('<b>1346K534 is the lowest-cost McMaster rotary shaft found that passes fatigue, the Shigley yield check and the added Kt elastic check.</b> 4138N27 is $20.11 cheaper but passes only the Shigley check and needs a 15-7 PH ring with a deeper groove. The selected shaft keeps the 1-1/2 in rings, key and pin, and has the larger margin on notch sensitivity (passes up to q = 0.91 against the calculated 0.69).')
newpage()

heading('Connection hardware | 1. Rectangular key')
p('<b>18-8 stainless straight key, 3/8 x 3/8 in cross section, cut 1/2 in long.</b> Specify cut length 12.70 +/-0.05 mm; the key is longer than it is wide, as required. A square is the standard equal-sided rectangular cross section for this shaft size. Cut from 36 in stock 92530A319; width and height tolerance -0.003/0 in. Use the assignment-only relation Sy=0.8 Sut, with proposed Sut=515 MPa for 18-8 stainless: Sy=412 MPa. [6,12]')
p('The sprocket has 28.575 mm overall width and 7.2136 mm tooth thickness. Put the tooth midplane at y=-50 mm and the hub above it: hub extent -46.3932 to -25.0318 mm. The key at y=-36.0 mm fits entirely within the un-toothed hub. Hub OD=2D=76.2 mm. Center the set screw over the key within +/-0.10 mm; the 12.7 mm key fully covers its flat tip. The 22.45 mm slot runs from y=-47.25 to -24.75 mm, ending 0.28 mm above the sprocket face; the shaft keyseat may extend past the hub.')
p('Mill a closed slot 22.45 +/-0.05 mm long and 9.525 +0.0254/-0 mm wide, with semicircular ends. Its minimum straight length is 22.40-9.5504=12.8496 mm, exceeding the key maximum 12.75 mm. Seat depth is 4.7625 +/-0.0254 mm. Deburr the key and clear the keyseat floor corners without removing the working side faces.')
eq(f"Ft = 2T/Dmin = 2(19630)/{I['D_min_mm']:.4f} = {K['F_N']:.3f} N\nbmin = hmin = 0.372 in = 9.4488 mm\nLmin = {I['key_length_mm']-I['key_length_tolerance_mm']:.3f} mm\nMinimum hub engagement = hmin - depthmax = {K['engagement_mm']:.4f} mm\ntau = Ft/(bmin Lmin) = {K['tau_MPa']:.3f} MPa\np = Ft/(engagement x Lmin) = {K['bearing_MPa']:.3f} MPa\nn_shear = Sy/(sqrt(3) tau) = {K['n_shear']:.2f}\nn_bearing = Sy/p = {K['n_bearing']:.2f}")
p('Both exceed 1.2. Mating shaft/hub yield strengths are higher than the key value. Maximum screw preload produces less than 14 MPa average compression over the key footprint. The shaft-fatigue check includes the key bearing pressure as a mean-stress allowance. No credit is taken for the closed slot resisting axial slip.')
sub('Key cost')
eq('Ckey = ($28.32 / 36 in)(0.50 in) = $0.3933')
p('For comparison, 12 in undersized 18-8 stock costs $10.49, and a precut 1 in key costs $14.38/5=$2.876 each. The cut stock is less expensive. Saw kerf/deburring are not charged under the stated material-only assumption; the nominal design cost used for grading is not supplied.')
p('Cut-length trials with correspondingly shortened slots give shaft fatigue factors '+', '.join(format(t['shaft_nf'],'.3f')+' at '+{.125:'1/8',.1875:'3/16',.25:'1/4',.5:'1/2'}[t['length_in']]+' in' for t in O['key_length_trials'])+'. Keys shorter than their 3/8 in width are excluded by the course rule that a key must be longer than it is wide; 1/2 in is the shortest common fraction that satisfies it.',small=True)
newpage()

heading('Connection hardware | 2. Set screw')
p('<b>McMaster 94355A533: 18-8 stainless, flat tip, 1/4-20 UNC, 1/4 in long, 1/8 in hex drive.</b> The 6.35 mm length is recessed in the 19.05 mm radial hub wall and provides at least 4.5 mm of full engaged thread after runouts. Tap at the key center. The flat tip is suitable for the flat key surface and avoids relying on uncontrolled cup-point penetration. [5]')
p('Assume friction coefficient mu >=0.10 at both the screw/key and key/shaft interfaces, and nut factor K=0.15-0.25. These are assembly assumptions, not catalog guarantees. Tighten to 0.75 +/-0.02 N m. The key and sprocket are both retained through the friction path; capacities at the two series interfaces are not added.')
eq(f"Fmin = Tmin/(Kmax d) = 0.73/(0.25 x 0.00635) = {C['Fmin_N']:.2f} N\nFmax = Tmax/(Kmin d) = 0.77/(0.15 x 0.00635) = {C['Fmax_N']:.2f} N\nFhold = mu Fmin = {C['axial_hold_N']:.2f} N\nn_slip = Fhold/35 = {C['n_slip']:.3f} >=1.2")
p('For a conservative elastic screening check use Sy=205 MPa for 18-8, root diameter 4.57 mm, and the full 1/8 in hex socket area removed at the critical section. A circumscribed circular socket is removed for the polar-moment estimate. The full installation torque is conservatively applied at this reduced section. The root/tip dimensions are conservative assumptions compatible with the specified standard; verify the supplier drawing before fabrication.')
eq(f"A = pi dr^2/4 - (sqrt(3)/2) AF^2 = {C['Aroot_mm2']:.3f} mm^2\nJ = pi[dr^4 - (2AF/sqrt(3))^4]/32 = {C['Jroot_mm4']:.3f} mm^4\nsigma = Fmax/A = {C['compression_MPa']:.2f} MPa\ntau = Tmax dr/(2J) = {C['torsion_MPa']:.2f} MPa\nsigma_VM = sqrt(sigma^2+3 tau^2) = {C['vm_MPa']:.2f} MPa\nny = 205/sigma_VM = {C['n_y']:.3f}")
eq(f"Thread shear area = 0.5 pi(5.4)(4.5) = {(.5*math.pi*5.4*4.5):.2f} mm^2\nn_thread = (205/sqrt(3))/(Fmax/Athread) = {C['n_thread']:.2f}\nUsing flat-tip diameter >=3.5 mm: n_tip = {C['n_tip']:.2f}")
p('The screw checks exceed 1.2, including installation stress and axial slip. Minimum hub yield is the key yield, 412 MPa, so internal-thread shear is less critical. At the key center the flat tip sits about 14.4 mm below the hub OD; the screw top is recessed about 8.0 mm and remains accessible with a long hex key. Assumed clean contacts must be preserved; lubrication or water ingress that lowers mu invalidates the slip result.')
eq('Cscrew = $4.81/25 = $0.1924')
newpage()

heading('Connection hardware | 3. Rotor pin')
p('<b>McMaster 98380A556: 416 stainless dowel pin, 1/4 in diameter x 3 in long.</b> Nominal length spans the rotor hub OD=2D=3 in. Diameter is +0.0001/+0.0003 in; minimum hardness HRC36; rated double-shear breaking load 7200 lbf. Proposed yield value: 760 MPa, the lower end of Swiss Steel\'s typical condition-T range (HRC27-31), used conservatively for the harder catalog pin. This is an explicit material assumption, not a supplier-certified yield minimum. The shaft HRC25 cap does not apply to the pin. [4,11]')
p('Place the pin at y=-180 mm, 30 mm below the hub top and within the allowed upper 40 mm. Shaft hole: 6.363-6.375 mm, giving clearance to the 6.35254-6.35762 mm pin. Retain the pin by a measured 0.00254-0.00508 mm diametral interference in one hub wall only; the opposite wall is clearance-fit. This avoids press-fit hoop stress at the shaft\'s transverse fatigue notch. The hub is assumed at least as strong as the pin, per Rev2.')
eq(f"Ft per shear plane = T/Dmin = {I['T_Nmm']/I['D_min_mm']:.3f} N\nFa per plane = 120/2 = 60 N\nR = sqrt(Ft^2 + Fa^2) = {P['R_per_plane_N']:.3f} N\ntau = R/(pi dp^2/4) = {P['tau_MPa']:.3f} MPa\nConservative pin bending bound: Mp = R D/2 = {P['M_Nmm']:.3f} N mm\nsigma_b = 32 Mp/(pi dp^3) = {P['bending_MPa']:.3f} MPa\nsigma_VM = {P['vm_MPa']:.3f} MPa; ny = {P['n_y']:.3f}")
p('The pin is checked for bending as well as double shear. The D/2 lever-arm bound exceeds the normal distributed-contact lever arm. Using at least 10 mm of full-diameter engagement per hub wall (19.05 mm nominal wall, with generous allowance for pin-end relief), bearing pressure is '+f(P['bearing_MPa'])+' MPa and bearing safety factor is '+f(P['n_bearing'])+'. A 3/16 in pin would have about 933 MPa bending stress under the same bound and fails the adopted yield criterion.')
eq('Interference-fit estimate: p approximately E(delta/d)/2\nAt delta = 0.00254-0.00508 mm, d=6.35 mm, E=205000 MPa:\n  p approximately 41-82 MPa; use pmax=85 MPa.\nBound combined bending/fit normal stress by sigma_b + 2pmax.\nVM with fit = '+f(P['vm_with_fit_MPa'])+' MPa; ny with fit = '+f(P['n_y_with_fit']))
p('With mu=0.10, pmin=40 MPa and 10 mm engagement, the conservative axial pin-retention force is mu p pi dp Le='+f(P['retention_min_N'])+' N, far above the pin\'s own weight. Pin length tolerance/end relief must leave the stated engagement; center it during installation. The 7200 lbf catalog breaking-load ratio is '+f(P['breaking_capacity_ratio'])+'; this is an additional ultimate check and is not mislabeled as yield safety factor.')
eq('Cpin = $4.69 each')
newpage()

heading('Connection hardware | 4. Retaining rings')
p('<b>Two identical McMaster 93576A210 rings:</b> 18-8 stainless, one turn, for 1.500 in shafts, thickness 0.025 +/-0.002 in. Catalog thrust rating 4950 lbf. Both are checked against the full downward thrust '+f(O['total_thrust_N'])+' N, even though the upper ring carries the normal gravity load. [3]')
eq('Catalog capacity = 4950(4.44822) = '+f(Q['catalog_thrust_N'])+' N\nCatalog allowable-load ratio = capacity / thrust = '+f(Q['capacity_ratio']))
p('Do not infer the ring material\'s yield strength from the thrust rating. Smalley lists its corresponding geometric VS-150 ring shear rating with a built-in factor of 3 and groove rating separately. The McMaster stainless rating is used as the supplier\'s allowable capacity; the large load ratio exceeds the required 1.2 without needing to reinterpret it as a coupon yield strength. [8]')
sub('Groove wall and end-margin checks')
eq(f"Minimum groove depth = (37.9984 - 37.0840)/2 = {Q['depth_min_mm']:.4f} mm\nUsable flat radial contact after radius = depthmin - 0.254 = {Q['flat_contact_mm']:.4f} mm\nAcontact = pi droot x usable_contact\nn_groove_bearing = Sy Acontact / thrust = {Q['n_groove_bearing']:.2f}\nMinimum nominal top end margin = {Q['edge_margin_mm']:.4f} mm\n3 x maximum groove depth = {3*G['t_max_mm']:.4f} mm")
p('Allowing the stated 0.10 mm end-length and 0.05 mm groove-location tolerances still leaves more than 2.41 mm end margin, exceeding 3t=1.5621 mm. The lower groove is far from either shaft end. An end-lip shear check and an annular cantilever-lip bending check give factors greater than 500 and 700 respectively; therefore the end material is adequate. [9]')
eq('Aedge = pi droot e\ntau_edge = thrust/Aedge\nsigma_edge,b = 6 thrust depth/(pi droot e^2)')
sub('Bearing interface and axial freedom')
p('The ring must contact the rotating bearing inner race, with clearance to stationary housing and outer race. Corresponding ring radial width is 0.088 +/-0.004 in. Using maximum groove depth, a 0.50 mm maximum inner-race chamfer remains below the approximately 0.60 mm geometric recommendation 0.375(b-depth). Specify this requirement to the bearing designer. Bearing faces must be perpendicular to the shaft; eccentric ring loading is not assumed.')
p('The drawing\'s groove widths allow axial clearance. At nominal ring thickness, the full 300 mm outside-face bearing stack has roughly 0.50 mm total axial freedom when the rings bear against their loaded groove walls. Ring, groove and position tolerances produce a small range around this value; no preload is imposed. Bearing-stack tolerance must be coordinated before release. A 0.5 mm shift of the drag line changes the section moments by 560(0.5) = 0.28 N m, about 0.1%, which the safety factors cover. Low-speed operation is assumed; Smalley lists 5900 rpm for this geometry, but final bearing/speed selection is outside Rev2\'s supplied data.')
eq('Crings = 2($10.26/5) = $4.1040')
newpage()

heading('Drawing and bill of materials')
p('The separate shaft-only drawing is <b>DP2_shaft_drawing_PROVISIONAL.pdf</b>; its editable 2-D source is <b>DP2_shaft_P3.dxf</b>. In the assembled packet, the drawing immediately follows this bill of materials, keeping the required section consecutive. Only the shaft is drawn, as required. The geometry is dimensioned for review/quotation, with release conditional on the stated interface assumptions.')
table(['Item / McMaster part','Quantity and prorating','Cost ($)'],[
 [row['item']+'<br/><b>'+row['part']+'</b>',row['quantity'],f(row['cost'])] for row in O['bom']
 ],[285,145,80])
eq('Shaft length = 554/25.4 = 21.8110 in, cut from 24 in stock\nCshaft = full price of 1346K534 (shortest stock long enough) = $112.69\nTotal before rounding = $'+format(O['total_cost_USD'],'.6f')+'\nMachining charge for shaft grooves, hole, keyway = $0 by Rev2')
p('The displayed total is rounded only after summing unrounded line values. The shaft is charged at the full stock price; hardware is prorated per item, so buying whole packages costs more. Freight, tax and unlisted fabrication charges are not estimated. No purchase has been made.')
sub('Requirement audit')
table(['Rev2 requirement','Evidence / status'],[
 ['Shaft yielding >=3.0','Shigley minimum '+format(min(s['ny_shigley'] for s in S),'.3f')+' (keyseat); supplemental elastic minimum '+format(min(s['ny_elastic'] for s in S),'.3f')+' (groove), at the approved Sy='+f(I['Sy_MPa'])+' MPa.'],
 ['Infinite-life fatigue >=1.2','Minimum '+format(min(s['nf'] for s in S),'.3f')+', at the conservative keyseat envelope.'],
 ['Hardware >=1.2','Key >23; screw minimum 1.275; pin 1.347 including fit bound; rings >1.2.'],
 ['Eligible material and source','1566 precision rotary shaft (HRC25, within the cap); stainless key/screw/rings; 416 pin; all McMaster part numbers.'],
 ['No chrome; coating allowance','Uncoated selected shaft; $100 added.'],
 ['Approved shaft material properties','Sy = 88 ksi from the Piazza-approved list (1566, HRC25, D <= 1.5 in); Sut from Eq. (2-36).'],
 ['Separate CAD PDF / assembled drawing','Provided; no hardware drawings.'],
 ['Nominal-cost score thresholds','Cannot determine: nominal design cost is not supplied.'],
 ],[200,310])
newpage()

heading('Review record | Sources')
sources=[
 ('1','Assignment','Fall2026DP2-RotorShaft-Rev2.pdf, supplied local file; requirements and dimensions.'),
 ('2','Selected shaft','https://www.mcmaster.com/1346K534/'),
 ('3','Retaining rings','https://www.mcmaster.com/93576A210/'),
 ('4','416 pin family','https://www.mcmaster.com/98380A556/'),
 ('5','Set screw','https://www.mcmaster.com/94355A533/'),
 ('6','Key stock','https://www.mcmaster.com/92530A319/'),
 ('7','Approved shaft properties','Instructor post on the course Piazza, 10 Nov 2026 (approved yield strengths for DP2 shaft materials).'),
 ('8','Corresponding spiral ring geometry','https://www.smalley.com/ring/vs-150'),
 ('9','Groove radii, edge margins, contact geometry','https://www.smalley.com/engineering-support/ring-design'),
 ('10','Shigley 8th ed., Tables A-15 and A-16 (original excerpt)','https://disbasicoupiita.wordpress.com/wp-content/uploads/2013/03/factor-concentracion-esfuerzos.pdf'),
 ('11','416 typical heat-treated strengths, p.2','https://swisssteel-group.com/content-media/documents/Data-Sheets/Swiss-Steel-USA-Canada/Stainless-Steel/SwissSteel_416__Stainless__4-21.pdf'),
 ('12','ATI 304 flat-product baseline; assumed for 18-8 hardware','https://www.atimaterials.com/Products/ati-304'),
 ('13','Alternative condition warning','https://www.pmtsco.com/1040-45-turned-polished'),
 ('14','1045 size-dependent cold-drawn properties, section 4.3','https://www.wakefieldmetals.co.nz/wp-content/uploads/2019/11/steelTechnicalData.pdf'),
 ('15','Shigley 10th ed., Sec.3-13, Eq.(3-48); Sec.7-4, Eqs.(7-15)-(7-16), p.362','https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf'),
 ]
for n,label,url in sources:
    if url.startswith('https:'):p(f'[{n}] {label}: <link href="{url}" color="#165b79">{html.escape(url)}</link>',True)
    else:p(f'[{n}] {label}: {html.escape(url)}',True)
p('Catalog prices were read live in the McMaster browser on 2026-11-08/10. Sources [13] and [14] are kept from the earlier 1045 property review.',True)
(ROOT/'piazza_property_request.md').write_text('# DP2 shaft properties\n\nNo request needed. Rev P3 uses McMaster 1346K534 (1566, Rockwell C25, 1.500 in), whose yield strength Sy = 88 ksi is on the instructor-approved Piazza list (10 Nov 2026). Sut = 3.4 HB = 3.4(253) = 860.2 MPa (Shigley Eq. 2-36). The earlier 1045 request (703/598 MPa) is superseded.\n')

def footer(c,doc):
    c.saveState();w,h=letter;c.setStrokeColor(colors.HexColor('#d4dde2'));c.line(42,38,w-42,38)
    c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#526570'))
    c.drawString(42,25,'DP2 / ANALYSIS REV P3 / SHAFT 1346K534, PIAZZA-APPROVED PROPERTIES')
    c.drawRightString(w-42,25,'Source record' if doc.page==13 else str(doc.page));c.restoreState()

base=OUT/'DP2_calculations_PROVISIONAL.pdf'
doc=SimpleDocTemplate(str(base),pagesize=letter,rightMargin=45,leftMargin=45,topMargin=38,bottomMargin=48,title='DP2 design review - provisional calculations')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
writer=PdfWriter()
# Keep the three required grading sections contiguous; the source appendix follows.
nbase=len(PdfReader(str(base)).pages)
writer.append(str(base),pages=(0,nbase-1));writer.append(str(drawpath))
writer.append(str(base),pages=(nbase-1,nbase))
with (OUT/'DP2_design_review_PROVISIONAL.pdf').open('wb') as fp:writer.write(fp)
(ROOT/'design_review.md').write_text('\n'.join(md))
(ROOT/'README.md').write_text('''# DP2 review record

Status: Rev P3 calculation/drawing package. Shaft McMaster 1346K534 (1566,
Rockwell C25, 1-1/2 x 24 in) with the Piazza-approved Sy = 88 ksi and
Sut = 3.4 HB = 860.2 MPa. Cost rule: full price of the shortest sufficient
stock plus prorated hardware. The catalog-wide search is in ../solver/.

Both yield checks pass: Shigley Kf/Kfs (needs Sy >= 500.9 MPa) and the added
Kt/Kts elastic check (needs Sy >= 591.4 MPa).

Files:
- `calculate.py`: auditable assumptions, equations, equilibrium/criterion checks.
- `data/results.json`, `data/shaft_sections.csv`, `data/bom.csv`: full-precision results.
- `sources/catalog_observations.csv`: dated part/length/price comparisons.
- `design_review.md`: editable report trace.
- `piazza_property_request.md`: note that the approved list covers this shaft.
- `build_report.py`: plots and vector drawing/PDF/DXF generation.
- `cad/DP2_shaft_P3.dxf`: editable 2-D drawing, paper geometry in millimeters.
- `../../output/pdf/DP2_design_review_PROVISIONAL.pdf`: assembled report and drawing.
- `../../output/pdf/DP2_shaft_drawing_PROVISIONAL.pdf`: separate shaft-only drawing.

Reproduce calculations with `python3 calculate.py`. To rebuild the report use a
Python environment with numpy, matplotlib, reportlab and pypdf, then execute
`python3 build_report.py`. The report builder imports the calculation module,
regenerates the results and checks all numerical acceptance criteria.

The original assignment, prior plan and earlier figures were not modified.
''')
print('Created',base,drawpath,OUT/'DP2_design_review_PROVISIONAL.pdf')
print('Calculation PDF pages:',len(PdfReader(str(base)).pages))
