import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing} from 'remotion';
import {fontFamily, AMARILLO, trazo, ICONOS, Candado, Personita, agrupar} from './Video';

const FPS = 30;
const W = 1080;
const H = 1920;
type Plano = any;

// ---------------------------------------------------------------- imagen vertical
const Imagen: React.FC<{p: Plano; dur: number}> = ({p, dur}) => {
  const f = useCurrentFrame();
  const vida = interpolate(f, [0, 6], [1.03, 1], {extrapolateRight: 'clamp'});
  const prog = dur > 1 ? f / dur : 0;
  let escala = 1;
  let tx = 0;
  if (p.cam === 'zoom') escala = 1 + 0.08 * prog;
  else if (p.cam === 'micro') escala = 1 + 0.04 * prog;
  else if (p.cam === 'zoom112') escala = 1 + 0.12 * prog;
  else if (p.cam === 'paneo') {
    escala = 1.08;
    tx = interpolate(prog, [0, 1], [-2.5, 2.5]);
  }
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000'}}>
      <Img src={staticFile(`img916v/${p.id}.png`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `translateX(${tx}%) scale(${escala * vida})`}} />
    </AbsoluteFill>
  );
};

const Pop: React.FC<{texto: string; y: number; size: number; color?: string}> = ({texto, y, size, color = '#fff'}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, 2, 4], [0.6, 1.12, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', top: y, width: '100%', display: 'flex', justifyContent: 'center'}}>
      <div style={{fontFamily, fontSize: size, color, textAlign: 'center', lineHeight: 1.05, padding: '0 50px', transform: `scale(${s})`, ...trazo(10)}}>{texto}</div>
    </div>
  );
};

// ---------------------------------------------------------------- tarjetas de datos verticales
const Dato: React.FC<{p: Plano}> = ({p}) => {
  const f = useCurrentFrame();
  const cfg = p.tipo === 'dato12' ? {n: 12, m: 1, color: '#8a8a8a', pre: 'MENOS DE', main: '1 DE CADA 12', cols: 6} :
    p.tipo === 'dato8' ? {n: 8, m: 1, color: '#8a8a8a', pre: 'MUERTES POR VIOLENCIA', main: '1 DE CADA 8', cols: 4} :
      {n: 10, m: 7, color: '#59c13b', pre: 'MUERTES POR ENFERMEDAD', main: '7 DE 10', cols: 5};
  return (
    <AbsoluteFill style={{background: 'linear-gradient(#1c2740,#0f1626)'}}>
      <div style={{position: 'absolute', top: 500, width: '100%', textAlign: 'center'}}>
        <div style={{fontFamily, fontSize: 72, color: '#fff', ...trazo(8)}}>{cfg.pre}</div>
        <div style={{fontFamily, fontSize: 170, lineHeight: 1, color: AMARILLO, ...trazo(12)}}>{cfg.main}</div>
      </div>
      <div style={{position: 'absolute', top: 780, width: '100%', display: 'grid', gridTemplateColumns: `repeat(${cfg.cols}, auto)`, justifyContent: 'center', columnGap: 26, rowGap: 6}}>
        {Array.from({length: cfg.n}).map((_, k) => {
          const pinta = k < cfg.m ? interpolate(f, [10 + k * 5, 14 + k * 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
          const entra = interpolate(f, [k, k + 5], [0, 1], {extrapolateRight: 'clamp'});
          const sc = cfg.n === 12 ? 1.05 : cfg.n === 10 ? 1.2 : 1.25;
          return <div key={k} style={{opacity: entra, transform: `scale(${sc})`, transformOrigin: 'top center', height: 150 * sc}}><Personita color={pinta > 0.5 ? cfg.color : '#f3d9b1'} /></div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

const Ranking: React.FC<{p: Plano}> = ({p}) => {
  const f = useCurrentFrame();
  const filas = [
    {t: 'ENFERMEDAD Y GÉRMENES', v: '7 DE CADA 10 · ~70 %', pct: 70, c: '#59c13b'},
    {t: 'VIOLENCIA (OTRAS PERSONAS)', v: '1 DE CADA 8 · 12,5 %', pct: 12.5, c: '#e04a3b'},
    {t: 'ACCIDENTES, LEÓN INCLUIDO', v: 'MENOS DE 1 DE 12 · 8,1 %', pct: 8.1, c: '#f2b33d'},
  ];
  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117'}}>
      {filas.map((r, k) => {
        const t0 = (p.barras?.[k] ?? k * 2) * FPS;
        const g = interpolate(f, [t0, t0 + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        const o = interpolate(f, [t0 - 3, t0 + 3], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const ancho = Math.max(220, 980 * (r.pct / 70)) * g;
        return (
          <div key={k} style={{position: 'absolute', left: 50, top: 520 + k * 300, width: 980, opacity: o}}>
            <div style={{fontFamily, fontSize: 64, color: '#fff', ...trazo(6)}}>{r.t}</div>
            <div style={{position: 'relative', height: 160, marginTop: 6}}>
              <div style={{position: 'absolute', height: 160, width: ancho, backgroundColor: r.c, borderRadius: 14, border: '6px solid #000'}} />
              <div style={{position: 'absolute', left: 24, top: 40, fontFamily, fontSize: 68, color: '#fff', whiteSpace: 'nowrap', ...trazo(8)}}>{r.v}</div>
            </div>
          </div>
        );
      })}
      <div style={{position: 'absolute', top: 1440, left: 50, right: 50, fontFamily: 'sans-serif', fontSize: 32, color: '#c3cad4', lineHeight: 1.3}}>
        Gurven y Kaplan, 2007. Grupos de cazadores-recolectores recientes, no de hace 20.000 años.
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- insignia permanente
const Insignia: React.FC<{ins: any}> = ({ins}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  return (
    <>
      <AbsoluteFill style={{background: 'linear-gradient(rgba(0,0,0,.62) 0%, rgba(0,0,0,.35) 22%, rgba(0,0,0,0) 30%)'}} />
      <div style={{position: 'absolute', top: 200, width: '100%', textAlign: 'center'}}>
        <div style={{fontFamily, fontSize: 64, color: '#fff', letterSpacing: 2, ...trazo(8)}}>FORMA #{ins.num} DE 7</div>
        <svg width={W} height={110} style={{display: 'block'}}>
          {ICONOS.map((_, i) => {
            let ab = ins.abiertos.includes(i) ? 1 : 0;
            if (i === ins.actual) ab = interpolate(t, [ins.abre_en, ins.abre_en + 0.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
            const x = W / 2 + (i - 3) * 104;
            return <g key={i} opacity={i === ins.actual || ins.abiertos.includes(i) ? 1 : 0.55}><Candado i={i} abierto={ab} x={x} y={62} s={0.9} /></g>;
          })}
        </svg>
        <div style={{fontFamily, fontSize: 104, lineHeight: 1, color: AMARILLO, ...trazo(10)}}>{ins.nombre}</div>
      </div>
    </>
  );
};

// ---------------------------------------------------------------- subtítulos grandes
const Subtitulos: React.FC<{tl: any; sube: boolean; ocultar: boolean}> = ({tl, sube, ocultar}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const lineas = React.useMemo(() => agrupar(tl.subs), [tl]);
  if (ocultar) return null;
  const l = lineas.find((x, k) => t >= x.ini - 0.05 && t < (lineas[k + 1] ? Math.min(lineas[k + 1].ini - 0.05, x.fin + 0.3) : x.fin + 0.3));
  if (!l) return null;
  return (
    <div style={{position: 'absolute', top: (sube ? 1190 - 80 : 1190), width: '100%', display: 'flex', justifyContent: 'center'}}>
      <div style={{display: 'flex', columnGap: 30, rowGap: 0, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 980}}>
        {l.palabras.map((w: any, k: number) => {
          const activa = t >= w.ini - 0.03 && t < w.fin + 0.03;
          return <span key={k} style={{fontFamily, fontSize: 96, lineHeight: 1.12, color: activa ? '#fff' : AMARILLO, transform: `scale(${activa ? 1.12 : 1})`,
            display: 'inline-block', textTransform: 'uppercase', ...trazo(8)}}>{w.w}</span>;
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- composición
export const Serie: React.FC<{tl: any; audio: string}> = ({tl, audio}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const actual = tl.planos.find((p: Plano) => t >= p.ini && t < p.fin) || {};
  const ins = tl.insignia;
  const enCliff = ins && t >= ins.cliff_ini;
  const sube = Boolean(actual.overlay) || Boolean(enCliff);
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {tl.planos.map((p: Plano, k: number) => {
        const from = Math.round(p.ini * FPS);
        const dur = Math.max(1, Math.round(p.fin * FPS) - from);
        return (
          <Sequence key={k} from={from} durationInFrames={dur}>
            {p.tipo === 'img' ? <Imagen p={p} dur={dur} /> : p.tipo === 'ranking' ? <Ranking p={p} /> : <Dato p={p} />}
            {p.overlay ? <Sequence from={3}><Pop texto={p.overlay} y={ins ? 900 : 860} size={96} /></Sequence> : null}
          </Sequence>
        );
      })}
      {ins ? <Insignia ins={ins} /> : null}
      {ins ? (
        <Sequence from={Math.round(ins.cliff_ini * FPS)}>
          <Pop texto={ins.cliff_texto} y={860} size={84} color={AMARILLO} />
        </Sequence>
      ) : null}
      <Subtitulos tl={tl} sube={sube} ocultar={actual.tipo === 'ranking'} />
      <Audio src={staticFile(audio)} />
    </AbsoluteFill>
  );
};
