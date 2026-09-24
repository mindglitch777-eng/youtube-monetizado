import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Subtitulos } from "./Subtitulos";
import type { Props, Segmento } from "./tipos";

const FONDO = "#2B2118";
const VOLUMEN_SONIDOS = 0.6;
const VOLUMEN_MUSICA = 0.12; // cama suave, siempre por debajo de la voz
const SOLAPE = 0.35; // segundos de fundido cruzado entre escenas (shorts)

// lineas: inicios de línea dentro del tramo (segundos desde su comienzo), para
// los pulsos de zoom. whoosh: el corte de entrada lleva whoosh (destello).
type Tramo = { imagen: string | null; desde: number; hasta: number; lineas: number[]; whoosh: boolean };

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
    if (ultimo && ultimo.imagen === s.imagen) {
      ultimo.lineas.push(s.inicio - ultimo.desde);
      continue;
    }
    if (ultimo) ultimo.hasta = s.inicio;
    const whoosh = s.sonidos.some((sonido) => sonido.archivo.endsWith("transicion.mp3"));
    tramos.push({ imagen: s.imagen, desde: s.inicio, hasta: total, lineas: [], whoosh });
  }
  return tramos;
}

// En los shorts, para que la imagen nunca quede quieta: entra con un "punch"
// de zoom, hace Ken Burns, da un pulso chico de zoom en cada línea nueva y, en
// los cortes con whoosh, un destello breve. El video largo mantiene el Ken
// Burns suave de siempre.
const Escena: React.FC<{ tramo: Tramo; frames: number; indice: number; entrada: number }> = ({
  tramo,
  frames,
  indice,
  entrada,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const vertical = height > width;
  const opacidad = interpolate(frame, [0, entrada], [0, 1], { extrapolateRight: "clamp" });
  const movimiento = MOVIMIENTOS[indice % MOVIMIENTOS.length];
  const avance = interpolate(frame, [0, frames], [0, 1], { extrapolateRight: "clamp" });

  let zoom = interpolate(avance, [0, 1], [1, 1.06]);
  let paneo = 0;
  let destello = 0;
  if (vertical) {
    const punch = indice === 0 ? 0 : 0.14 * (1 - spring({ frame, fps, config: { damping: 18, stiffness: 120 } }));
    const pulsos = tramo.lineas.reduce((total, inicio) => {
      const t = frame / fps - inicio;
      return t < 0 ? total : total + 0.035 * Math.exp(-t / 0.18);
    }, 0);
    zoom = 1.1 * interpolate(avance, [0, 1], movimiento.zoom) * (1 + punch + pulsos);
    paneo = interpolate(avance, [0, 1], movimiento.x) * 3; // % del ancho
    destello = tramo.whoosh ? interpolate(frame, [entrada, entrada + 7], [0.35, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  }
  if (!tramo.imagen) return <AbsoluteFill style={{ backgroundColor: FONDO }} />;
  return (
    <AbsoluteFill style={{ opacity: opacidad }}>
      <Img
        src={staticFile(tramo.imagen)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${zoom}) translateX(${paneo}%)`,
        }}
      />
      {destello > 0 ? <AbsoluteFill style={{ backgroundColor: "white", opacity: destello }} /> : null}
    </AbsoluteFill>
  );
};

// Viñeta: oscurece los bordes para dar clima y que los subtítulos resalten.
const Vineta: React.FC = () => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)" }} />
);

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
  const { fps, width, height } = useVideoConfig();
  const vertical = height > width;
  const f = (segundos: number) => Math.round(segundos * fps);

  if (!timeline) {
    return (
      <AbsoluteFill style={{ backgroundColor: FONDO, color: "white", justifyContent: "center", alignItems: "center", fontSize: 48 }}>
        Falta public/timeline.json — correr: npm run preparar -- ../content/&lt;video&gt;
      </AbsoluteFill>
    );
  }

  const { segmentos, duracionTotal } = timeline;
  const totalFrames = f(duracionTotal);
  return (
    <AbsoluteFill style={{ backgroundColor: FONDO }}>
      {armarTramos(segmentos, duracionTotal).map((tramo, indice) => {
        // En los shorts cada escena arranca un poco antes y se funde sobre la anterior.
        const adelanto = vertical && indice > 0 ? f(SOLAPE) : 0;
        const desde = f(tramo.desde) - adelanto;
        const frames = Math.max(1, f(tramo.hasta) - desde);
        return (
          <Sequence key={`img-${tramo.desde}`} from={desde} durationInFrames={frames}>
            <Escena tramo={tramo} frames={frames} indice={indice} entrada={adelanto || 12} />
          </Sequence>
        );
      })}

      <Vineta />

      {timeline.musica ? (
        <Audio
          src={staticFile(timeline.musica)}
          loop
          volume={(frame) =>
            interpolate(frame, [0, fps, totalFrames - fps * 1.5, totalFrames], [0, VOLUMEN_MUSICA, VOLUMEN_MUSICA, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      ) : null}

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
          <Sequence key={`${s.id}-${sonido.archivo}-${sonido.en}`} from={f(s.inicio + sonido.en)} name={`sonido ${sonido.archivo.split("/").pop()}`}>
            <Audio src={staticFile(sonido.archivo)} volume={sonido.volumen ?? VOLUMEN_SONIDOS} />
          </Sequence>
        )),
      )}

      <Icono src={timeline.icono} />
    </AbsoluteFill>
  );
};
