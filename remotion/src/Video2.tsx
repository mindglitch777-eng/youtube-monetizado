import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing, continueRender, delayRender} from 'remotion';

// Video 2: Pijama en 8 épocas. Bebas Neue y Montserrat ExtraBold (Google Fonts, licencia OFL) servidas desde public/
export const BEBAS = 'BebasV2';
export const MONT = 'MontV2';
if (typeof document !== 'undefined') {
  const espera = delayRender('fuentes video 2');
  Promise.all([
    new FontFace(BEBAS, `url(${staticFile('bebas.woff2')}) format('woff2')`).load(),
    new FontFace(MONT, `url(${staticFile('montserrat800.woff2')}) format('woff2')`, {weight: '800'}).load(),
  ]).then((fs) => { fs.forEach((f) => (document as any).fonts.add(f)); continueRender(espera); }).catch(() => continueRender(espera));
}

export const FPS = 30;
export const contorno = (px: number) => ({
  WebkitTextStroke: `${px}px #000`,
  paintOrder: 'stroke fill' as const,
  textShadow: `0 ${px / 2}px ${px * 1.2}px rgba(0,0,0,.6)`,
});
const NOTA_COLOR: Record<string, string> = {S: '#ff4fd8', A: '#3ddc84', B: '#8bd346', C: '#ffd23f', D: '#ff9f1c', F: '#ff3b3b'};

type P = any;

// ---------------------------------------------------------------- cámara por tipo de plano del manifest
const camara = (cam: string, prog: number) => {
  let s = 1, x = 0, y = 0;
  switch (cam) {
    case 'WS': s = 1 + 0.05 * prog; break;
    case 'MS': s = 1.02 + 0.07 * prog; break;
    case 'CU': s = 1.03 + 0.04 * prog; break;
    case 'EC': s = 1.06 + 0.07 * prog; break;
    case 'LA': s = 1.08; y = interpolate(prog, [0, 1], [2, -2]); break;
    case 'HA': s = 1.1 - 0.08 * prog; break;
    case 'BE': s = 1.14 - 0.12 * prog; break;
    case 'FE': s = 1 + 0.1 * prog; break;
    case 'OS': s = 1.07; x = interpolate(prog, [0, 1], [-2, 2]); break;
    default: s = 1 + 0.06 * prog;
  }
  return {s, x, y};
};

export const Imagen: React.FC<{p: P; dur: number; dir?: string; vertical?: boolean}> = ({p, dur, dir = 'v2/img16', vertical = false}) => {
  const f = useCurrentFrame();
  const congelar = p.congelar ? Math.round((p.congelar - p.ini) * FPS) : 1e9;
  const fq = Math.min(f, congelar);
  const prog = dur > 1 ? fq / dur : 0;
  let {s, x, y} = camara(p.cam, prog);
  // entrada según la transición
  let tx = 0, ty = 0, blur = 0;
  if (p.tr === 'PUNCH') s *= interpolate(f, [0, 5], [1.25, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  if (p.tr === 'WHIP') { tx = interpolate(f, [0, 6], [35, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)}); blur = interpolate(f, [0, 6], [14, 0], {extrapolateRight: 'clamp'}); }
  if (p.tr === 'GAME') ty = interpolate(f, [0, 8], [100, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.2))});
  // golpes de zoom dentro de planos largos
  for (const g of p.golpes || []) {
    const gf = Math.round((g - p.ini) * FPS);
    s *= interpolate(f, [gf, gf + 3, gf + 10], [1, 1.07, 1.04], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  }
  // temblor: Hielo (frío) y Pompeya (tierra que tiembla)
  let sx = 0, sy = 0;
  if (!vertical && (p.epoca === 1 || p.epoca === 3) && f < congelar) {
    const a = p.epoca === 3 ? 0.45 : 0.18;
    sx = Math.sin(f * 1.7) * a + Math.sin(f * 0.63) * a;
    sy = Math.cos(f * 1.3) * a;
  }
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000', transform: `translate(${tx}%, ${ty}%)`, filter: blur ? `blur(${blur}px)` : undefined}}>
      <Img src={staticFile(`${dir}/${p.id}.jpg`)} style={{width: '100%', height: '100%', objectFit: 'cover',
        transform: `translate(${x + sx}%, ${y + sy}%) scale(${s})`}} />
    </AbsoluteFill>
  );
};

const Flash: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{backgroundColor: '#fff', opacity: interpolate(f, [0, 6], [1, 0], {extrapolateRight: 'clamp'})}} />;
};

// ---------------------------------------------------------------- pantallas propias
const TituloEpoca: React.FC<{texto: string}> = ({texto}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, 4, 8], [0.7, 1.08, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#07070b', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{fontFamily: BEBAS, fontSize: 210, color: '#fff', letterSpacing: 6, transform: `scale(${s})`, ...contorno(0)}}>{texto}</div>
    </AbsoluteFill>
  );
};

const Grano: React.FC<{op?: number}> = ({op = 0.18}) => {
  const f = useCurrentFrame();
  return (
    <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: op, mixBlendMode: 'overlay'}}>
      <filter id={`g${f % 6}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 6} /></filter>
      <rect width="100%" height="100%" filter={`url(#g${f % 6})`} />
    </svg>
  );
};

const Fin: React.FC<{p: P}> = ({p}) => {
  const f = useCurrentFrame();
  const a = interpolate(f, [0, 5], [0, 1], {extrapolateRight: 'clamp'});
  const nota = interpolate(f, [10, 15, 19], [2.2, 0.9, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #241b2f, #07070b 70%)', justifyContent: 'center', alignItems: 'center', opacity: a}}>
      <Grano op={0.12} />
      <div style={{fontFamily: BEBAS, fontSize: 230, color: '#fff', lineHeight: 0.9, letterSpacing: 10}}>FIN</div>
      <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 56, color: '#ffd23f', marginTop: 10}}>CULPABLE: {p.culpable}</div>
      <div style={{display: 'flex', gap: 40, alignItems: 'center', marginTop: 30}}>
        <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 44, color: '#cfd3dc'}}>TU VIDA: {p.tiempo}</div>
        <div style={{width: 150, height: 150, borderRadius: 24, background: NOTA_COLOR[p.nota], display: 'flex', alignItems: 'center', justifyContent: 'center',
          transform: `scale(${nota})`, border: '6px solid #000', boxShadow: '0 10px 30px rgba(0,0,0,.6)'}}>
          <span style={{fontFamily: BEBAS, fontSize: 140, color: '#000', lineHeight: 1}}>{p.nota}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const FILAS = ['S', 'A', 'B', 'C', 'D', 'F'];
export const TablaSF: React.FC<{filas: P[]; llenar: number; parcial?: boolean}> = ({filas, llenar, parcial}) => {
  const f = useCurrentFrame();
  const paso = (llenar * FPS) / Math.max(1, filas.length);
  return (
    <AbsoluteFill style={{background: parcial ? 'rgba(7,7,11,.78)' : 'linear-gradient(#141428, #07070b)', padding: '150px 140px 60px', gap: 14}}>
      {!parcial && <Grano op={0.08} />}
      {FILAS.map((n) => (
        <div key={n} style={{display: 'flex', alignItems: 'center', gap: 18, height: 118}}>
          <div style={{width: 118, height: 118, background: NOTA_COLOR[n], borderRadius: 14, border: '5px solid #000', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <span style={{fontFamily: BEBAS, fontSize: 100, color: '#000'}}>{n}</span>
          </div>
          <div style={{flex: 1, height: 118, background: 'rgba(255,255,255,.07)', borderRadius: 14, display: 'flex', alignItems: 'center', gap: 16, padding: '0 16px'}}>
            {filas.map((r, i) => {
              if (r.nota !== n) return null;
              const fi = 8 + i * paso;
              const sc = interpolate(f, [fi, fi + 4, fi + 8], [0, 1.15, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
              return (
                <div key={i} style={{transform: `scale(${sc})`, background: '#fff', borderRadius: 12, border: '4px solid #000', padding: '6px 18px', textAlign: 'center'}}>
                  <div style={{fontFamily: BEBAS, fontSize: 56, color: '#000', lineHeight: 1}}>{r.epoca}</div>
                  {r.tiempo ? <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 22, color: '#444'}}>{r.tiempo}</div> : null}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- textos y carteles
export const Texto: React.FC<{texto: string; abajo?: number; size?: number}> = ({texto, abajo = 70, size = 104}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, 2, 4], [0.6, 1.12, 1], {extrapolateRight: 'clamp'});
  const partes = texto.length > 26 && texto.includes(' · ') ? texto.split(' · ') : [texto];
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: abajo}}>
      <div style={{transform: `scale(${s})`, textAlign: 'center'}}>
        {partes.map((x, i) => (
          <div key={i} style={{fontFamily: BEBAS, fontSize: size, lineHeight: 0.98, color: '#fff', letterSpacing: 2, ...contorno(10)}}>{x}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Jefe: React.FC<{texto: string}> = ({texto}) => {
  const f = useCurrentFrame();
  const y = interpolate(f, [0, 7], [-140, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.4))});
  return (
    <AbsoluteFill style={{alignItems: 'center', paddingTop: 120}}>
      <div style={{transform: `translateY(${y}px)`, background: '#b3121b', border: '6px solid #000', borderRadius: 14, padding: '6px 34px', boxShadow: '0 8px 0 #000'}}>
        <span style={{fontFamily: BEBAS, fontSize: 84, color: '#fff', letterSpacing: 3}}>{texto}</span>
      </div>
    </AbsoluteFill>
  );
};

const Logro: React.FC<{texto: string; aura?: number}> = ({texto, aura}) => {
  const f = useCurrentFrame();
  const y = interpolate(f, [0, 8], [260, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 60}}>
      <div style={{transform: `translateY(${y}px)`, display: 'flex', alignItems: 'center', gap: 22, background: 'linear-gradient(#2b2b38, #15151d)', border: '5px solid #ffd23f',
        borderRadius: 60, padding: '14px 40px 14px 18px', boxShadow: '0 10px 30px rgba(0,0,0,.6)'}}>
        <div style={{width: 96, height: 96, borderRadius: 48, background: '#ffd23f', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 58}}>🏆</div>
        <div>
          <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 28, color: '#ffd23f', letterSpacing: 2}}>LOGRO DESBLOQUEADO</div>
          <div style={{fontFamily: BEBAS, fontSize: 66, color: '#fff', lineHeight: 1}}>{texto}</div>
        </div>
        {aura ? <div style={{fontFamily: BEBAS, fontSize: 70, color: aura > 0 ? '#3ddc84' : '#ff3b3b', marginLeft: 16}}>AURA {aura > 0 ? '+' : '−'}{Math.abs(aura)}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

const Banda: React.FC<{texto: string; derecha: boolean}> = ({texto, derecha}) => (
  <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: derecha ? 'flex-end' : 'flex-start', padding: derecha ? '0 50px 40px 0' : '0 0 40px 50px'}}>
    <div style={{background: 'rgba(0,0,0,.72)', borderRadius: 10, padding: '8px 20px', fontFamily: MONT, fontWeight: 800, fontSize: 30, color: '#fff', letterSpacing: 1}}>{texto}</div>
  </AbsoluteFill>
);

// ---------------------------------------------------------------- HUD
const Corazon: React.FC<{lleno: boolean}> = ({lleno}) => (
  <svg width="40" height="36" viewBox="0 0 32 29"><path d="M16 28 2 14C-3 8 2-1 9 1c3 1 5 3 7 6 2-3 4-5 7-6 7-2 12 7 7 13Z" fill={lleno ? '#ff3b4e' : 'rgba(255,255,255,.18)'} stroke="#000" strokeWidth="2.5" /></svg>
);
const Hud: React.FC<{h: P; t: number}> = ({h, t}) => {
  const corriendo = !h.vida;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', top: 24, left: 34, right: 34, height: 78, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: 'rgba(8,8,14,.62)', borderRadius: 18, padding: '0 26px', border: '3px solid rgba(255,255,255,.18)'}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 14}}>
          <span style={{fontFamily: MONT, fontWeight: 800, fontSize: 24, color: '#aab'}}>TU VIDA</span>
          <span style={{fontFamily: BEBAS, fontSize: 52, color: corriendo ? '#fff' : '#ffd23f', minWidth: 230}}>
            {corriendo ? `⏱ ${['·', '··', '···'][Math.floor(t * 2) % 3]}` : h.vida}
          </span>
        </div>
        <span style={{fontFamily: BEBAS, fontSize: 56, color: '#fff', letterSpacing: 3}}>ÉPOCA {h.epoca}/8</span>
        <div style={{display: 'flex', alignItems: 'center', gap: 4}}>
          {Array.from({length: 8}).map((_, i) => <Corazon key={i} lleno={i < h.vidas} />)}
          <span style={{fontFamily: BEBAS, fontSize: 48, color: h.aura < 0 ? '#ff3b3b' : h.aura > 0 ? '#3ddc84' : '#fff', marginLeft: 22}}>
            AURA {h.aura > 0 ? '+' : h.aura < 0 ? '−' : ''}{Math.abs(h.aura)}
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- color por época
export const tinte = (estilo: string, t: number, c: P): {filtro: string; capa?: string; op?: number; mezcla?: string} => {
  switch (estilo) {
    case 'hielo': return {filtro: 'saturate(0.9) brightness(1.03)', capa: '#7fc8ff', op: 0.12, mezcla: 'soft-light'};
    case 'egipto': return {filtro: 'saturate(1.08)', capa: '#ffb52e', op: 0.12, mezcla: 'soft-light'};
    case 'pompeya': return {filtro: 'saturate(0.9) contrast(1.05)', capa: '#ff6a2b', op: 0.12, mezcla: 'soft-light'};
    case 'roma': return {filtro: 'saturate(1.1)', capa: '#d9452f', op: 0.1, mezcla: 'soft-light'};
    case '1348': return {filtro: 'saturate(0.6) brightness(0.95)', capa: '#6b8f5a', op: 0.18, mezcla: 'soft-light'};
    case 'tenochtitlan': return {filtro: 'saturate(1.15)', capa: '#2fd1c5', op: 0.06, mezcla: 'soft-light'};
    case 'drenaje': {
      const g = c.fin_rampa ? interpolate(t, [c.ini, c.fin_rampa], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
      return {filtro: `grayscale(${g}) saturate(${1.15 - 0.15 * g})`};
    }
    case '1816': return {filtro: 'saturate(0.7) brightness(0.97)', capa: '#6f88a8', op: 0.15, mezcla: 'soft-light'};
    case 'mudo': return {filtro: 'grayscale(1) sepia(0.35) contrast(1.15)'};
    case 'londres': return {filtro: 'sepia(0.55) saturate(0.85)'};
    case 'casa': return {filtro: 'saturate(1.05)', capa: '#ffb36b', op: 0.08, mezcla: 'soft-light'};
    default: return {filtro: 'none'};
  }
};

// ---------------------------------------------------------------- composición
export const Largo2: React.FC<{tl: P; audio: string}> = ({tl, audio}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const c = [...tl.color].reverse().find((x: P) => t >= x.ini) || {estilo: 'none'};
  const tin = tinte(c.estilo, t, c);
  const actual = tl.planos.find((p: P) => t >= p.ini && t < p.fin) || {};
  const h = [...tl.hud].reverse().find((x: P) => t >= x.ini);
  const tablaFinal = tl.planos.find((p: P) => p.tipo === 'tabla');
  const conHud = h && h.epoca > 0 && actual.tipo === 'img' && (!tablaFinal || t < tablaFinal.ini);
  const mudo = c.estilo === 'mudo';
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{filter: tin.filtro}}>
        {tl.planos.map((p: P, k: number) => {
          const from = Math.round(p.ini * FPS);
          const dur = Math.max(1, Math.round(p.fin * FPS) - from);
          const prev = tl.planos[k - 1];
          let cuerpo: React.ReactNode = null;
          if (p.tipo === 'img') cuerpo = <Imagen p={p} dur={dur} />;
          else if (p.tipo === 'negro') cuerpo = <AbsoluteFill style={{backgroundColor: '#000'}} />;
          else if (p.tipo === 'titulo_epoca') cuerpo = <TituloEpoca texto={p.texto} />;
          else if (p.tipo === 'fin') cuerpo = <Fin p={p} />;
          else if (p.tipo === 'tabla') cuerpo = <TablaSF filas={p.filas} llenar={p.llenar} />;
          const flash = p.tipo === 'img' && (p.tr === 'FLASH' || (prev && prev.tipo === 'titulo_epoca'));
          return (
            <Sequence key={k} from={from} durationInFrames={dur}>
              {cuerpo}
              {flash ? <Flash /> : null}
            </Sequence>
          );
        })}
        {tin.capa ? <AbsoluteFill style={{backgroundColor: tin.capa, opacity: tin.op, mixBlendMode: (tin.mezcla as any) || 'normal'}} /> : null}
      </AbsoluteFill>
      {mudo ? (
        <AbsoluteFill>
          <Grano op={0.3} />
          <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 240, background: '#000'}} />
          <div style={{position: 'absolute', right: 0, top: 0, bottom: 0, width: 240, background: '#000'}} />
          <AbsoluteFill style={{backgroundColor: '#fff', opacity: 0.04 + 0.04 * Math.sin(f * 2.1)}} />
        </AbsoluteFill>
      ) : null}
      {conHud ? <Hud h={h} t={t} /> : null}
      {tl.textos.map((x: P, k: number) => (
        <Sequence key={`t${k}`} from={Math.round(x.ini * FPS)} durationInFrames={Math.max(1, Math.round((x.fin - x.ini) * FPS))}>
          <Texto texto={x.texto} />
        </Sequence>
      ))}
      {tl.carteles.map((x: P, k: number) => (
        <Sequence key={`c${k}`} from={Math.round(x.ini * FPS)} durationInFrames={Math.max(1, Math.round((x.fin - x.ini) * FPS))}>
          {x.tipo === 'jefe' ? <Jefe texto={x.texto} /> : x.tipo === 'logro' ? <Logro texto={x.texto} aura={x.aura} /> :
            <Banda texto={x.texto} derecha={x.tipo === 'fuentes'} />}
        </Sequence>
      ))}
      <Audio src={staticFile(audio)} />
    </AbsoluteFill>
  );
};
