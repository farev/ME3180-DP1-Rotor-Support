"""Builds DP2_Walkthrough.html from content_v2.html (text) + addon.css + bench.html + bench.js."""
import re, pathlib
D=pathlib.Path(__file__).parent
s=(D/'content_v2.html').read_text()
head,rest=s.split('<style>',1); css,rest=rest.split('</style>',1)
main=re.search(r'<main>.*?</main>',rest,re.S).group(0)
oldjs=re.findall(r'<script>(.*?)</script>',rest,re.S)[-1]

def once(t,a,b):
    n=t.count(a); assert n==1,(a[:80],n); return t.replace(a,b)
def first(t,a,b):
    assert a in t,(a[:80]); return t.replace(a,b,1)
ref=lambda f,txt:f'<button type="button" class="ref" data-f="{f}">{txt}</button>'

# --- table rows -> 3D items ---
rows=[('<tr><td>Shaft top end</td>','groove-u'),('<tr><td>Upper bearing midplane, y<sub>U</sub></td>','bearing-u'),
('<tr><td>Lower bearing midplane, y<sub>L</sub></td>','bearing-l'),('<tr><td>Lower ring groove (centre)</td>','groove-l'),
('<tr><td>Keyseat (centre / upper end)</td>','keyseat'),('<tr><td>Chain line (tooth midplane)</td>','chain'),
('<tr><td>Top of rotor hub</td>','hub'),('<tr><td>Pin centre</td>','pin'),('<tr><td>Bottom of hub / shaft bottom end</td>','hub'),
('<tr><td>Rotor CG (120 N)</td>','wr'),('<tr><td>Centre of pressure (560 N drag, +z)</td>','drag'),
('<tr><td>Upper, y = 293.65</td>','ru'),('<tr class="hl"><td>Lower, y = 6.35</td>','rl'),
('<tr><td>Lower bearing midplane</td><td class="num">6.35</td>','plain'),('<tr class="hl"><td>Lower ring groove</td><td class="num">−0.49</td>','groove-l'),
('<tr><td>Keyseat upper end</td><td class="num">−24.75</td>','keyseat'),('<tr><td>Pin hole, upper edge</td>','pinhole'),
('<tr><td>Upper ring groove</td><td class="num">+300.5</td>','groove-u'),
('<tr><td>Overall length</td>','shaft'),('<tr><td>Stock OD</td>','shaft'),('<tr><td>Pin hole</td><td>Ø6.363','pinhole'),
('<tr><td>Keyseat</td><td>Centre 214.50','keyseat'),('<tr><td>Lower groove</td>','groove-l'),('<tr><td>Upper groove</td>','groove-u'),
('<tr><td>1566 HRC25 precision rotary shaft, Ø1.500 × 24 in</td>','shaft'),('<tr><td>18-8 single-turn spiral ring, 1.500 in</td>','rings'),
('<tr><td>416 dowel pin, 1/4 × 3 in</td>','pin'),('<tr><td>18-8 flat-tip set screw','screw'),('<tr><td>18-8 key stock, 3/8 in square, cut 1/2 in</td>','key')]
for a,f in rows:
    main=once(main,a,a.replace('<tr','<tr data-f="'+f+'"',1))

# --- in-text mentions ---
main=once(main,'The chain pulls with 161.8 N at θ = −4.732° from x', ref('chain','The chain pulls with 161.8 N')+' at θ = −4.732° from x')
main=once(main,'rotor 120 N (through the pin), sprocket 35 N (through key and set screw) and shaft self-weight:',
          ref('wr','rotor 120 N')+' (through the pin), '+ref('ws','sprocket 35 N')+' (through key and set screw) and '+ref('wsh','shaft self-weight')+':')
main=once(main,'Axially, the shaft hangs from the upper ring: thrust N = 203.62 N','Axially, the shaft hangs from the upper ring: '+ref('thrust','thrust N = 203.62 N'))
main=once(main,'Half a bearing width lower, the <b>lower retaining-ring groove</b>','Half a bearing width lower, the '+ref('groove-l','lower retaining-ring groove'))
main=once(main,'The <b>keyseat upper end</b> comes second','The '+ref('keyseat','keyseat upper end')+' comes second')
main=once(main,'The pin hole sees much less moment','The '+ref('pinhole','pin hole')+' sees much less moment')
main=once(main,'The upper groove sees no bending or torque.','The '+ref('groove-u','upper groove')+' sees no bending or torque.')
main=once(main,'<span class="tag d">D1</span><b>Shaft: McMaster 1346K534</b>','<span class="tag d">D1</span>'+ref('shaft','Shaft: McMaster 1346K534'))
main=once(main,'<span class="tag d">D3</span><b>Rings: McMaster 93576A210</b>','<span class="tag d">D3</span>'+ref('rings','Rings: McMaster 93576A210'))
main=once(main,'<b>18-8 stainless square key, 3/8 × 3/8 in, cut 1/2 in long</b>',ref('key','18-8 stainless square key, 3/8 × 3/8 in, cut 1/2 in long'))
main=once(main,'<span class="tag d">D10</span><b>Closed keyseat</b>','<span class="tag d">D10</span>'+ref('keyseat','Closed keyseat'))
main=once(main,'<span class="tag d">D11</span><b>McMaster 94355A533</b>','<span class="tag d">D11</span>'+ref('screw','McMaster 94355A533'))
main=once(main,'<span class="tag d">D12</span><b>McMaster 98380A556</b>','<span class="tag d">D12</span>'+ref('pin','McMaster 98380A556'))
main=once(main,'<span class="tag d">D3</span><b>Two McMaster 93576A210</b>','<span class="tag d">D3</span>'+ref('rings','Two McMaster 93576A210'))
main=once(main,'<h3>Lower ring groove (governs yield)</h3>','<h3>'+ref('groove-l','Lower ring groove')+' (governs yield)</h3>')
main=once(main,'<h3>Keyseat upper end (governs fatigue)</h3>','<h3>'+ref('keyseat','Keyseat upper end')+' (governs fatigue)</h3>')
main=once(main,'<h3>Pin hole (Shigley Table A-16, solid bar)</h3>','<h3>'+ref('pinhole','Pin hole')+' (Shigley Table A-16, solid bar)</h3>')
main=once(main,'<h3>z direction (drag and chain)</h3>','<h3>z direction ('+ref('drag','drag')+' and '+ref('chain','chain')+')</h3>')
main=once(main,'<h3>x direction (chain only)</h3>','<h3>x direction ('+ref('chain','chain')+' only)</h3>')
main=once(main,'<figure class="chartwrap"><svg id="mtSvg"','<p>'+ref('mdiag,tdiag','Show these diagrams on the 3D shaft')+'</p>\n  <figure class="chartwrap"><svg id="mtSvg"')
main=once(main,'<header class="top">','<header class="top">\n  <p class="src" style="margin:0 0 6px">Click any underlined term, chip or ◎ table row to highlight it on the 3D model. Scroll and the model follows the step you are reading.</p>')

# --- Sy table rows clickable ---
oldjs=once(oldjs,"{n:'Lower ring groove',","{f:'groove-l',n:'Lower ring groove',")
oldjs=once(oldjs,"{n:'Keyseat upper end',","{f:'keyseat',n:'Keyseat upper end',")
oldjs=once(oldjs,"{n:'Pin hole',","{f:'pinhole',n:'Pin hole',")
oldjs=once(oldjs,"{n:'Plain section at lower bearing',","{f:'plain',n:'Plain section at lower bearing',")
oldjs=once(oldjs,"{n:'Upper ring groove',","{f:'groove-u',n:'Upper ring groove',")
oldjs=once(oldjs,"const tr=document.createElement('tr'); if(a===minT) tr.className='hl';","const tr=document.createElement('tr'); if(a===minT) tr.className='hl'; tr.dataset.f=s.f; tr.tabIndex=0;")

out=(head+'<style>'+css+'\n'+(D/'addon.css').read_text()+'</style>\n'
 +'<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
 +'<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>\n'
 +'<div class="wrap">\n'+main+'\n'+(D/'bench.html').read_text()+'</div>\n'
 +'<script>'+oldjs+'</script>\n<script>\n'+(D/'bench.js').read_text()+'</script>\n')
(D.parent/'DP2_Walkthrough.html').write_text(out)
print('written',len(out))
