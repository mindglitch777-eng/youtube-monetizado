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

const Escena: React.FC<{ imagen: string | null; frames: number }> = ({ imagen, frames }) => {
  const frame = useCurrentFrame();
  const opacidad = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const zoom = interpolate(frame, [0, frames], [1, 1.06]);
  if (!imagen) return <AbsoluteFill style={{ backgroundColor: FONDO }} />;
  return (
    <AbsoluteFill style={{ opacity: opacidad }}>
      <Img src={staticFile(imagen)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }} />
    </AbsoluteFill>
  );
};

const Icono: React.FC<{ src: string }> = ({ src }) => (
  <Img
    src={staticFile(src)}
    style={{
      position: "absolute",
      right: 48,
      bottom: 48,
      width: 150,
      height: 150,
      borderRadius: "50%",
      objectFit: "cover",
      border: "5px solid rgba(255, 255, 255, 0.9)",
      boxShadow: "0 6px 20px rgba(0, 0, 0, 0.45)",
    }}
  />
);

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
      {armarTramos(segmentos, duracionTotal).map((tramo) => (
        <Sequence key={`img-${tramo.desde}`} from={f(tramo.desde)} durationInFrames={Math.max(1, f(tramo.hasta) - f(tramo.desde))}>
          <Escena imagen={tramo.imagen} frames={f(tramo.hasta) - f(tramo.desde)} />
        </Sequence>
      ))}

      {segmentos.map((s, n) => {
        const siguiente = segmentos[n + 1]?.inicio ?? duracionTotal;
        return (
          <Sequence key={s.id} from={f(s.inicio)} durationInFrames={Math.max(1, f(siguiente) - f(s.inicio))} name={s.id}>
            <Audio src={staticFile(s.audio)} />
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
