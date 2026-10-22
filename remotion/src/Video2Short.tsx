import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {BEBAS, MONT, FPS, contorno, Imagen, Texto, tinte} from './Video2';
import {agrupar} from './Video';

const NOTA_COLOR: Record<string, string> = {S: '#ff4fd8', A: '#3ddc84', B: '#8bd346', C: '#ffd23f', D: '#ff9f1c', F: '#ff3b3b'};
type P = any;

// barra de recap (tercio superior): título, vidas y notas de las épocas anteriores
const Recap: React.FC<{r: P}> = ({r}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 560, background: 'linear-gradient(rgba(5,5,10,.82) 0%, rgba(5,5,10,.55) 60%, rgba(5,5,10,0) 100%)'}} />
    <div style={{position: 'absolute', top: 120, left: 40, right: 40, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
      <div style={{fontFamily: BEBAS, fontSize: 92, color: '#fff', letterSpacing: 3, lineHeight: 1, ...contorno(6)}}>{r.titulo}</div>
      <div style={{display: 'flex', gap: 6}}>
        {Array.from({length: 8}).map((_, i) => (
          <svg key={i} width="46" height="42" viewBox="0 0 32 29"><path d="M16 28 2 14C-3 8 2-1 9 1c3 1 5 3 7 6 2-3 4-5 7-6 7-2 12 7 7 13Z" fill={i < r.vidas ? '#ff3b4e' : 'rgba(255,255,255,.2)'} stroke="#000" strokeWidth="2.5" /></svg>
        ))}
      </div>
      {r.previas.length ? (
        <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 10, maxWidth: 1000}}>
          {r.previas.map((p: P, i: number) => (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 8, background: 'rgba(255,255,255,.12)', borderRadius: 10, padding: '4px 12px 4px 4px'}}>
              <span style={{background: NOTA_COLOR[p.nota], color: '#000', fontFamily: BEBAS, fontSize: 40, borderRadius: 8, padding: '0 10px', border: '3px solid #000'}}>{p.nota}</span>
              <span style={{fontFamily: MONT, fontWeight: 800, fontSize: 26, color: '#fff'}}>{p.epoca}</span>
            </div>
          ))}
        </div>
      ) : null}
      {r.jefe ? <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 30, color: '#ffd23f', ...contorno(0)}}>{r.jefe}</div> : null}
    </div>
  </AbsoluteFill>
);

// subtítulos grandes palabra por palabra, en el tercio central
const Subs: React.FC<{subs: P[]; hasta: number}> = ({subs, hasta}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const lineas = React.useMemo(() => agrupar(subs), [subs]);
  if (t > hasta) return null;
  const l = lineas.find((x, k) => t >= x.ini - 0.05 && t < (lineas[k + 1] ? Math.min(lineas[k + 1].ini - 0.05, x.fin + 0.4) : x.fin + 0.4));
  if (!l) return null;
  return (
    <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', paddingTop: 1080}}>
      <div style={{display: 'flex', columnGap: 30, rowGap: 0, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 1000, padding: '0 30px'}}>
        {l.palabras.map((w: P, k: number) => {
          const activa = t >= w.ini - 0.03 && t < w.fin + 0.03;
          return (
            <span key={k} style={{fontFamily: BEBAS, fontSize: 112, lineHeight: 1.02, color: activa ? '#ffd23f' : '#fff', transform: `scale(${activa ? 1.1 : 1})`,
              display: 'inline-block', textTransform: 'uppercase', letterSpacing: 1, ...contorno(9)}}>{w.w}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Tarjeta: React.FC<{n: number}> = ({n}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, 4, 8], [0.7, 1.08, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Img src={staticFile('v2/img916/239.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', paddingBottom: 380}}>
        <div style={{transform: `scale(${s})`, textAlign: 'center', padding: '0 50px'}}>
          <div style={{fontFamily: BEBAS, fontSize: 150, color: '#ffd23f', lineHeight: 1, ...contorno(10)}}>{n === 0 ? 'TRÁILER' : `PARTE ${n} DE 8`}</div>
          <div style={{fontFamily: BEBAS, fontSize: 96, color: '#fff', lineHeight: 1.05, marginTop: 16, ...contorno(9)}}>EL VIDEO COMPLETO ESTÁ EN MI CANAL</div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Short2: React.FC<{tl: P; audio: string}> = ({tl, audio}) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  let tin = tinte(tl.estilo, t, {});
  if (tl.drenaje && t >= tl.drenaje[0]) tin = tinte('drenaje', t, {ini: tl.drenaje[0], fin_rampa: tl.drenaje[1]});
  const enTarjeta = t >= tl.fin_voz;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{filter: tin.filtro}}>
        {tl.planos.map((p: P, k: number) => {
          const from = Math.round(p.ini * FPS);
          const dur = Math.max(1, Math.round(p.fin * FPS) - from);
          return (
            <Sequence key={k} from={from} durationInFrames={dur}>
              {p.tipo === 'img' ? <Imagen p={p} dur={dur} dir="v2/img916" vertical /> : p.tipo === 'tarjeta' ? <Tarjeta n={p.n} /> : <AbsoluteFill style={{backgroundColor: '#000'}} />}
            </Sequence>
          );
        })}
        {tin.capa && !enTarjeta ? <AbsoluteFill style={{backgroundColor: tin.capa, opacity: tin.op, mixBlendMode: (tin.mezcla as any) || 'normal'}} /> : null}
      </AbsoluteFill>
      {!enTarjeta ? <Recap r={tl.recap} /> : null}
      {tl.textos.map((x: P, k: number) => (
        <Sequence key={`t${k}`} from={Math.round(x.ini * FPS)} durationInFrames={Math.max(1, Math.round((x.fin - x.ini) * FPS))}>
          <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', paddingTop: 690}}>
            <ShortTexto texto={x.texto} />
          </AbsoluteFill>
        </Sequence>
      ))}
      <Subs subs={tl.subs} hasta={tl.fin_voz} />
      <Audio src={staticFile(audio)} />
    </AbsoluteFill>
  );
};

const ShortTexto: React.FC<{texto: string}> = ({texto}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, 2, 4], [0.6, 1.12, 1], {extrapolateRight: 'clamp'});
  const partes = texto.includes(' · ') ? texto.split(' · ') : [texto];
  return (
    <div style={{transform: `scale(${s})`, textAlign: 'center', padding: '0 40px'}}>
      {partes.map((x, i) => (
        <div key={i} style={{fontFamily: BEBAS, fontSize: 104, lineHeight: 0.98, color: '#ffd23f', ...contorno(10)}}>{x}</div>
      ))}
    </div>
  );
};
