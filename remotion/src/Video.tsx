import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Subtitulos } from "./Subtitulos";
import type { Props, Segmento } from "./tipos";

const FONDO = "#2B2118";
const VOLUMEN_SONIDOS = 0.6;

type Tramo = { imagen: string | null; desde: number; hasta: number };

// Ken Burns: zoom lento con un paneo suave; la dirección se alterna por escena
// para que dos escenas seguidas no se muevan igual. En vertical el movimiento
// es más marcado (la imagen cuadrada tiene margen de sobra a los costados).
const MOVIMIENTOS = [
  { zoom: [1, 1.08], x: [-1, 1] },
  { zoom: [1.08, 1], x: [1, -1] },
  { zoom: [1, 1.08], x: [1, -1] },
  { zoom: [1.08, 1], x: [-1, 1] },
];

// Une segmentos seguidos con la misma imagen (la transición mantiene la escena
// anterior) y estira cada imagen hasta el comienzo de la siguiente.
function armarTramos(segmentos: Segmento[], total: number): Tramo[] {
  const tramos: Tramo[] = [];
  for (const s of segmentos) {
    const ultimo = tramos[tramos.length - 1];
    if (ultimo && ultimo.imagen === s.imagen) continue;
    if (ultimo) ultimo.hasta = s.inicio;
    tramos.push({ imagen: s.imagen, desde: s.inicio, hasta: total });
  }
  return tramos;
}

const Escena: React.FC<{ imagen: string | null; frames: number; indice: number }> = ({ imagen, frames, indice }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const vertical = height > width;
  const opacidad = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const movimiento = MOVIMIENTOS[indice % MOVIMIENTOS.length];
  const avance = interpolate(frame, [0, frames], [0, 1], { extrapolateRight: "clamp" });
  const zoomExtra = vertical ? 1.1 : 1; // en vertical arranca algo más cerca
  const zoom = zoomExtra * interpolate(avance, [0, 1], vertical ? movimiento.zoom : [1, 1.06]);
  const paneo = vertical ? interpolate(avance, [0, 1], movimiento.x) * 3 : 0; // % del ancho
  if (!imagen) return <AbsoluteFill style={{ backgroundColor: FONDO }} />;
  return (
    <AbsoluteFill style={{ opacity: opacidad }}>
      <Img
        src={staticFile(imagen)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${zoom}) translateX(${paneo}%)`,
        }}
      />
    </AbsoluteFill>
  );
};

// En los shorts se sube para no quedar tapado por los botones de YouTube Shorts.
const Icono: React.FC<{ src: string }> = ({ src }) => {
  const { width, height } = useVideoConfig();
  return (
  <Img
    src={staticFile(src)}
    style={{
      position: "absolute",
      right: 48,
      bottom: height > width ? 380 : 48,
      width: 150,
      height: 150,
      borderRadius: "50%",
      objectFit: "cover",
      border: "5px solid rgba(255, 255, 255, 0.9)",
      boxShadow: "0 6px 20px rgba(0, 0, 0, 0.45)",
    }}
  />
  );
};

export const Video: React.FC<Props> = ({ timeline }) => {
  const { fps } = useVideoConfig();
  const f = (segundos: number) => Math.round(segundos * fps);

  if (!timeline) {
    return (
      <AbsoluteFill style={{ backgroundColor: FONDO, color: "white", justifyContent: "center", alignItems: "center", fontSize: 48 }}>
        Falta public/timeline.json — correr: npm run preparar -- ../content/&lt;video&gt;
      </AbsoluteFill>
    );
  }

  const { segmentos, duracionTotal } = timeline;
  return (
    <AbsoluteFill style={{ backgroundColor: FONDO }}>
      {armarTramos(segmentos, duracionTotal).map((tramo, indice) => (
        <Sequence key={`img-${tramo.desde}`} from={f(tramo.desde)} durationInFrames={Math.max(1, f(tramo.hasta) - f(tramo.desde))}>
          <Escena imagen={tramo.imagen} frames={f(tramo.hasta) - f(tramo.desde)} indice={indice} />
        </Sequence>
      ))}

      {/* Short standalone: una sola narración para todo el video. */}
      {timeline.audio ? <Audio src={staticFile(timeline.audio)} /> : null}

      {segmentos.map((s, n) => {
        const siguiente = segmentos[n + 1]?.inicio ?? duracionTotal;
        return (
          <Sequence key={s.id} from={f(s.inicio)} durationInFrames={Math.max(1, f(siguiente) - f(s.inicio))} name={s.id}>
            {s.audio ? <Audio src={staticFile(s.audio)} /> : null}
            <Subtitulos palabras={s.palabras} destacada={s.destacada} duracion={s.duracion} />
          </Sequence>
        );
      })}

      {segmentos.flatMap((s) =>
        s.sonidos.map((sonido) => (
          <Sequence key={`${s.id}-${sonido.archivo}`} from={f(s.inicio + sonido.en)} name={`sonido ${sonido.archivo.split("/").pop()}`}>
            <Audio src={staticFile(sonido.archivo)} volume={VOLUMEN_SONIDOS} />
          </Sequence>
        )),
      )}

      <Icono src={timeline.icono} />
    </AbsoluteFill>
  );
};
