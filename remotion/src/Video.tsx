import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing, continueRender, delayRender} from 'remotion';

// Anton (Google Fonts, licencia OFL) servida desde public/ porque el navegador del render no tiene salida directa a Google
export const fontFamily = 'Anton';
if (typeof document !== 'undefined') {
  const espera = delayRender('fuente Anton');
  const fuente = new FontFace('Anton', `url(${staticFile('anton.woff2')}) format('woff2')`);
  fuente.load().then((ff) => { (document as any).fonts.add(ff); continueRender(espera); }).catch(() => continueRender(espera));
}
const FPS = 30;
export const AMARILLO = '#FFE600';

type Plano = any;
type TL = {duracion: number; planos: Plano[]; subs: {w: string; ini: number; fin: number}[]; hud: {ini: number; fin: number; abiertos: number}[]};

export const trazo = (px: number) => ({
  WebkitTextStroke: `${px}px #000`,
  paintOrder: 'stroke fill' as const,
  textShadow: `0 ${px / 2}px ${px}px rgba(0,0,0,.55)`,
});

// ---------------------------------------------------------------- imágenes
const Imagen: React.FC<{p: Plano; dur: number; formato: string}> = ({p, dur, formato}) => {
  const f = useCurrentFrame();
  const dir = formato === 'largo' ? 'img16' : 'img916';
  const vida = interpolate(f, [0, 6], [1.03, 1], {extrapolateRight: 'clamp'});
  const prog = dur > 1 ? f / dur : 0;
  let escala = 1;
  let tx = 0;
  if (p.cam === 'zoom') escala = 1 + 0.08 * prog;
  else if (p.cam === 'microzoom') escala = 1 + 0.05 * prog;
  else if (p.cam === 'zoomout') escala = 1.1 - 0.1 * prog;
  else if (p.cam === 'paneo') {
    escala = 1.06;
    tx = interpolate(prog, [0, 1], [-2, 2]);
  }
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000'}}>
      <Img src={staticFile(`${dir}/${p.id}.png`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `translateX(${tx}%) scale(${escala * vida})`}} />
    </AbsoluteFill>
  );
};

const Overlay: React.FC<{texto: string; formato: string}> = ({texto, formato}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, 2, 4], [0.6, 1.12, 1], {extrapolateRight: 'clamp'});
  const largo = formato === 'largo';
  return (
    <AbsoluteFill style={{justifyContent: largo ? 'flex-start' : 'flex-start', alignItems: 'center', paddingTop: largo ? '50%' : '16%'}}>
      <div style={{fontFamily, fontSize: largo ? 120 : 110, color: '#fff', textAlign: 'center', lineHeight: 1.05, padding: '0 40px', transform: `scale(${s})`, ...trazo(largo ? 12 : 12)}}>
        {texto}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- tarjeta de número (piedra)
const Piedra: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, #8d8a84 0%, #6b6862 45%, #3d3b37 100%)'}}>
    <svg width="100%" height="100%" style={{position: 'absolute', opacity: 0.35}}>
      <filter id="ruido"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="5" seed="4" /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter="url(#ruido)" />
    </svg>
    <svg width="100%" height="100%" style={{position: 'absolute', opacity: 0.25}}>
      <filter id="ruido2"><feTurbulence type="turbulence" baseFrequency="0.06" numOctaves="2" seed="9" /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter="url(#ruido2)" />
    </svg>
    {children}
  </AbsoluteFill>
);

const Numero: React.FC<{p: Plano; dur: number; formato: string}> = ({p, dur, formato}) => {
  const f = useCurrentFrame();
  const negro = interpolate(f, [0, 12], [1, 0], {extrapolateRight: 'clamp'});
  const zoom = interpolate(f, [12, 12 + 48], [1, 1.12], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const golpe = interpolate(f, [12, 15, 20], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const largo = formato === 'largo';
  return (
    <AbsoluteFill>
      <Piedra>
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', transform: `scale(${zoom}) translateY(${golpe * 8}px)`}}>
          <div style={{fontFamily, fontSize: largo ? 560 : 640, lineHeight: 1, color: '#55524c',
            textShadow: '-6px -6px 0 rgba(0,0,0,.55), 5px 5px 0 rgba(255,255,255,.22), 0 22px 40px rgba(0,0,0,.6)'}}>
            {p.num}
          </div>
          <div style={{fontFamily, fontSize: largo ? 92 : 96, color: '#fff', marginTop: largo ? -20 : 10, letterSpacing: 4, ...trazo(10)}}>{p.nombre}</div>
        </AbsoluteFill>
      </Piedra>
      <AbsoluteFill style={{backgroundColor: '#000', opacity: negro}} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- candados y reloj
export const ICONOS = ['gota', 'ojo', 'fruto', 'luna', 'lanza', 'espina', 'fantasma'];
const Icono: React.FC<{tipo: string}> = ({tipo}) => {
  switch (tipo) {
    case 'gota': return <path d="M0,-26 C10,-10 16,0 16,9 A16,16 0 0 1 -16,9 C-16,0 -10,-10 0,-26Z" fill="#3fa2f0" stroke="#000" strokeWidth={3} />;
    case 'ojo': return <g><path d="M-22,0 Q0,-18 22,0 Q0,18 -22,0Z" fill="#f2b33d" stroke="#000" strokeWidth={3} /><ellipse cx={0} cy={0} rx={4} ry={9} fill="#000" /></g>;
    case 'fruto': return <g><circle cx={-6} cy={4} r={11} fill="#d6262c" stroke="#000" strokeWidth={3} /><circle cx={9} cy={2} r={10} fill="#e23a3f" stroke="#000" strokeWidth={3} /><path d="M0,-8 L4,-22" stroke="#2f7a32" strokeWidth={4} /></g>;
    case 'luna': return <g><path d="M8,-20 A20,20 0 1 0 8,20 A14,14 0 1 1 8,-20Z" fill="#f4e7a1" stroke="#000" strokeWidth={3} /><text x={8} y={8} fontSize={20} fill="#bfe6ff" stroke="#000" strokeWidth={1}>✱</text></g>;
    case 'lanza': return <g><path d="M-20,20 L14,-14" stroke="#8a5a2b" strokeWidth={5} /><path d="M14,-14 L24,-24 L10,-22 Z" fill="#9aa0a6" stroke="#000" strokeWidth={3} /></g>;
    case 'espina': return <g><path d="M-22,10 Q0,0 22,10" stroke="#5b3a1e" strokeWidth={6} fill="none" /><path d="M-2,5 L6,-22 L10,6Z" fill="#c0392b" stroke="#000" strokeWidth={3} /></g>;
    default: return <path d="M-16,-6 h32 v26 h-32Z" fill="none" stroke="#fff" strokeOpacity={0.35} strokeDasharray="5 5" strokeWidth={3} />;
  }
};

export const Candado: React.FC<{i: number; abierto: number; x: number; y: number; s: number}> = ({i, abierto, x, y, s}) => {
  const fantasma = i === 6 && abierto < 0.5;
  const sube = -26 * abierto;
  return (
    <g transform={`translate(${x},${y}) scale(${s})`} opacity={fantasma ? 0.45 : 1}>
      <path d={`M-22,-10 V-32 A22,22 0 0 1 22,-32 V${-10 + 0}`} transform={`translate(0,${sube}) rotate(${abierto * -18},22,-10)`}
        fill="none" stroke={fantasma ? '#fff' : '#b9bec4'} strokeWidth={9} strokeDasharray={fantasma ? '6 6' : undefined} />
      <rect x={-38} y={-12} width={76} height={70} rx={10} fill={fantasma ? 'none' : '#cfa64a'} stroke={fantasma ? '#fff' : '#000'} strokeWidth={5}
        strokeDasharray={fantasma ? '7 7' : undefined} />
      <g transform="translate(0,24)">{!fantasma || abierto > 0.5 ? <Icono tipo={ICONOS[i]} /> : null}</g>
    </g>
  );
};

const Reloj: React.FC<{hora: string; f: number; size: number}> = ({hora, f, size}) => {
  const [h, m] = hora.split(':').map(Number);
  const objetivo = ((h % 12) + m / 60) * 30;
  const ang = interpolate(f, [0, 24], [objetivo - 90, objetivo], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <svg width={size} height={size} viewBox="-110 -110 220 220">
      <circle r={100} fill="#fbf3dc" stroke="#000" strokeWidth={8} />
      {Array.from({length: 12}).map((_, k) => (
        <line key={k} x1={0} y1={-86} x2={0} y2={k % 3 === 0 ? -70 : -78} stroke="#000" strokeWidth={k % 3 === 0 ? 7 : 4} transform={`rotate(${k * 30})`} />
      ))}
      <line x1={0} y1={12} x2={0} y2={-72} stroke="#d62020" strokeWidth={9} strokeLinecap="round" transform={`rotate(${ang})`} />
      <circle r={9} fill="#000" />
      <text y={52} textAnchor="middle" fontFamily={fontFamily} fontSize={28} fill="#000">{hora}</text>
    </svg>
  );
};

const Candados: React.FC<{p: Plano; dur: number; formato: string}> = ({p, dur, formato}) => {
  const f = useCurrentFrame();
  const W = formato === 'largo' ? 1920 : 1080;
  const H = formato === 'largo' ? 1080 : 1920;
  const esc = formato === 'largo' ? 1.5 : 1.15;
  const sep = (W - 160) / 7;
  return (
    <AbsoluteFill>
      {p.fondo ? (
        <AbsoluteFill style={{filter: 'brightness(0.45)'}}>
          <Img src={staticFile(`${formato === 'largo' ? 'img16' : 'img916'}/${p.fondo}.png`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </AbsoluteFill>
      ) : <AbsoluteFill style={{backgroundColor: '#05070d'}} />}
      <svg width={W} height={H} style={{position: 'absolute'}}>
        {ICONOS.map((_, i) => {
          let ab = i < p.abre - 1 ? 1 : 0;
          if (p.abre === 7) ab = interpolate(f, [12 + i * 4, 18 + i * 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          else if (i === p.abre - 1) ab = interpolate(f, [21, 27], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return <Candado key={i} i={i} abierto={ab} x={80 + sep * (i + 0.5)} y={H * 0.5} s={esc} />;
        })}
      </svg>
      {p.hora ? (
        <div style={{position: 'absolute', right: formato === 'largo' ? 60 : 40, top: formato === 'largo' ? 50 : 220}}>
          <Reloj hora={p.hora} f={f} size={formato === 'largo' ? 230 : 260} />
        </div>
      ) : null}
      <div style={{position: 'absolute', width: '100%', top: H * 0.5 + 150 * esc / 1.5, textAlign: 'center', fontFamily, fontSize: formato === 'largo' ? 64 : 70, color: '#fff', ...trazo(8)}}>
        {p.abre === 7 ? '7 DE 7' : `${p.abre} DE 7`}
      </div>
    </AbsoluteFill>
  );
};

const Hud: React.FC<{abiertos: number}> = ({abiertos}) => (
  <svg width={520} height={90} style={{position: 'absolute', left: 24, top: 18}}>
    {ICONOS.map((_, i) => <Candado key={i} i={i} abierto={i < abiertos ? 1 : 0} x={36 + i * 68} y={46} s={0.55} />)}
  </svg>
);

// ---------------------------------------------------------------- tarjetas de datos
export const Personita: React.FC<{color: string}> = ({color}) => (
  <svg width={90} height={150} viewBox="0 0 90 150">
    <circle cx={45} cy={30} r={24} fill={color} stroke="#000" strokeWidth={5} />
    <path d="M12,145 V80 Q12,58 45,58 Q78,58 78,80 V145Z" fill={color} stroke="#000" strokeWidth={5} />
  </svg>
);

const Dato: React.FC<{p: Plano; dur: number; formato: string}> = ({p, formato}) => {
  const f = useCurrentFrame();
  const cfg = p.tipo === 'dato12' ? {n: 12, m: 1, color: '#8a8a8a', texto: 'MENOS DE 1 DE CADA 12', prev: ''} :
    p.tipo === 'dato8' ? {n: 8, m: 1, color: '#8a8a8a', texto: '1 DE CADA 8', prev: '1 DE CADA 12'} :
      {n: 10, m: 7, color: '#59c13b', texto: '7 DE 10', prev: ''};
  const largo = formato === 'largo';
  const esc = largo ? 1 : 1.1;
  return (
    <AbsoluteFill style={{background: 'linear-gradient(#1c2740,#0f1626)', justifyContent: 'center', alignItems: 'center', gap: 40}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', width: largo ? 1500 : 900, gap: 18, transform: `scale(${esc})`}}>
        {Array.from({length: cfg.n}).map((_, k) => {
          const pinta = k < cfg.m ? interpolate(f, [15 + k * 6, 21 + k * 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
          const entra = interpolate(f, [k * 2, k * 2 + 6], [0, 1], {extrapolateRight: 'clamp'});
          return <div key={k} style={{opacity: entra, transform: `translateY(${(1 - entra) * 20}px)`}}>
            <Personita color={pinta > 0.5 ? cfg.color : '#f3d9b1'} />
          </div>;
        })}
      </div>
      <div style={{display: 'flex', gap: 50, alignItems: 'baseline'}}>
        <div style={{fontFamily, fontSize: largo ? 110 : 96, color: AMARILLO, ...trazo(10)}}>{cfg.texto}</div>
        {cfg.prev ? <div style={{fontFamily, fontSize: largo ? 60 : 52, color: '#bbb', ...trazo(6)}}>vs {cfg.prev}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

const Ranking: React.FC<{p: Plano; dur: number; formato: string}> = ({p, formato}) => {
  const f = useCurrentFrame();
  const largo = formato === 'largo';
  const filas = [
    {t: 'ENFERMEDAD Y GÉRMENES', v: '7 DE CADA 10 (~70 %)', pct: 70, c: '#59c13b'},
    {t: 'VIOLENCIA (otras personas)', v: '1 DE CADA 8 (12,5 %)', pct: 12.5, c: '#e04a3b'},
    {t: 'ACCIDENTES, LEÓN INCLUIDO', v: 'MENOS DE 1 DE CADA 12 (8,1 %)', pct: 8.1, c: '#f2b33d'},
  ];
  const ancho = largo ? 1000 : 700;
  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117', padding: largo ? '70px 160px 260px' : '260px 70px 520px', gap: largo ? 40 : 60, justifyContent: 'center'}}>
      <div style={{fontFamily, fontSize: largo ? 90 : 96, color: '#fff', ...trazo(6)}}>EL RANKING DE VERDAD</div>
      <div style={{fontFamily: 'sans-serif', fontSize: largo ? 26 : 30, color: '#9aa4b2', marginTop: largo ? -30 : -50}}>
        Gurven y Kaplan, 2007. Grupos de cazadores-recolectores recientes; no son datos de hace 20.000 años.
      </div>
      {filas.map((r, k) => {
        const t0 = (p.barras?.[k] ?? k * 2) * FPS;
        const g = interpolate(f, [t0, t0 + 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        return (
          <div key={k} style={{opacity: interpolate(f, [t0 - 4, t0 + 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
            <div style={{fontFamily, fontSize: largo ? 48 : 50, color: '#fff'}}>{r.t}</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 24, flexWrap: largo ? 'nowrap' : 'wrap'}}>
              <div style={{height: largo ? 64 : 70, width: Math.max(14, ancho * (r.pct / 70) * g), backgroundColor: r.c, borderRadius: 8}} />
              <div style={{fontFamily, fontSize: largo ? 46 : 48, color: r.c}}>{r.v}</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const RelojRoto: React.FC<{p: Plano; dur: number; formato: string}> = ({formato}) => {
  const f = useCurrentFrame();
  const roto = f > 18;
  const sac = roto ? Math.sin(f * 2.3) * interpolate(f, [18, 30], [14, 0], {extrapolateRight: 'clamp'}) : 0;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(#3a2a1a,#120c07)', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{transform: `translateX(${sac}px)`, position: 'relative'}}>
        <Reloj hora="9:00" f={f} size={formato === 'largo' ? 600 : 760} />
        {roto ? (
          <svg viewBox="-110 -110 220 220" width={formato === 'largo' ? 600 : 760} height={formato === 'largo' ? 600 : 760} style={{position: 'absolute', left: 0, top: 0}}>
            <path d="M-10,-95 L5,-40 L-20,-5 L15,30 L-5,95 M5,-40 L50,-60 M-20,-5 L-75,10 M15,30 L70,55" stroke="#000" strokeWidth={4} fill="none" />
          </svg>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

const Collage: React.FC<{p: Plano; dur: number; formato: string}> = ({p}) => {
  const f = useCurrentFrame();
  const items = p.items as {id: string; x: number; y: number}[];
  const cols = 3;
  const tw = 1920 / cols;
  const th = 1080 / 2;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {items.map((it, k) => {
        const x0 = (k % cols) * tw;
        const y0 = Math.floor(k / cols) * th;
        const r = interpolate(f, [8 + k * 6, 20 + k * 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const s = tw / 1920;
        return (
          <div key={k} style={{position: 'absolute', left: x0, top: y0, width: tw, height: th, overflow: 'hidden', border: '4px solid #000'}}>
            <Img src={staticFile(`img16/${it.id}.png`)} style={{width: '100%', height: '100%'}} />
            <svg width={tw} height={th} style={{position: 'absolute', left: 0, top: 0}}>
              <circle cx={it.x * s} cy={it.y * s} r={46} fill="none" stroke="#ff1f1f" strokeWidth={7} strokeDasharray={2 * Math.PI * 46} strokeDashoffset={2 * Math.PI * 46 * (1 - r)} />
            </svg>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const Final: React.FC<{p: Plano; dur: number; formato: string}> = ({formato}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#000', justifyContent: 'center', alignItems: 'center', opacity: o}}>
      <div style={{fontFamily, fontSize: formato === 'largo' ? 150 : 140, color: '#fff'}}>SUSCRÍBETE</div>
    </AbsoluteFill>
  );
};

const Cta: React.FC<{p: Plano; dur: number; formato: string}> = () => {
  const f = useCurrentFrame();
  const y = Math.sin(f / 4) * 18;
  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117', justifyContent: 'center', alignItems: 'center', gap: 40, padding: 60}}>
      <div style={{fontFamily, fontSize: 110, color: '#fff', textAlign: 'center', lineHeight: 1.1, ...trazo(8)}}>EL VIDEO COMPLETO ESTÁ EN MI CANAL</div>
      <svg width={220} height={260} style={{transform: `translateY(${y}px)`}} viewBox="0 0 220 260">
        <path d="M80,0 h60 v150 h60 l-90,100 l-90,-100 h60z" fill={AMARILLO} stroke="#000" strokeWidth={10} />
      </svg>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- subtítulos palabra por palabra
type Linea = {palabras: {w: string; ini: number; fin: number}[]; ini: number; fin: number};
export const agrupar = (subs: TL['subs']): Linea[] => {
  const out: Linea[] = [];
  let cur: Linea | null = null;
  subs.forEach((w, k) => {
    const prev = subs[k - 1];
    const corte = !cur || cur.palabras.length >= 4 || (prev && /[.?!…:]$/.test(prev.w)) || (prev && w.ini - prev.fin > 0.35) || (cur.palabras.length >= 3 && prev && /,$/.test(prev.w));
    if (corte) {
      if (cur) out.push(cur);
      cur = {palabras: [], ini: w.ini, fin: w.fin};
    }
    cur!.palabras.push(w);
    cur!.fin = w.fin;
  });
  if (cur) out.push(cur);
  return out;
};

const Subtitulos: React.FC<{tl: TL; formato: string}> = ({tl, formato}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const lineas = React.useMemo(() => agrupar(tl.subs), [tl]);
  const l = lineas.find((x, k) => t >= x.ini - 0.05 && t < (lineas[k + 1] ? Math.min(lineas[k + 1].ini - 0.05, x.fin + 0.4) : x.fin + 0.4));
  if (!l) return null;
  const largo = formato === 'largo';
  return (
    <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', paddingTop: largo ? 830 : 1240}}>
      <div style={{display: 'flex', columnGap: largo ? 40 : 34, rowGap: 6, flexWrap: 'wrap', justifyContent: 'center', maxWidth: largo ? 1700 : 960, padding: '0 20px'}}>
        {l.palabras.map((w, k) => {
          const activa = t >= w.ini - 0.03 && t < w.fin + 0.03;
          return (
            <span key={k} style={{fontFamily, fontSize: largo ? 76 : 92, color: activa ? '#fff' : AMARILLO, transform: `scale(${activa ? 1.12 : 1})`,
              display: 'inline-block', textTransform: 'uppercase', letterSpacing: 1, ...trazo(7)}}>{w.w}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- composición
const COMP: Record<string, React.FC<{p: Plano; dur: number; formato: string}>> = {
  img: Imagen, numero: Numero, candados: Candados, dato12: Dato, dato8: Dato, dato10: Dato, ranking: Ranking,
  reloj_roto: RelojRoto, collage: Collage, final: Final, cta: Cta,
  negro: () => <AbsoluteFill style={{backgroundColor: '#000'}} />,
};

export const Video: React.FC<{tl: TL; formato: string; audio: string}> = ({tl, formato, audio}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const hud = tl.hud.find((h) => t >= h.ini && t < h.fin);
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {tl.planos.map((p, k) => {
        const from = Math.round(p.ini * FPS);
        const dur = Math.max(1, Math.round(p.fin * FPS) - from);
        const C = COMP[p.tipo];
        return (
          <Sequence key={k} from={from} durationInFrames={dur}>
            <C p={p} dur={dur} formato={formato} />
            {p.overlay ? <Sequence from={3}><Overlay texto={p.overlay} formato={formato} /></Sequence> : null}
            {p.parpadeo ? <Parpadeo formato={formato} /> : null}
          </Sequence>
        );
      })}
      {hud ? <Hud abiertos={hud.abiertos} /> : null}
      <Subtitulos tl={tl} formato={formato} />
      <Audio src={staticFile(audio)} />
    </AbsoluteFill>
  );
};

const Parpadeo: React.FC<{formato: string}> = ({formato}) => {
  const f = useCurrentFrame();
  const on = Math.floor(f / 6) % 2 === 0;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div style={{fontFamily, fontSize: formato === 'largo' ? 200 : 220, color: '#ff2b2b', opacity: on ? 1 : 0.15, ...trazo(10)}}>24:00</div>
    </AbsoluteFill>
  );
};
