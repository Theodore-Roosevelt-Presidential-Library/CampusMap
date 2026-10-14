import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { draco } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import earcut from 'earcut';
import fs from 'fs';
const [,, inGlb, polysPath, routePath, outGlb] = process.argv;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule() });
const doc = await io.read(inGlb);
const root = doc.getRoot(); const buf = root.listBuffers()[0]; const scene = root.listScenes()[0];
const FT = f => (f + 38.3) / 33.3333333;     // feet above FFE -> model Y
const UNIT = 1 / 33.3333333;                  // one foot in model units
const P = JSON.parse(fs.readFileSync(polysPath)); const R = JSON.parse(fs.readFileSync(routePath));
const mat = (name, hex, extra={}) => { const c = [1,3,5].map(i => Math.pow(parseInt(hex.slice(i,i+2),16)/255, 2.2));
  const m = doc.createMaterial(name).setBaseColorFactor([...c,1]).setMetallicFactor(0).setRoughnessFactor(1); if (extra.double) m.setDoubleSided(true); return m; };
const M = { floor: mat('int floor','#FFFFFF'), blue: mat('int narrative','#C3D2E2'), mass: mat('int mass','#B8B2A7'),
  plate: mat('int plate','#B8B2A7'), floor2: mat('int floor upper','#FFFFFF'), route: mat('int route','#1F3552', {double:true}) };
function meshFrom(name, pos, nor, material) {
  const p = doc.createAccessor().setType('VEC3').setArray(new Float32Array(pos)).setBuffer(buf);
  const n = doc.createAccessor().setType('VEC3').setArray(new Float32Array(nor)).setBuffer(buf);
  const prim = doc.createPrimitive().setAttribute('POSITION', p).setAttribute('NORMAL', n).setMaterial(material);
  return doc.createMesh(name).addPrimitive(prim);
}
// cap (horizontal face at y) for polygon [outer, ...holes], each ring [[x,z],...]
function cap(poly, y, pos, nor) {
  const flat = [], holes = [];
  poly.forEach((r, i) => { if (i) holes.push(flat.length / 2); r.forEach(([x, z]) => flat.push(x, z)); });
  const tri = earcut(flat, holes, 2);
  for (let i = 0; i < tri.length; i += 3) {
    const a = tri[i], b = tri[i+1], c = tri[i+2];
    // ensure upward normal: in x,z with y up, CCW when viewed from +y means (b-a)x(c-a) has negative "z-cross"
    const ax=flat[2*a], az=flat[2*a+1], bx=flat[2*b], bz=flat[2*b+1], cx=flat[2*c], cz=flat[2*c+1];
    const cr = (bx-ax)*(cz-az) - (bz-az)*(cx-ax);
    const order = cr < 0 ? [a,b,c] : [a,c,b];
    for (const k of order) { pos.push(flat[2*k], y, flat[2*k+1]); nor.push(0,1,0); }
  }
}
function sides(poly, y0, y1, pos, nor) {
  for (const r of poly) for (let i = 0; i < r.length; i++) {
    const [x1, z1] = r[i], [x2, z2] = r[(i+1) % r.length];
    const dx = x2-x1, dz = z2-z1, L = Math.hypot(dx, dz) || 1; const nx = dz/L, nz = -dx/L;
    const q = [[x1,y0,z1],[x2,y0,z2],[x2,y1,z2],[x1,y0,z1],[x2,y1,z2],[x1,y1,z1]];
    for (const v of q) { pos.push(...v); nor.push(nx,0,nz); }   // double-sided material not needed: normals set; ring orientation varies, so make material double sided
  }
}
function slab(polys, yb, yt, withSides=true) { const pos=[], nor=[]; polys.forEach(p => { cap(p, yt, pos, nor); if (withSides) sides(p, yb, yt, pos, nor); }); return [pos, nor]; }
const interior = doc.createNode('INTERIOR'); scene.addChild(interior);
const add = (parent, name, [pos, nor], m) => { if (!pos.length) return; const n = doc.createNode(name).setMesh(meshFrom(name, pos, nor, m)); parent.addChild(n); };
M.mass.setDoubleSided(true); M.plate.setDoubleSided(true);
const L1 = doc.createNode('INT_L1'); interior.addChild(L1);
add(L1, 'INT_L1_floor', slab(P.L1.floor, FT(0), FT(0.4), false), M.floor);
add(L1, 'INT_L1_narrative', slab(P.L1.blue, FT(0), FT(0.55), false), M.blue);
add(L1, 'INT_L1_mass', slab(P.L1.mass, FT(0), FT(11)), M.mass);
const L2 = doc.createNode('INT_L2'); interior.addChild(L2);
add(L2, 'INT_L2_plate', slab(P.L2.plate, FT(0), FT(16)), M.plate);
add(L2, 'INT_L2_floor', slab(P.L2.floor, FT(16), FT(16.4), false), M.floor2);
add(L2, 'INT_L2_mass', slab(P.L2.mass, FT(16), FT(27)), M.mass);
// route: dashed ribbon + chevrons
{
  const pos=[], nor=[]; const y = FT(0.75), w = 0.55*UNIT, dash = 2.6*UNIT, gap = 2.2*UNIT;
  let carry = 0, sinceArrow = 10*UNIT;
  for (let i = 0; i < R.length-1; i++) {
    const [x1,z1] = R[i], [x2,z2] = R[i+1]; const L = Math.hypot(x2-x1, z2-z1); if (!L) continue;
    const ux=(x2-x1)/L, uz=(z2-z1)/L, px=-uz, pz=ux;
    let s = carry;
    while (s < L) {
      const e = Math.min(L, s + dash);
      const ax=x1+ux*s, az=z1+uz*s, bx=x1+ux*e, bz=z1+uz*e;
      const v=[[ax+px*w,az+pz*w],[bx+px*w,bz+pz*w],[bx-px*w,bz-pz*w],[ax+px*w,az+pz*w],[bx-px*w,bz-pz*w],[ax-px*w,az-pz*w]];
      v.forEach(([x,z]) => { pos.push(x,y,z); nor.push(0,1,0); });
      s = e + gap;
    }
    carry = s - L;
    // chevrons every ~22 ft
    let t = (22*UNIT - sinceArrow);
    while (t < L) {
      if (t >= 0) { const cx=x1+ux*t, cz=z1+uz*t, a=2.2*UNIT, b=1.8*UNIT;
        const tip=[cx+ux*a, cz+uz*a], l=[cx+px*b, cz+pz*b], r=[cx-px*b, cz-pz*b];
        [tip,l,r].forEach(([x,z]) => { pos.push(x,y+0.0005,z); nor.push(0,1,0); }); }
      t += 22*UNIT;
    }
    sinceArrow = (sinceArrow + L) % (22*UNIT);
  }
  const RN = doc.createNode('INT_ROUTE'); interior.addChild(RN);
  RN.setMesh(meshFrom('INT_ROUTE', pos, nor, M.route));
}

// ---------------- exterior details (from conformed elevations A300-A303, A320/A321, A275) ----------------
{
  const A = [[25.720819446257327,21.20260734259213],[-21.20260734259213,25.720819446257327]], T=[2609.6351988962733,1344.5456666231719];
  const det = A[0][0]*A[1][1]-A[0][1]*A[1][0];
  const toCM = (fx, fy) => { const a = fx - T[0], b = -fy - T[1]; return [( A[1][1]*a - A[0][1]*b)/det, (-A[1][0]*a + A[0][0]*b)/det]; };
  const toFT = (X, Z) => [A[0][0]*X + A[0][1]*Z + T[0], -(A[1][0]*X + A[1][1]*Z + T[1])];
  const glassMat = root.listMaterials().find(m => m.getName() === 'windows');
  const frameMat = mat('ext frame', '#3A342E'); frameMat.setDoubleSided(true);
  const woodMat = mat('ext alcove wood', '#9C7A55'); woodMat.setDoubleSided(true);
  const soffitMat = mat('ext alcove soffit', '#B08B62'); soffitMat.setDoubleSided(true);
  const paveMat = mat('ext alcove paving', '#BDB6AA');
  glassMat.setDoubleSided(true);
  const quad = (pos, nor, p1, p2, y0, y1, n) => { // vertical quad between plan points (feet) p1->p2
    const a = toCM(...p1), b = toCM(...p2); const dx=b[0]-a[0], dz=b[1]-a[1], L=Math.hypot(dx,dz)||1; const nn = n || [dz/L, 0, -dx/L];
    const Y0=FT(y0), Y1=FT(y1);
    [[a[0],Y0,a[1]],[b[0],Y0,b[1]],[b[0],Y1,b[1]],[a[0],Y0,a[1]],[b[0],Y1,b[1]],[a[0],Y1,a[1]]].forEach(v => { pos.push(...v); nor.push(...nn); });
  };
  const hquad = (pos, nor, pts, y) => { const P = pts.map(p => toCM(...p)); const Y=FT(y);
    for (let i=1;i<P.length-1;i++) [[P[0][0],Y,P[0][1]],[P[i][0],Y,P[i][1]],[P[i+1][0],Y,P[i+1][1]]].forEach(v => { pos.push(...v); nor.push(0,1,0); }); };
  const ext = doc.createNode('EXT_DETAILS'); scene.addChild(ext);
  const G = { pos: [], nor: [] }, F = { pos: [], nor: [] }, Wd = { pos: [], nor: [] }, S = { pos: [], nor: [] }, Pv = { pos: [], nor: [] };
  // offset a polyline outward (to the left of travel direction 'side') so glass sits on the facade face
  const ribbon = (pl, y0, y1, mullion = 5) => {
    let acc = 0, next = 0;
    for (let i = 0; i < pl.length - 1; i++) {
      const p1 = pl[i], p2 = pl[i+1]; quad(G.pos, G.nor, p1, p2, y0, y1);
      const L = Math.hypot(p2[0]-p1[0], p2[1]-p1[1]); if (!L) continue; const ux=(p2[0]-p1[0])/L, uy=(p2[1]-p1[1])/L;
      while (next <= acc + L) { const t = next - acc, x = p1[0]+ux*t, y = p1[1]+uy*t;
        quad(F.pos, F.nor, [x-ux*0.22, y-uy*0.22], [x+ux*0.22, y+uy*0.22], y0, y1); next += mullion; }
      acc += L;
      quad(F.pos, F.nor, p1, p2, y1-0.6, y1); quad(F.pos, F.nor, p1, p2, y0, y0+0.8);
    }
  };
  const OUT = 0.6; // feet proud of the drawn glazing line
  const offset = (pl, d) => pl.map((p, i) => { const a = pl[Math.max(0,i-1)], b = pl[Math.min(pl.length-1,i+1)];
    const dx=b[0]-a[0], dy=b[1]-a[1], L=Math.hypot(dx,dy)||1; return [p[0] - dy/L*d, p[1] + dx/L*d]; });
  // People's Library + Main Lobby curtain wall (A321 area B), drawn west->east->south, outward = left
  const GZ = JSON.parse(fs.readFileSync(process.env.GLAZING));
  const smooth = pl => pl.map((p, i) => i === 0 || i === pl.length-1 ? p : [0,1].map(k => (pl[i-1][k] + 2*p[k] + pl[i+1][k]) / 4));
  ribbon(smooth(GZ.lobby), 0, 19);
  // Auditorium stage window CW13 and the curved glazing at the East Wing's northwest corner (A320 area A), east->west->south
  ribbon(smooth(GZ.aud), 0, 16);
  // Permanent exhibit bay window (A303 9A/8B, A321): box projecting from the north wall between grids 5 and 6
  { const x0=87.2, x1=102, yw=GZ.bay_wall_y-0.3, yo=GZ.bay_wall_y+4.4, z0=2.7, z1=10.5;
    quad(G.pos, G.nor, [x1,yo],[x0,yo], z0+0.4, z1-0.4);                    // glass face
    quad(F.pos, F.nor, [x1,yo+0.05],[x0,yo+0.05], z0, z0+0.4); quad(F.pos, F.nor, [x1,yo+0.05],[x0,yo+0.05], z1-0.4, z1);
    quad(F.pos, F.nor, [x0,yw],[x0,yo], z0, z1); quad(F.pos, F.nor, [x1,yo],[x1,yw], z0, z1);
    hquad(F.pos, F.nor, [[x0,yw],[x1,yw],[x1,yo],[x0,yo]], z1); hquad(F.pos, F.nor, [[x0,yw],[x1,yw],[x1,yo],[x0,yo]], z0);
    for (let x = x0+3.7; x < x1-1; x += 3.7) quad(F.pos, F.nor, [x+0.2,yo+0.06],[x-0.2,yo+0.06], z0, z1); }
  // West Patio alcove (A275): open recess along the west wall, timber-clad back wall, vestibule doors at the north end
  const ALC = { poly: [[4,46],[30,46],[30,17],[22,8.5],[4,8.5]], top: 11 };
  { quad(Wd.pos, Wd.nor, [30,17],[30,46], 0, ALC.top);            // back wall (timber mats)
    quad(Wd.pos, Wd.nor, [22,8.5],[30,17], 0, ALC.top);            // south end, along the roof stair
    quad(Wd.pos, Wd.nor, [30,46],[21.5,46], 0, ALC.top);           // north end (vestibule wall)
    quad(G.pos, G.nor, [28.6,45.9],[23.4,45.9], 0.2, 8);           // vestibule doors (glass pair)
    quad(F.pos, F.nor, [26.1,45.8],[25.9,45.8], 0, 8.2); quad(F.pos, F.nor, [28.8,45.8],[23.2,45.8], 8, 8.6);
    hquad(S.pos, S.nor, [[21.5,46],[30,46],[30,17],[22,8.5],[21.5,8.5]], ALC.top);   // soffit
    hquad(Pv.pos, Pv.nor, [[21.5,46],[30,46],[30,17],[22,8.5],[21.5,8.5]], 0.3);      // paving
    for (let y = 19; y < 46; y += 4.5) quad(Wd.pos, Wd.nor, [29.9,y],[29.9,y+0.25], 1.5, 1.6); // bench line
  }
  add(ext, 'EXT_glazing', [G.pos, G.nor], glassMat);
  add(ext, 'EXT_frames', [F.pos, F.nor], frameMat);
  add(ext, 'EXT_alcove_walls', [Wd.pos, Wd.nor], woodMat);
  add(ext, 'EXT_alcove_soffit', [S.pos, S.nor], soffitMat);
  add(ext, 'EXT_alcove_paving', [Pv.pos, Pv.nor], paveMat);
  // carve the alcove opening out of the building shell: subdivide facade triangles touching the opening, drop pieces inside
  const inPoly = (x, y, P) => { let c=false; for (let i=0,j=P.length-1;i<P.length;j=i++){ const [xi,yi]=P[i],[xj,yj]=P[j]; if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi)) c=!c; } return c; };
  let removed = 0;
  for (const n of root.listNodes()) {
    const m = n.getMesh(); if (!m || m.getName() !== 'building-BUILDING') continue;
    const W = n.getWorldMatrix(); const inv = (() => { const M=W; // invert affine 4x4 (rotation+translation, no scale assumed generic)
      const a=[[M[0],M[4],M[8]],[M[1],M[5],M[9]],[M[2],M[6],M[10]]]; const d=a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);
      const c=(r,k)=>{const m2=[0,1,2].filter(i=>i!==r), n2=[0,1,2].filter(i=>i!==k); const v=a[m2[0]][n2[0]]*a[m2[1]][n2[1]]-a[m2[0]][n2[1]]*a[m2[1]][n2[0]]; return ((r+k)%2?-v:v)/d;};
      const R=[[c(0,0),c(1,0),c(2,0)],[c(0,1),c(1,1),c(2,1)],[c(0,2),c(1,2),c(2,2)]]; return { R, t:[M[12],M[13],M[14]] }; })();
    const toWorld = v => [W[0]*v[0]+W[4]*v[1]+W[8]*v[2]+W[12], W[1]*v[0]+W[5]*v[1]+W[9]*v[2]+W[13], W[2]*v[0]+W[6]*v[1]+W[10]*v[2]+W[14]];
    const toLocal = w => { const d=[w[0]-inv.t[0], w[1]-inv.t[1], w[2]-inv.t[2]]; return inv.R.map(r => r[0]*d[0]+r[1]*d[1]+r[2]*d[2]); };
    const prim = m.listPrimitives()[0]; const P = prim.getAttribute('POSITION'), I = prim.getIndices(); const N = prim.getAttribute('NORMAL');
    const tris = []; for (let t = 0; t < I.getCount()/3; t++) tris.push([0,1,2].map(k => I.getScalar(3*t+k)));
    const outPos = [], outNor = [];
    const inside = w => { const [fx, fy] = toFT(w[0], w[2]); const z = w[1]*33.3333333-38.3; return z < ALC.top && z > -3 && inPoly(fx, fy, ALC.poly); };
    const near = w => { const [fx, fy] = toFT(w[0], w[2]); return fx > -10 && fx < 45 && fy > -5 && fy < 60; };
    const emit = (vs, nn) => { if (inside(toWorld([(vs[0][0]+vs[1][0]+vs[2][0])/3,(vs[0][1]+vs[1][1]+vs[2][1])/3,(vs[0][2]+vs[1][2]+vs[2][2])/3]))) { removed++; return; } vs.forEach(v => { outPos.push(...v); outNor.push(...nn); }); };
    const sub = (vs, nn, depth) => { const w = vs.map(toWorld); if (depth === 0 || !w.some(near)) return emit(vs, nn); const ins = w.map(inside); if (ins.every(x=>x)) { removed++; return; }
      const e = (a,b)=>Math.hypot(...[0,1,2].map(k=>(w[a][k]-w[b][k]))); if (Math.max(e(0,1),e(1,2),e(2,0)) < 0.012) return emit(vs, nn);
      const m01=vs[0].map((v,k)=>(v+vs[1][k])/2), m12=vs[1].map((v,k)=>(v+vs[2][k])/2), m20=vs[2].map((v,k)=>(v+vs[0][k])/2);
      [[vs[0],m01,m20],[m01,vs[1],m12],[m20,m12,vs[2]],[m01,m12,m20]].forEach(t => sub(t, nn, depth-1)); };
    for (const t of tris) { const vs = t.map(i => P.getElement(i, [])); const nn = N ? N.getElement(t[0], []) : [0,1,0];
      // flat normal from geometry
      const u=[0,1,2].map(k=>vs[1][k]-vs[0][k]), v=[0,1,2].map(k=>vs[2][k]-vs[0][k]); const c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]; const l=Math.hypot(...c)||1;
      sub(vs, N ? nn : c.map(x=>x/l), 9); }
    const np = doc.createAccessor().setType('VEC3').setArray(new Float32Array(outPos)).setBuffer(buf);
    const nn = doc.createAccessor().setType('VEC3').setArray(new Float32Array(outNor)).setBuffer(buf);
    prim.setIndices(null); prim.setAttribute('POSITION', np); prim.setAttribute('NORMAL', nn);
    for (const sem of prim.listSemantics()) if (!['POSITION','NORMAL'].includes(sem)) prim.setAttribute(sem, null);
  }
  console.log('alcove: removed sub-triangles', removed);
}
await doc.transform(draco({ method: 'edgebreaker', quantizePosition: 16 }));
await io.write(outGlb, doc);
console.log('wrote', outGlb, fs.statSync(outGlb).size);
