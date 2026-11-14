(function(){
"use strict";
const $ = id => document.getElementById(id);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------------- what each clickable item is ---------------- */
const F = {
  drag:{t:'Drag, D',v:'560 N in +z',d:'Water stream on the rotor, acting at the centre of pressure y = −500 mm. Its 506 mm lever arm to the lower bearing makes it the load that sizes the shaft.',s:'s2',c:'--c-water',chip:'Drag',val:'560 N'},
  chain:{t:'Chain force, F_c',v:'161.8 N at −4.732° → (161.25, 0, +13.35) N',d:'Tight span at the chain line, y = −50 mm. Eqs. (1)–(2). The +z part adds to the drag (conservative sign).',s:'s2',c:'--c-chain',chip:'Chain force',val:'161.8 N'},
  wr:{t:'Rotor + blade weight',v:'120 N down',d:'At the rotor CG, y = −350 mm. Carried into the shaft by the pin; the shaft hangs from the upper ring.',s:'s2',c:'--c-weight',chip:'Rotor weight',val:'120 N'},
  ws:{t:'Sprocket weight',v:'35 N down',d:'Held by the set screw through friction at two contacts: n_slip = 2(0.15)(141.7)/35 = 1.22.',s:'s12',c:'--c-weight',chip:'Sprocket weight',val:'35 N'},
  wsh:{t:'Shaft self-weight',v:'48.62 N down',d:'ρg(πD²/4)L for the 554 mm shaft, Eq. (3). Drawn at mid-length.',s:'s2',c:'--c-weight',chip:'Shaft weight',val:'48.6 N'},
  tw:{t:'Water torque',v:'19.63 N·m about +y',d:'Enters the shaft at the pin, y = −185 mm. Only the stretch from the pin up to the key is twisted.',s:'s2',c:'--c-water',chip:'Water torque',val:'19.63 N·m'},
  tc:{t:'Chain torque',v:'19.63 N·m, opposite',d:'Leaves the shaft through the key into the sprocket. ΣM_y = 0, so the bearings carry no torque.',s:'s2',c:'--c-chain',chip:'Chain torque',val:'19.63 N·m'},
  rl:{t:'Lower bearing reaction, R_L',v:'(−192.88, 0, −1562.93) N · |R_L| = 1574.8 N',d:'At the lower bearing midplane, y = 6.35 mm. Pushes upstream at 2.8 times the drag because of the overhang. Eqs. (6), (8).',s:'s3',c:'--c-react',chip:'R_L',val:'1574.8 N'},
  ru:{t:'Upper bearing reaction, R_U',v:'(+31.63, 0, +989.59) N · |R_U| = 990.1 N',d:'At the upper bearing midplane, y = 293.65 mm. Pulls downstream to stop the shaft tipping. Eqs. (5), (7).',s:'s3',c:'--c-react',chip:'R_U',val:'990.1 N'},
  thrust:{t:'Axial thrust on the upper ring',v:'N = 203.62 N up',d:'The upper bearing pushes up on the upper ring; all three weights hang below it. Eq. (4). Both rings are checked for it.',s:'s3',c:'--c-react',chip:'Ring thrust',val:'203.6 N'},
  'groove-l':{t:'Lower ring groove (critical)',v:'M = 280.5 N·m, T = 0 · n_y = 3.92 (Eq 7-15), n_f = 1.43',d:'Root Ø36.98–37.08 mm, R 0.20–0.25 mm, K_t = 3.6 at the worst corner (Fig. A-15-16). Governs yield and fatigue.',s:'s9',c:'--c-feat',chip:'Lower groove',val:'n_f 1.43'},
  'groove-u':{t:'Upper ring groove',v:'M = 0, T = 0',d:'Same groove section. Carries the 203.6 N thrust; 2.56 mm of shaft above it (≥ 3t = 1.68 mm).',s:'s14',c:'--c-feat',chip:'Upper groove',val:'M = 0'},
  keyseat:{t:'Keyseat (closed slot)',v:'22.225 × 9.525, 3/16 in deep at the wall (B17.1), y −47.11 to −24.89',d:'Upper end (longest slot, y −24.65): M = 266.6 N·m, T = 19.63 N·m. End centres 12.70 H14, width +0.051/−0, fillet R 1/32 in (B17.1). Peterson K_t 2.17, K_ts 2.59. n_f = 2.02, n_y = 5.61.',s:'s9',c:'--c-feat',chip:'Keyseat',val:'n_f 2.02'},
  pinhole:{t:'Pin hole, Ø6.37 mm',v:'M = 178.2 N·m, T = 19.63 N·m · n_y = 6.31, n_f = 2.28',d:'Transverse hole, a/D = 0.168. Table A-16: K_t 2.114 (A 0.732), K_ts 1.606 (A 0.856).',s:'s9',c:'--c-feat',chip:'Pin hole',val:'n_f 2.28'},
  plain:{t:'Plain section at the lower bearing',v:'M = 284.5 N·m · n_y = 11.5, n_f = 4.95',d:'Largest moment on the shaft but no notch, ground surface.',s:'s9',c:'--c-feat',chip:'Plain section',val:'n_f 4.95'},
  key:{t:'Key, 18-8, 3/8 × 3/8 × 1/2 in',v:'F = 1033.2 N · n_shear = 26.7, n_bearing = 15.2',d:'Cut 12.70 h14 from 92530A319; longer than it is wide; long edges chamfered 3/64 in (B17.1). Centred at y = −36 under the set screw.',s:'s11',c:'--c-hw',chip:'Key',val:'1/2 in'},
  screw:{t:'Set screw, 1/4"-20 × 1/4 in flat tip',v:'Clamp 142–236 N · n_slip = 1.22, thread n = 4.74',d:'94355A533, 18-8. Through the sprocket hub, presses on the key. 0.24 N·m (K 0.2, μ 0.15).',s:'s12',c:'--c-hw',chip:'Set screw',val:'0.24 N·m'},
  pin:{t:'Pin, 416 stainless, 1/4 × 3 in',v:'R = 520.1 N per shear plane · n = 30.8 vs 7200 lbf rating',d:'98380A556 at y = −185, spanning the 3 in hub. Shaft hole 6.35 F7 (slip); hub holes 0.2495–0.2500 in (B18.8.2 press fit).',s:'s13',c:'--c-hw',chip:'Pin',val:'n 1.35'},
  'ring-l':{t:'Lower retaining ring',v:'93576A210 · 4950 lbf rating',d:'18-8 single-turn spiral ring below the lower bearing. Unloaded in normal operation, still checked for 203.6 N.',s:'s14',c:'--c-hw',chip:'Lower ring',val:''},
  'ring-u':{t:'Upper retaining ring',v:'93576A210 · capacity/N = 108',d:'Sits on the upper bearing and carries the whole 203.6 N thrust.',s:'s14',c:'--c-hw',chip:'Upper ring',val:'×108'},
  'bearing-l':{t:'Lower bearing',v:'12.7 mm wide, midplane y = 6.35',d:'Assumption A2: the 300 mm runs between the outer bearing faces, so the midplanes are 287.3 mm apart.',s:'s1',c:'--c-steel',chip:'Lower bearing',val:''},
  'bearing-u':{t:'Upper bearing',v:'12.7 mm wide, midplane y = 293.65',d:'Assumption A2. Supports the shaft radially; the upper ring rests on it.',s:'s1',c:'--c-steel',chip:'Upper bearing',val:''},
  sprocket:{t:'Sprocket',v:'1.125 in wide, 0.284 in teeth, hub OD 76.2 mm',d:'Tooth midplane on the chain line y = −50; the un-toothed hub (−46.39 to −25.03) holds the key and set screw.',s:'s11',c:'--c-part',chip:'Sprocket',val:''},
  hub:{t:'Rotor hub',v:'100 mm long (y −250 to −150), OD 76.2 mm at the pin',d:'Carries the drag into the shaft by contact; the pin carries torque and weight (A4).',s:'s1',c:'--c-part',chip:'Rotor hub',val:''},
  shaft:{t:'Shaft, McMaster 1346K534',v:'1566 HRC25, Ø1.500 in × 554 mm from 24 in stock · $112.69',d:'Approved S_y 88 ksi = 606.7 MPa; S_ut = 3.4(253) = 860.2 MPa. Runs from y = −250.5 to +303.5.',s:'s6',c:'--c-steel',chip:'Shaft',val:'Ø1.5 in'},
  cg:{t:'Rotor centre of gravity',v:'y = −350 mm',d:'Where the 120 N rotor weight acts.',s:'s2',c:'--c-weight',chip:'CG',val:''},
  cop:{t:'Centre of pressure',v:'y = −500 mm',d:'Where the 560 N drag acts.',s:'s2',c:'--c-water',chip:'COP',val:''},
  mdiag:{t:'Bending moment diagram',v:'Peak 284.5 N·m at the lower bearing midplane',d:'Drawn on the −x side, scaled to the resultant M = √(M_x² + M_z²). Eqs. (9)–(11).',s:'s4',c:'--c-water',chip:'M diagram',val:'284.5 N·m'},
  tdiag:{t:'Torque diagram',v:'19.63 N·m from the pin (y −185) to the keyseat top (y −24.89)',d:'Drawn on the +x side. Zero at both bearings and both grooves.',s:'s4',c:'--c-chain',chip:'T diagram',val:'19.63 N·m'}
};
const ALIAS = { rings:['ring-l','ring-u'], applied:['drag','chain','wr','ws','wsh','tw','tc'], reactions:['rl','ru','thrust'] };
const expand = ids => [].concat(...ids.map(i=>ALIAS[i]||[i]));

const CHIPS = {
  s1:['bearing-l','bearing-u','hub','pin','thrust'],
  s2:['drag','chain','wr','ws','wsh','tw','tc','cg','cop'],
  s3:['rl','ru','thrust','drag','chain'],
  s4:['mdiag','tdiag','groove-l','keyseat','pinhole','plain'],
  s5:['groove-l','keyseat','pinhole','groove-u'],
  s6:['shaft'], s7:['groove-l','ring-l'], s8:['groove-l'],
  s9:['groove-l','keyseat','pinhole','plain','groove-u'],
  s10:['shaft'], s11:['key','keyseat','sprocket'], s12:['screw','key','ws'],
  s13:['pin','pinhole','tw','wr'], s14:['ring-u','ring-l','thrust','groove-u'],
  s15:['shaft','groove-l','groove-u','keyseat','pinhole'], s16:['shaft','rings','pin','screw','key']
};
const SCENE = {
  review:{f:[],view:'iso'}, s1:{f:['bearing-l','bearing-u','hub','pin'],view:'iso',all:true},
  s2:{f:['applied'],view:'iso',all:true,dims:true}, s3:{f:['rl','ru','thrust','drag','chain'],view:'front',all:true,dims:true,levers:true},
  s4:{f:['mdiag','tdiag'],view:'front',diag:true,dims:true,cut:true}, s5:{f:['groove-l','keyseat','pinhole'],view:'front',diag:true,dims:true,cut:true},
  s6:{f:['shaft'],view:'iso'}, s7:{f:['groove-l','ring-l'],view:'iso'}, s8:{f:['groove-l'],view:'iso'},
  s9:{f:['groove-l','keyseat','pinhole','plain'],view:'front'}, s10:{f:['shaft'],view:'iso'},
  s11:{f:['key','keyseat'],view:'iso'}, s12:{f:['screw','key'],view:'iso'}, s13:{f:['pin'],view:'iso'},
  s14:{f:['ring-l','ring-u','thrust'],view:'iso'}, s15:{f:['groove-l','groove-u','keyseat','pinhole'],view:'front',dims:true},
  s16:{f:['shaft','rings','pin','screw','key'],view:'iso'}, s17:{f:[],view:'iso'}, s18:{f:[],view:'iso'}
};

/* ---------------- geometry (mm), Rev P2 ---------------- */
const G = {r:19.05,yBot:-250.5,yTop:303.5,yL:6.35,yU:293.65,bw:12.7,gL:-0.49,gU:300.52,gW:0.81,
  ks0:-47.11,ks1:-24.89,k0:-42.35,k1:-29.65,ksD:5.367,ksW:9.525,yS:-36,
  sT0:-53.61,sT1:-46.39,sH1:-25.03,Rp:121.3,hub0:-250,hub1:-150,yPin:-185,yCG:-350,yCOP:-500,rot0:-255,rot1:-720,rotR:185};
function Mres(y){ // resultant bending moment, N·mm
  if (y>G.yU) return 0;
  if (y>=G.yL) return 990.09*(G.yU-y);
  if (y>=-50){ const mx=560*(y+500)+13.3477*(y+50), mz=161.2485*(y+50); return Math.hypot(mx,mz); }
  return 560*(y+500);
}
const Tor = y => (y>=G.yPin && y<=G.ks1) ? 19.63 : 0;

/* ---------------- three.js scene ---------------- */
const stage=$('stage'), labelsEl=$('labels');
if (!window.THREE || !THREE.OrbitControls){ stage.innerHTML='<p style="padding:16px">The 3D view needs three.js from cdnjs, which did not load. The walkthrough still works.</p>'; return; }
const renderer=new THREE.WebGLRenderer({canvas:$('c3d'),antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(2,window.devicePixelRatio||1));
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(30,1,2,30000);
const controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.1;
scene.add(new THREE.HemisphereLight(0xffffff,0x777766,.9));
const dl=new THREE.DirectionalLight(0xffffff,.6); dl.position.set(700,900,900); scene.add(dl);
const dl2=new THREE.DirectionalLight(0xffffff,.25); dl2.position.set(-700,-300,-600); scene.add(dl2);

let root=null, meshes=[], labels=[], focusSet=new Set(), opts={labels:true,diag:false,rotor:true,dims:false,levers:false,cut:false,cutY:-0.49};
const col = n => new THREE.Color(css(n)||'#888');
const BLACK=new THREE.Color(0,0,0);

function reg(obj,fid,o){ o=o||{}; obj.traverse(m=>{ if(!m.isMesh && !m.isLine) return; m.userData.fid=fid; m.userData.base=o.op!=null?o.op:1; m.userData.ctx=!!o.ctx; m.userData.pri=o.pri||1; m.userData.grp=o.grp||''; m.userData.only=!!o.only; m.userData.keep=!!o.keep; meshes.push(m); }); root.add(obj); return obj; }
function mat(c,o){ o=o||{}; const M=o.basic?THREE.MeshBasicMaterial:THREE.MeshStandardMaterial; const p={color:col(c),transparent:true,opacity:o.op!=null?o.op:1,side:THREE.DoubleSide}; if(!o.basic){p.metalness=o.metal!=null?o.metal:.25;p.roughness=.55;} return new M(p); }
function annulus(Ro,Ri,h,gap){ const s=new THREE.Shape();
  if (gap){ s.absarc(0,0,Ro,gap/2,Math.PI*2-gap/2,false); s.absarc(0,0,Ri,Math.PI*2-gap/2,gap/2,true); }
  else { s.absarc(0,0,Ro,0,Math.PI*2,false); const hp=new THREE.Path(); hp.absarc(0,0,Ri,0,Math.PI*2,true); s.holes.push(hp); }
  const g=new THREE.ExtrudeGeometry(s,{depth:h,bevelEnabled:false,curveSegments:56}); g.rotateX(-Math.PI/2); return g; }
function sprocketGeo(Ro,Rr,n,Ri,h){ const s=new THREE.Shape(), st=Math.PI*2/n;
  for (let i=0;i<n;i++){ const a=i*st; [[Rr,a],[Ro,a+.3*st],[Ro,a+.55*st],[Rr,a+.85*st]].forEach((p,j)=>{ const x=p[0]*Math.cos(p[1]), y=p[0]*Math.sin(p[1]); (i===0&&j===0)?s.moveTo(x,y):s.lineTo(x,y); }); }
  const hp=new THREE.Path(); hp.absarc(0,0,Ri,0,Math.PI*2,true); s.holes.push(hp);
  const g=new THREE.ExtrudeGeometry(s,{depth:h,bevelEnabled:false,curveSegments:24}); g.rotateX(-Math.PI/2); return g; }
function label(text,pos,fid,cvar,always,extra){ const el=document.createElement('div'); el.className='lbl'+(extra&&extra.cls?' '+extra.cls:''); el.innerHTML=text; if(cvar) el.style.setProperty('--lc','var('+cvar+')'); labelsEl.appendChild(el); const L=Object.assign({el,pos:new THREE.Vector3(...pos),fid,always},extra||{}); labels.push(L); return L; }
function arrowObj(tail,dir,len,rad,c){ const g=new THREE.Group(), m=mat(c,{basic:true}); const hl=Math.min(len*.35,rad*7);
  const sh=new THREE.Mesh(new THREE.CylinderGeometry(rad,rad,len-hl,12),m); sh.position.y=(len-hl)/2;
  const hd=new THREE.Mesh(new THREE.ConeGeometry(rad*2.6,hl,18),m); hd.position.y=len-hl/2; g.add(sh,hd);
  g.position.copy(tail); g.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize()); return g; }
const aLen = Fv => 6.4*Math.sqrt(Fv);
function force(fid,tail,v,c,text,headAt){ // headAt: arrow ends at tail point (pushes on it)
  const Fv=Math.hypot(...v), dir=new THREE.Vector3(...v).normalize(), len=aLen(Fv);
  const t=new THREE.Vector3(...tail); const start=headAt?t.clone().sub(dir.clone().multiplyScalar(len)):t;
  reg(arrowObj(start,dir,len,3.2,c),fid,{pri:3});
  const lp=headAt?start.clone().sub(dir.clone().multiplyScalar(12)):start.clone().add(dir.clone().multiplyScalar(len+12));
  label(text,[lp.x,lp.y,lp.z],fid,c,true);
}
function torque(fid,y,R,sign,c,text){ const g=new THREE.Group(), m=mat(c,{basic:true}); const arc=1.5*Math.PI;
  const tor=new THREE.Mesh(new THREE.TorusGeometry(R,2.6,8,80,arc),m); tor.rotation.x=-Math.PI/2; g.add(tor);
  const cone=new THREE.Mesh(new THREE.ConeGeometry(7.5,20,16),m); const ex=R*Math.cos(arc), ez=-R*Math.sin(arc);
  cone.position.set(ex,0,ez); cone.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),new THREE.Vector3(-Math.sin(arc),0,-Math.cos(arc))); g.add(cone);
  g.position.set(0,y,0); if (sign<0) g.scale.z=-1; reg(g,fid,{pri:3});
  label(text,[-R*.72,y+14,(sign<0?-1:1)*R*.72],fid,c,true); }

function build(){
  if (root){ scene.remove(root); root.traverse(o=>{ if(o.geometry) o.geometry.dispose(); if(o.material) o.material.dispose(); }); }
  labels.forEach(l=>l.el.remove()); labels=[]; meshes=[];
  root=new THREE.Group(); scene.add(root); scene.background=col('--stage');
  const r=G.r;
  // shaft
  const sh=new THREE.Mesh(new THREE.CylinderGeometry(r,r,G.yTop-G.yBot,64,1),mat('--c-steel',{metal:.45}));
  sh.position.y=(G.yTop+G.yBot)/2; reg(sh,'shaft',{ctx:true,pri:1});
  // plain-section marker and cut discs (only when focused)
  const cut=(fid,y)=>{ const d=new THREE.Mesh(new THREE.RingGeometry(r*1.15,r*1.6,48),mat('--glow',{basic:true,op:.5})); d.rotation.x=-Math.PI/2; d.position.y=y; reg(d,fid,{only:true,op:.5,pri:0}); };
  cut('plain',G.yL); cut('groove-l',G.gL); cut('keyseat',G.ks1); cut('pinhole',-181.81);
  // grooves (dark bands) and rings
  [['groove-l',G.gL],['groove-u',G.gU]].forEach(([f,y])=>{ const b=new THREE.Mesh(new THREE.CylinderGeometry(r+.15,r+.15,Math.max(G.gW,1.4),48,1,true),mat('--c-feat',{metal:.1})); b.position.y=y; reg(b,f,{pri:2}); });
  [['ring-l',G.gL],['ring-u',G.gU]].forEach(([f,y])=>{ const m=new THREE.Mesh(annulus(r+3.4,r-.5,.9,.45),mat('--c-hw',{metal:.5})); m.position.y=y-.45; reg(m,f,{pri:2}); });
  // keyseat slot (+x side), key, set screw
  const ksLen=G.ks1-G.ks0;
  const ks=new THREE.Mesh(new THREE.BoxGeometry(G.ksD+.4,ksLen,G.ksW),mat('--c-feat',{metal:.1})); ks.position.set(r-G.ksD/2+.2,(G.ks0+G.ks1)/2,0); reg(ks,'keyseat',{pri:2});
  const key=new THREE.Mesh(new THREE.BoxGeometry(G.ksW,G.k1-G.k0,G.ksW),mat('--c-hw',{metal:.4})); key.position.set(r,(G.k0+G.k1)/2,0); reg(key,'key',{pri:2});
  const scr=new THREE.Mesh(new THREE.CylinderGeometry(3.17,3.17,6.35,20),mat('--c-hw',{metal:.5})); scr.rotation.z=Math.PI/2; scr.position.set(r+G.ksW/2+3.2,G.yS,0); reg(scr,'screw',{pri:2});
  // sprocket
  const spr=new THREE.Group();
  const teeth=new THREE.Mesh(sprocketGeo(G.Rp+4,G.Rp-7,60,r+.4,G.sT1-G.sT0),mat('--c-part',{op:.35})); teeth.position.y=G.sT0; spr.add(teeth);
  const shub=new THREE.Mesh(annulus(2*r,r+.4,G.sH1-G.sT1),mat('--c-part',{op:.3})); shub.position.y=G.sT1; spr.add(shub);
  reg(spr,'sprocket',{op:.32,pri:1});
  // rotor hub and pin (pin axis along z)
  const hub=new THREE.Mesh(annulus(2*r,r+.4,G.hub1-G.hub0),mat('--c-part',{op:.3})); hub.position.y=G.hub0; reg(hub,'hub',{op:.3,pri:1});
  const pin=new THREE.Mesh(new THREE.CylinderGeometry(3.175,3.175,76.2,20),mat('--c-hw',{metal:.5})); pin.rotation.x=Math.PI/2; pin.position.set(0,G.yPin,0); reg(pin,'pin',{pri:2});
  const ph=new THREE.Mesh(new THREE.CylinderGeometry(3.6,3.6,2*r+1,20),mat('--c-feat',{op:.55})); ph.rotation.x=Math.PI/2; ph.position.set(0,G.yPin,0); reg(ph,'pinhole',{op:.0,pri:0,only:true});
  // bearings and support plates
  [['bearing-l',0],['bearing-u',287.3]].forEach(([f,y0])=>{ const b=new THREE.Mesh(annulus(2.1*r,r+.3,G.bw),mat('--c-steel',{metal:.6,op:.85})); b.position.y=y0; reg(b,f,{op:.85,pri:1}); });
  const sup=new THREE.Group(); const pw=190, pt=20;
  [[-pt,0],[300,0]].forEach(([y0])=>{ const s=new THREE.Shape(); s.moveTo(-pw/2,-pw/2); s.lineTo(pw/2,-pw/2); s.lineTo(pw/2,pw/2); s.lineTo(-pw/2,pw/2); s.lineTo(-pw/2,-pw/2);
    const hp=new THREE.Path(); hp.absarc(0,0,2.1*r+1,0,Math.PI*2,true); s.holes.push(hp);
    const g=new THREE.ExtrudeGeometry(s,{depth:pt,bevelEnabled:false,curveSegments:40}); g.rotateX(-Math.PI/2); const m=new THREE.Mesh(g,mat('--c-part',{op:.12})); m.position.y=y0; sup.add(m); });
  sup.userData.grp='rotor'; reg(sup,'supports',{op:.12,pri:0,grp:'rotor'});
  // rotor (schematic) + CG/COP
  const rot=new THREE.Group(); const rm=()=>mat('--c-part',{op:.1});
  const tp=new THREE.Mesh(annulus(G.rotR,2*r,4),rm()); tp.position.y=G.rot0-4; rot.add(tp);
  const bt=new THREE.Mesh(annulus(G.rotR,.01,4),rm()); bt.position.y=G.rot1; rot.add(bt);
  for (let i=0;i<4;i++){ const b=new THREE.Mesh(new THREE.BoxGeometry(G.rotR-2*r-6,G.rot0-G.rot1-8,4),rm()); const a=i*Math.PI/2+Math.PI/4, rr=(G.rotR+2*r)/2; b.position.set(rr*Math.cos(a),(G.rot0+G.rot1)/2,rr*Math.sin(a)); b.rotation.y=-a; rot.add(b); }
  reg(rot,'rotor',{op:.1,pri:0,grp:'rotor'});
  const lev=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,G.hub0,0),new THREE.Vector3(0,G.yCOP,0)]),new THREE.LineDashedMaterial({color:col('--muted'),dashSize:8,gapSize:6,transparent:true}));
  lev.computeLineDistances(); reg(lev,'rotor',{op:.8,pri:0,grp:'rotor'});
  [['cg',G.yCG,'--c-weight'],['cop',G.yCOP,'--c-water']].forEach(([f,y,c])=>{ const m=new THREE.Mesh(new THREE.SphereGeometry(7,18,12),mat(c,{basic:true})); m.position.set(0,y,0); reg(m,f,{pri:2}); label(f.toUpperCase(),[12,y-10,0],f,c,true); });
  // forces
  const RL=[-192.88,0,-1562.93], RU=[31.63,0,989.59];
  force('drag',[0,G.yCOP,0],[0,0,560],'--c-water','Drag 560 N');
  force('chain',[G.Rp+6,-50,0],[161.25,0,13.35],'--c-chain','Chain 161.8 N');
  force('wr',[0,G.yCG,0],[0,-120,0],'--c-weight','W rotor 120 N');
  force('ws',[-70,-36,0],[0,-35,0],'--c-weight','W sprocket 35 N');
  force('wsh',[-34,26.5,0],[0,-48.62,0],'--c-weight','W shaft 48.6 N');
  force('rl',[0,G.yL,2.1*r],RL,'--c-react','R<sub>L</sub> 1574.8 N',true);
  force('ru',[0,G.yU,-2.1*r],RU,'--c-react','R<sub>U</sub> 990.1 N',true);
  force('thrust',[r+8,G.gU-1,0],[0,203.62,0],'--c-react','Thrust 203.6 N',true);
  torque('tw',G.yPin,62,1,'--c-water','T<sub>water</sub> 19.63 N·m');
  torque('tc',-50,G.Rp+24,-1,'--c-chain','T<sub>chain</sub> 19.63 N·m');
  // M and T diagrams (planar ribbons in z = 0)
  const ribbon=(fid,fn,x0,k,y0,y1,c,sgn)=>{ const pos=[], n=260; for(let i=0;i<n;i++){ const ya=y0+(y1-y0)*i/n, yb=y0+(y1-y0)*(i+1)/n, a=fn(ya), b=fn(yb);
      pos.push(x0,ya,0, x0+sgn*k*a,ya,0, x0+sgn*k*b,yb,0,  x0,ya,0, x0+sgn*k*b,yb,0, x0,yb,0); }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
    const m=new THREE.Mesh(g,mat(c,{basic:true,op:.35})); const grp=new THREE.Group(); grp.add(m);
    const ln=[]; for(let i=0;i<=n;i++){ const y=y0+(y1-y0)*i/n; ln.push(new THREE.Vector3(x0+sgn*k*fn(y),y,0)); }
    grp.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ln),new THREE.LineBasicMaterial({color:col(c),transparent:true})));
    reg(grp,fid,{op:.6,pri:1,grp:'diag'}); };
  ribbon('mdiag',y=>Mres(y)/1000,-(r+14),0.45,G.yBot,G.yTop,'--c-water',-1);
  ribbon('tdiag',Tor,2*r+8,3.0,G.yBot,G.yTop,'--c-chain',1);
  label('M<sub>max</sub> 284.5 N·m',[-(r+14)-0.45*284.5-6,G.yL,0],'mdiag','--c-water',false);
  label('T 19.63 N·m',[2*r+8+3*19.63+8,-100,0],'tdiag','--c-chain',false);
  // part labels
  label('upper bearing',[2.1*r+10,G.yU,0],'bearing-u','--c-steel',false); label('lower bearing',[2.1*r+10,G.yL,0],'bearing-l','--c-steel',false);
  label('keyseat + key',[r+14,G.ks1+8,0],'keyseat','--c-feat',false); label('key 1/2 in',[r+12,G.k0,10],'key','--c-hw',false);
  label('set screw',[r+20,G.yS,0],'screw','--c-hw',false); label('pin',[0,G.yPin-8,40],'pin','--c-hw',false);
  label('pin hole',[r+8,G.yPin+8,0],'pinhole','--c-feat',false);
  label('lower groove',[-(r+8),G.gL-6,0],'groove-l','--c-feat',false); label('upper groove',[-(r+8),G.gU+6,0],'groove-u','--c-feat',false);
  label('lower ring',[r+6,G.gL-8,0],'ring-l','--c-hw',false); label('upper ring',[r+6,G.gU+8,0],'ring-u','--c-hw',false);
  label('plain section',[-(2.2*r),G.yL+8,0],'plain','--c-feat',false);
  label('sprocket',[G.Rp+8,G.sT1+14,0],'sprocket','--c-part',false); label('rotor hub',[2*r+10,G.hub1-12,0],'hub','--c-part',false);
  label('shaft Ø1.500',[-(r+6),180,0],'shaft','--c-steel',false);
  buildDims(); buildCut();
  // axes triad
  const ax=new THREE.Vector3(-330,230,-170);
  [['x',[1,0,0]],['y',[0,1,0]],['z',[0,0,1]]].forEach(([n,v])=>{ const a=arrowObj(ax,new THREE.Vector3(...v),60,1.4,'--ink'); root.add(a); label(n,[ax.x+v[0]*72,ax.y+v[1]*72,ax.z+v[2]*72],null,'--ink',true); });
  paint();
}

/* ---------------- dimensions: station ruler, lever arms, cut tool ---------------- */
const V=(x,y,z)=>new THREE.Vector3(x,y,z||0);
const lineGeo=pts=>new THREE.BufferGeometry().setFromPoints(pts);
const fmtN=(v,dp)=>{ const t=Math.abs(v).toFixed(dp==null?2:dp).replace(/\B(?=(\d{3})+(?!\d))/g,' '); return (v<0?'−':'')+t; };
function dimV(grp,x,y0,y1,text,c,ext,z,left){ z=z||0; const g=new THREE.Group(); const lm=new THREE.LineBasicMaterial({color:col(c||'--ink'),transparent:true});
  g.add(new THREE.Line(lineGeo([V(x,y0,z),V(x,y1,z)]),lm));
  [y0,y1].forEach(y=>g.add(new THREE.Line(lineGeo([V(x-7,y,z),V(x+7,y,z)]),lm)));
  if (ext!=null){ const em=new THREE.LineDashedMaterial({color:col(c||'--ink'),dashSize:4,gapSize:4,transparent:true,opacity:.6});
    [y0,y1].forEach(y=>{ const l=new THREE.Line(lineGeo([V(ext,y,z),V(x,y,z)]),em); l.computeLineDistances(); g.add(l); }); }
  const cm=mat(c||'--ink',{basic:true}), dir=Math.sign(y1-y0)||1, hl=Math.min(9,Math.abs(y1-y0)/3);
  if (hl>2){ [[y1,dir],[y0,-dir]].forEach(([y,d])=>{ const cn=new THREE.Mesh(new THREE.ConeGeometry(2.6,hl,10),cm); cn.position.set(x,y-d*hl/2,z); if(d<0) cn.rotation.z=Math.PI; g.add(cn); }); }
  reg(g,grp,{grp,keep:true,pri:0});
  label(text,[left?x-9:x+9,(y0+y1)/2,z],null,c,true,{grp,cls:'dim',left:!!left});
  return g; }
function buildDims(){
  const RX=250, r=G.r;
  const st=[[303.5,'303.5 top'],[300,'300 brg face'],[293.65,'293.65 R<sub>U</sub>'],[6.35,'6.35 R<sub>L</sub>'],[0,'0 brg face'],
    [-24.89,'−24.89 keyseat'],[-50,'−50 chain'],[-150,'−150 hub top'],[-185,'−185 pin'],[-250,'−250 shaft end'],[-350,'−350 CG'],[-500,'−500 COP']];
  const g=new THREE.Group(), lm=new THREE.LineBasicMaterial({color:col('--muted'),transparent:true});
  g.add(new THREE.Line(lineGeo([V(RX,-500),V(RX,303.5)]),lm));
  const gm=new THREE.LineDashedMaterial({color:col('--muted'),dashSize:3,gapSize:5,transparent:true,opacity:.55});
  st.forEach(([y,t])=>{ g.add(new THREE.Line(lineGeo([V(RX-6,y),V(RX+6,y)]),lm));
    const gl=new THREE.Line(lineGeo([V(RX,y),V(r,y)]),gm); gl.computeLineDistances(); g.add(gl);
    label(t,[RX,y,0],null,'--muted',true,{grp:'dims',lane:'ruler',cls:'dim ruler'}); });
  const pad=new THREE.Mesh(new THREE.BoxGeometry(2,2,2),mat('--muted',{basic:true,op:0})); pad.position.set(RX+110,0,0); g.add(pad);
  const padL=pad.clone(); padL.material=pad.material; padL.position.set(-360,0,0); g.add(padL);
  reg(g,'dims',{grp:'dims',keep:true,pri:0}); pad.material.opacity=0; pad.userData.base=0;
  // lever arms used in Eqs. (5)-(8): measured from the lower bearing midplane
  dimV('levers',-90,G.yL,G.yU,'L = 287.30','--c-react',-r,0,true);
  dimV('levers',-90,-50,G.yL,'56.35 (chain → R<sub>L</sub>)','--c-chain',-r,0,true);
  dimV('levers',-170,G.yCOP,G.yL,'506.35 (drag → R<sub>L</sub>)','--c-water',-r,0,true);
}
let cutGrp=null;
function buildCut(){ if(cutGrp){ root.remove(cutGrp); meshes=meshes.filter(m=>!cutGrp.getObjectById(m.id)); cutGrp.traverse(o=>{ if(o.geometry) o.geometry.dispose(); if(o.material) o.material.dispose(); });
    labels=labels.filter(l=>{ if(l.grp==='cut'){ l.el.remove(); return false; } return true; }); }
  const y=opts.cutY, r=G.r; cutGrp=new THREE.Group();
  const ring=new THREE.Mesh(new THREE.RingGeometry(r*1.15,r*2.6,48),mat('--glow',{basic:true,op:.6})); ring.rotation.x=-Math.PI/2; ring.position.y=y; cutGrp.add(ring);
  const m=Mres(y)/1000; const dot=new THREE.Mesh(new THREE.SphereGeometry(4.5,14,10),mat('--glow',{basic:true})); dot.position.set(-(r+14)-0.45*m,y,0); cutGrp.add(dot);
  cutGrp.add(new THREE.Line(lineGeo([V(-(r+14)-0.45*m,y),V(r*2.6,y)]),new THREE.LineBasicMaterial({color:col('--glow')})));
  root.add(cutGrp); reg(cutGrp,'cut',{grp:'cut',keep:true,pri:0});
  // lever arms from the cut down to each load below it
  const arms=[[G.yCOP,'y+500 = '+fmtN(y+500),'--c-water',-250]];
  if (y>-50) arms.push([-50,'y+50 = '+fmtN(y+50),'--c-chain',-215]);
  if (y>G.yL) arms.push([G.yL,'y−6.35 = '+fmtN(y-G.yL),'--c-react',-180]);
  arms.forEach(([yb,t,c,x])=>{ const g=dimV('cut',x,yb,y,t,c,-(r+14)-0.45*m,0,true); cutGrp.add(g); });
  label('cut y = '+fmtN(y),[-(r+14)-0.45*m-6,y+10,0],null,'--glow',true,{grp:'cut',cls:'dim'});
}
function setCut(y){ y=Math.max(-250,Math.min(303.5,y)); opts.cutY=y; $('cutY').value=y; $('cutOut').textContent=fmtN(y)+' mm';
  if(root){ buildCut(); paint(); }
  const Fz=13.35, Fx=161.25; let html;
  if (y>G.yU) html='Above the upper bearing nothing is below the cut that is not balanced: <b>M = 0</b>.';
  else if (y>=G.yL){ const M=990.09*(G.yU-y); html='Between the bearings (Eq. 11):<br>M = |R<sub>U</sub>|(293.65 − y) = 990.09('+fmtN(G.yU-y)+') = '+fmtN(M,0)+' N·mm<br><b>M = '+fmtN(M/1000)+' N·m</b>'; }
  else if (y>=-50){ const a=y+500,b=y+50, mx=560*a+Fz*b, mz=Fx*b, M=Math.hypot(mx,mz);
    html='Chain to lower bearing (Eq. 10):<br>|M<sub>x</sub>| = 560('+fmtN(a)+') + 13.35('+fmtN(b)+') = '+fmtN(mx,0)+'<br>|M<sub>z</sub>| = 161.25('+fmtN(b)+') = '+fmtN(mz,0)+'<br><b>M = √(M<sub>x</sub>² + M<sub>z</sub>²) = '+fmtN(M/1000)+' N·m</b>'; }
  else { const a=y+500, M=560*a; html=(y<-150?'Inside the hub, cantilever envelope (Eq. 9):':'Hub top to chain (Eq. 9):')+'<br>|M<sub>x</sub>| = 560('+fmtN(a)+') = '+fmtN(M,0)+' N·mm, M<sub>z</sub> = 0<br><b>M = '+fmtN(M/1000)+' N·m</b>'; }
  const T=Tor(y); html+='<br>T = '+(T?'19.63 N·m (between pin and key)':'0');
  $('cutEq').innerHTML=html; }

/* ---------------- highlighting ---------------- */
let preview=null;
function paint(){
  const set=preview||focusSet; const any=set.size>0; const glow=col('--glow');
  meshes.forEach(m=>{ const u=m.userData, f=u.fid, M=m.material;
    let vis=true;
    if (u.only) vis=set.has(f);
    if (u.grp==='diag') vis=opts.diag||set.has(f);
    if (u.grp==='rotor') vis=opts.rotor;
    if (u.grp==='dims') vis=opts.dims; if (u.grp==='levers') vis=opts.levers; if (u.grp==='cut') vis=opts.cut;
    m.visible=vis; if(!vis) return;
    let op=u.base;
    if (u.keep){ M.opacity=op; M.transparent=op<.999; return; }
    if (u.only) op=Math.max(u.base,.5);
    if (any && !set.has(f)) op = u.ctx ? .38 : (u.pri===3 ? .07 : Math.min(u.base,.9)*.16);
    if (any && set.has(f)) op = Math.max(u.base,.92);
    M.opacity=op; M.transparent=op<.999; M.depthWrite=op>.5;
    if (M.emissive){ M.emissive.copy(any&&set.has(f)?glow:BLACK); M.emissiveIntensity=any&&set.has(f)?.38:0; }
  });
  labels.forEach(l=>{ if(l.grp){ l.show=!!opts[l.grp]; return; } const on=l.fid&&set.has(l.fid);
    const show = on || (!any && opts.labels && l.always) || (!l.fid && opts.labels);
    l.show=show && (l.fid!=='mdiag'&&l.fid!=='tdiag' || opts.diag || on);
    l.el.classList.toggle('on',!!on); });
  document.querySelectorAll('[data-f]').forEach(e=>{ const ids=expand(e.dataset.f.split(',')); e.classList.toggle('on', ids.some(i=>focusSet.has(i))); });
}
const SECY={'groove-l':-0.49,'keyseat':-24.89,'pinhole':-181.81,'plain':6.35,'groove-u':300.5,'chain':-50,'mdiag':null};
function setFocus(ids,o){ o=o||{}; focusSet=new Set(expand(ids)); preview=null; if(opts.cut && ids.length && SECY[ids[0]]!=null) setCut(SECY[ids[0]]); paint();
  if (o.fly!==false && focusSet.size) fly([...focusSet],o.view);
  if (o.info) showInfo(ids[0]); else if(!o.keepInfo) hideInfo(); }

/* ---------------- camera ---------------- */
const VIEWS={iso:[.62,.3,.72],front:[0,0,1],side:[-1,0,0],top:[0,1,0.0001]};
let tween=null;
function boxOf(ids){ const b=new THREE.Box3(); let has=false;
  meshes.forEach(m=>{ if(ids.includes(m.userData.fid) && (m.visible||m.userData.only||m.userData.grp==='diag')){ const bb=new THREE.Box3().setFromObject(m); if(!bb.isEmpty()){ b.union(bb); has=true; } } });
  return has?b:null; }
function fly(ids,view){ const b=boxOf(ids)||boxOf(['shaft']); const c=b.getCenter(new THREE.Vector3());
  const dir = view ? new THREE.Vector3(...VIEWS[view]).normalize() : camera.position.clone().sub(controls.target).normalize();
  const up = view==='top' ? new THREE.Vector3(0,0,-1) : new THREE.Vector3(0,1,0);
  const right=new THREE.Vector3().crossVectors(up,dir).normalize(), upv=new THREE.Vector3().crossVectors(dir,right).normalize();
  let hw=30,hh=30,hd=0; [b.min,b.max].forEach(px=>[b.min,b.max].forEach(py=>[b.min,b.max].forEach(pz=>{ const v=new THREE.Vector3(px.x,py.y,pz.z).sub(c);
    hw=Math.max(hw,Math.abs(v.dot(right))); hh=Math.max(hh,Math.abs(v.dot(upv))); hd=Math.max(hd,Math.abs(v.dot(dir))); })));
  const t=Math.tan(camera.fov*Math.PI/360); const dist=Math.max(hh/t, hw/(t*camera.aspect))*1.12+hd;
  moveTo(c.clone().add(dir.multiplyScalar(dist)),c,up); }
function fitAll(view){ const ids=[...new Set(meshes.filter(m=>m.visible && m.userData.grp!=='diag' && m.userData.grp!=='cut').map(m=>m.userData.fid))]; fly(ids,view||'iso'); }
let instant=true;
function moveTo(pos,tgt,up){ camera.up.copy(up||new THREE.Vector3(0,1,0));
  if (reduce||instant){ camera.position.copy(pos); controls.target.copy(tgt); controls.update(); return; }
  tween={t0:performance.now(),dur:650,p0:camera.position.clone(),q0:controls.target.clone(),p1:pos,q1:tgt}; }
function stepTween(now){ if(!tween) return; let k=Math.min(1,(now-tween.t0)/tween.dur); k=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
  camera.position.lerpVectors(tween.p0,tween.p1,k); controls.target.lerpVectors(tween.q0,tween.q1,k); if(k>=1) tween=null; }

/* ---------------- labels + render ---------------- */
const v3=new THREE.Vector3();
function placeLabels(){ const w=stage.clientWidth,h=stage.clientHeight; const lanes={};
  labels.forEach(l=>{ if(!l.show){ l.el.style.display='none'; return; } v3.copy(l.pos).project(camera);
    if (v3.z>1||v3.z<-1){ l.el.style.display='none'; return; } l.el.style.display='';
    l.sx=(v3.x*.5+.5)*w; l.sy=(-v3.y*.5+.5)*h;
    if (l.lane){ (lanes[l.lane]=lanes[l.lane]||[]).push(l); return; }
    l.el.style.transform=l.left?'translate(calc('+(l.sx-4)+'px - 100%),'+(l.sy-10)+'px)':'translate('+(l.sx+4)+'px,'+(l.sy-10)+'px)'; });
  Object.values(lanes).forEach(arr=>{ arr.sort((a,b)=>a.sy-b.sy); let last=-1e9;
    arr.forEach(l=>{ const y=Math.max(l.sy,last+15); last=y;
      l.el.style.transform='translate('+(l.sx+8)+'px,'+(y-8)+'px)'; }); }); }
function resize(){ const w=stage.clientWidth||1,h=stage.clientHeight||1; renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(stage);
function loop(now){ requestAnimationFrame(loop); stepTween(now||performance.now()); controls.update(); renderer.render(scene,camera); placeLabels(); }

/* ---------------- picking ---------------- */
const ray=new THREE.Raycaster(), ptr=new THREE.Vector2(); let down=null;
renderer.domElement.addEventListener('pointerdown',e=>{ down=[e.clientX,e.clientY]; $('hint').hidden=true; });
renderer.domElement.addEventListener('pointerup',e=>{ if(!down) return; const moved=Math.hypot(e.clientX-down[0],e.clientY-down[1]); down=null; if(moved>5) return;
  const r=renderer.domElement.getBoundingClientRect(); ptr.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);
  ray.setFromCamera(ptr,camera); const hits=ray.intersectObjects(meshes.filter(m=>m.visible&&m.isMesh&&F[m.userData.fid]),false);
  if(!hits.length){ return; }
  hits.sort((a,b)=>(b.object.userData.pri-a.object.userData.pri)||(a.distance-b.distance));
  const f=hits[0].object.userData.fid; setFocus([f],{fly:false,info:true}); });

/* ---------------- info card ---------------- */
function showInfo(f){ const d=F[f]; if(!d){ hideInfo(); return; }
  $('infoT').textContent=d.t; $('infoV').textContent=d.v; $('infoD').textContent=d.d; $('info').style.setProperty('--ic','var('+d.c+')');
  const row=$('infoRow'); row.innerHTML='';
  const sec=document.getElementById(d.s); if(sec){ const b=document.createElement('button'); b.className='ib'; b.type='button'; b.textContent='Read in step '+(sec.querySelector('.n')||{}).textContent+' →'; b.onclick=()=>{ suppress=performance.now()+1500; sec.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'}); }; row.appendChild(b); }
  const z=document.createElement('button'); z.className='ib'; z.type='button'; z.textContent='Zoom to it'; z.onclick=()=>fly(expand([f])); row.appendChild(z);
  $('info').hidden=false; }
function hideInfo(){ $('info').hidden=true; }
$('infoX').onclick=hideInfo;

/* ---------------- text ↔ 3D wiring ---------------- */
const sections=[...document.querySelectorAll('section.step')];
sections.forEach(sec=>{ const ids=CHIPS[sec.id]; if(!ids) return;
  const bar=document.createElement('div'); bar.className='chips'; bar.innerHTML='<span class="lead">Show in 3D</span>';
  ids.forEach(i=>{ const d=F[i]||F[(ALIAS[i]||[])[0]]; const b=document.createElement('button'); b.type='button'; b.className='chip'; b.dataset.f=i;
    b.style.setProperty('--cc','var('+d.c+')'); b.innerHTML=(i==='rings'?'Rings (2)':d.chip)+(d.val&&i!=='rings'?'<small>'+d.val+'</small>':''); bar.appendChild(b); });
  const after=sec.querySelector('.sub')||sec.querySelector('h2'); after.insertAdjacentElement('afterend',bar); });
document.querySelectorAll('.ref[data-f]').forEach(b=>{ const d=F[expand([b.dataset.f.split(',')[0]])[0]]; if(d) b.style.setProperty('--cc','var('+d.c+')'); });
document.addEventListener('click',e=>{ const t=e.target.closest('[data-f]'); if(!t||t.closest('.bench')) return;
  const ids=t.dataset.f.split(','); if(lastClick===t.dataset.f && t.classList.contains('on') && t.matches('.chip,.ref')){ lastClick=null; setFocus([]); return; }
  lastClick=t.dataset.f; setFocus(ids,{info:true}); if(innerWidth<=1000) $('bench').classList.remove('min'); });
document.addEventListener('pointerover',e=>{ const t=e.target.closest('.chip[data-f],.ref[data-f],tr[data-f]'); if(!t||t.closest('.bench')) return; preview=new Set(expand(t.dataset.f.split(','))); paint(); });
document.addEventListener('pointerout',e=>{ const t=e.target.closest('.chip[data-f],.ref[data-f],tr[data-f]'); if(!t) return; if(e.relatedTarget&&t.contains(e.relatedTarget)) return; preview=null; paint(); });
document.addEventListener('keydown',e=>{ const t=e.target.closest&&e.target.closest('tr[data-f]'); if(t&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); t.click(); } });
document.querySelectorAll('tr[data-f]').forEach(t=>t.tabIndex=0);

/* ---------------- step tracking ---------------- */
const sel=$('stepSel');
sections.forEach(s=>{ const o=document.createElement('option'); o.value=s.id; const n=(s.querySelector('h2 .n')||{}).textContent||''; o.textContent=(n?n+'  ':'')+s.querySelector('h2').textContent.replace(n,'').trim(); sel.appendChild(o); });
let active=null, suppress=0, follow=true, lastClick=null;
function activate(id){ if(id===active) return; active=id;
  sections.forEach(s=>s.classList.toggle('active',s.id===id));
  sel.value=id; const s=document.getElementById(id); $('stepNo').textContent=(s.querySelector('h2 .n')||{}).textContent||'';
  $('prog').style.width=(100*sections.findIndex(x=>x.id===id)/(sections.length-1))+'%';
  if(follow) applyScene(id); }
function applyScene(id){ const sc=SCENE[id]; if(!sc) return;
  setDiag(!!sc.diag); setFlag('dims',!!sc.dims); setFlag('levers',!!sc.levers); setFlag('cut',!!sc.cut);
  focusSet=new Set(expand(sc.f)); preview=null; paint(); hideInfo();
  if (sc.all || !sc.f.length) fitAll(sc.view); else fly([...focusSet].concat(sc.dims?['dims']:[]),sc.view); }
function current(){ const line=innerWidth<=1000 ? innerHeight*.62 : innerHeight*.35; let c=sections[0];
  for (const s of sections){ if (s.getBoundingClientRect().top<line) c=s; } return c.id; }
let ticking=false, settle=null;
addEventListener('scroll',()=>{ if(ticking) return; ticking=true; requestAnimationFrame(()=>{ ticking=false;
  clearTimeout(settle); if(performance.now()<suppress){ settle=setTimeout(()=>activate(current()),1600); return; } activate(current()); }); },{passive:true});
sel.addEventListener('change',()=>{ const s=document.getElementById(sel.value); s.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'}); });
const go=d=>{ const i=sections.findIndex(x=>x.id===active); const n=sections[Math.max(0,Math.min(sections.length-1,i+d))]; n.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'}); };
$('prevStep').onclick=()=>go(-1); $('nextStep').onclick=()=>go(1);

/* ---------------- toolbar ---------------- */
function tog(id,fn){ const b=$(id); b.addEventListener('click',()=>{ const v=b.getAttribute('aria-pressed')!=='true'; b.setAttribute('aria-pressed',v); fn(v); }); }
function setDiag(v){ opts.diag=v; $('tDiag').setAttribute('aria-pressed',v); paint(); }
tog('tFollow',v=>{ follow=v; if(v&&active) applyScene(active); });
tog('tLabels',v=>{ opts.labels=v; paint(); });
tog('tDiag',v=>{ opts.diag=v; paint(); if(v) fly(['mdiag','tdiag'],'front'); });
tog('tRotor',v=>{ opts.rotor=v; paint(); });
function setFlag(k,v){ opts[k]=v; const id={dims:'tDims',cut:'tCut'}[k]; if(id) $(id).setAttribute('aria-pressed',v);
  if(k==='cut'){ $('cutBox').hidden=!v; stage.classList.toggle('cuton',v); $('hint').hidden=v||$('hint').hidden; if(v) setCut(opts.cutY); } paint(); }
tog('tDims',v=>{ setFlag('dims',v); setFlag('levers',v); });
tog('tCut',v=>{ setFlag('cut',v); if(v){ setDiag(true); fly(['mdiag','tdiag','dims'],'front'); } });
$('cutY').addEventListener('input',e=>setCut(+e.target.value));
document.querySelectorAll('[data-cut]').forEach(b=>b.addEventListener('click',()=>setCut(+b.dataset.cut)));
$('tClear').onclick=()=>{ setFocus([]); };
document.querySelectorAll('.views [data-view]').forEach(b=>b.addEventListener('click',()=>{ focusSet.size?fly([...focusSet],b.dataset.view):fitAll(b.dataset.view); }));
$('fitAll').onclick=()=>fitAll(null);
tog('minBench',v=>{ $('bench').classList.toggle('min',v); $('minBench').textContent=v?'Show 3D':'Hide 3D'; setTimeout(resize,50); });

/* ---------------- theme ---------------- */
const rethem=()=>{ build(); };
try{ matchMedia('(prefers-color-scheme: dark)').addEventListener('change',rethem); }catch(e){}
new MutationObserver(rethem).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});

build(); resize();
camera.position.set(900,250,1000); controls.target.set(0,-150,0); controls.update(); fitAll('iso'); instant=false;
requestAnimationFrame(loop);
activate(current());
setInterval(()=>{ if(performance.now()>suppress) activate(current()); },900);
window.__bench={setFocus,fly,F};
})();
