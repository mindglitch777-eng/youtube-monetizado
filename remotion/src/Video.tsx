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
import type { CorteImagen, Props, Segmento } from "./tipos";

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

// Si el timeline trae sus propios cortes de imagen (una imagen cada ~2 s), se
// usan esos; los pulsos de zoom caen en las líneas que empiezan dentro de cada corte.
function tramosDeCortes(cortes: CorteImagen[], segmentos: Segmento[]): Tramo[] {
  return cortes.map((c) => ({
    imagen: c.imagen,
    desde: c.desde,
    hasta: c.hasta,
    whoosh: c.whoosh,
    lineas: segmentos.filter((s) => s.inicio > c.desde + 0.05 && s.inicio < c.hasta).map((s) => s.inicio - c.desde),
  }));
}

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
    // Con cortes cada ~2 s el golpe de entrada es más chico para no marear.
    const fuerza = frames < fps * 3 ? 0.07 : 0.14;
    const punch = indice === 0 ? 0 : fuerza * (1 - spring({ frame, fps, config: { damping: 18, stiffness: 120 } }));
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

// Contador de lista ("2/5"): una placa amarilla con texto oscuro, bien distinta
// de los subtítulos (blancos con contorno). Entra con un salto al cambiar.
const Contador: React.FC<{ valor: string; desde: number }> = ({ valor, desde }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const salto = spring({ frame: frame - desde, fps, config: { damping: 11, stiffness: 160 } });
  return (
    <div
      style={{
        position: "absolute",
        top: "33%",
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        transform: `scale(${0.6 + 0.4 * salto}) rotate(${(1 - salto) * -8}deg)`,
        opacity: Math.min(1, salto * 2),
      }}
    >
      <div
        style={{
          fontFamily: "Montserrat",
          fontWeight: 900,
          fontSize: 120,
          lineHeight: 1,
          color: "#1B140F",
          backgroundColor: "#FFD83D",
          padding: "18px 44px",
          borderRadius: 28,
          boxShadow: "0 12px 30px rgba(0, 0, 0, 0.5)",
          letterSpacing: 2,
        }}
      >
        {valor}
      </div>
    </div>
  );
};

// Shake de cámara + flash en los momentos de impacto ("Number X:").
function efectoImpacto(t: number, impactos: number[]) {
  let dx = 0;
  let dy = 0;
  let flash = 0;
  for (const inicio of impactos) {
    const d = t - inicio;
    if (d < 0 || d > 0.45) continue;
    const caida = Math.exp(-d / 0.12);
    dx += 22 * caida * Math.sin(d * 95);
    dy += 16 * caida * Math.cos(d * 80);
    flash = Math.max(flash, 0.45 * Math.exp(-d / 0.07));
  }
  return { dx, dy, flash };
}

// Overlays de llamada a la acción: una placa blanca que entra con un salto y
// late mientras dura la línea. Like = corazón; follow = campana.
const Overlay: React.FC<{ tipo: "like" | "follow"; desde: number }> = ({ tipo, desde }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entrada = spring({ frame: frame - desde, fps, config: { damping: 10, stiffness: 150 } });
  const latido = 1 + 0.07 * Math.max(0, Math.sin(((frame - desde) / fps) * Math.PI * 2.4));
  const rojo = "#FF3B5C";
  const icono =
    tipo === "like" ? (
      <svg width="110" height="100" viewBox="0 0 24 22">
        <path
          fill={rojo}
          d="M12 21.6 10.3 20C4.2 14.5.2 10.9.2 6.4.2 2.8 3 0 6.6 0c2 0 4 1 5.4 2.5C13.4 1 15.4 0 17.4 0 21 0 23.8 2.8 23.8 6.4c0 4.5-4 8.1-10.1 13.6L12 21.6z"
        />
      </svg>
    ) : (
      <svg width="96" height="100" viewBox="0 0 24 25">
        <path
          fill={rojo}
          d="M12 25a2.8 2.8 0 0 0 2.8-2.8H9.2A2.8 2.8 0 0 0 12 25zm8.4-7V11c0-4.3-2.3-7.9-6.3-8.8V1.3a2.1 2.1 0 0 0-4.2 0v.9C5.9 3.1 3.6 6.7 3.6 11v7L.8 20.8v1.4h22.4v-1.4L20.4 18z"
        />
      </svg>
    );
  return (
    <div
      style={{
        position: "absolute",
        top: "58%",
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        transform: `scale(${(0.5 + 0.5 * entrada) * latido})`,
        opacity: Math.min(1, entrada * 2),
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 28,
          backgroundColor: "white",
          borderRadius: 999,
          padding: "26px 56px",
          boxShadow: "0 16px 40px rgba(0, 0, 0, 0.55)",
          fontFamily: "Montserrat",
          fontWeight: 900,
          fontSize: 92,
          color: "#1B140F",
          letterSpacing: 2,
        }}
      >
        {icono}
        {tipo === "like" ? "LIKE" : "FOLLOW"}
      </div>
    </div>
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
  const frame = useCurrentFrame();
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
  const t = frame / fps;
  const impacto = efectoImpacto(t, segmentos.filter((s) => s.impacto).map((s) => s.inicio));
  const actual = [...segmentos].reverse().find((s) => s.inicio <= t);
  const contador = actual?.contador ?? null;
  const contadorDesde = contador
    ? f(segmentos.find((s) => s.contador === contador)?.inicio ?? 0)
    : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: FONDO }}>
      <AbsoluteFill style={{ transform: `translate(${impacto.dx}px, ${impacto.dy}px) scale(${impacto.dx || impacto.dy ? 1.03 : 1})` }}>
      {(timeline.tramos ? tramosDeCortes(timeline.tramos, segmentos) : armarTramos(segmentos, duracionTotal)).map((tramo, indice) => {
        // En los shorts cada escena arranca un poco antes y se funde sobre la anterior
        // (fundido más corto cuando los cortes son de ~2 s).
        const solape = Math.min(SOLAPE, (tramo.hasta - tramo.desde) * 0.15);
        const adelanto = vertical && indice > 0 ? f(solape) : 0;
        const desde = f(tramo.desde) - adelanto;
        const frames = Math.max(1, f(tramo.hasta) - desde);
        return (
          <Sequence key={`img-${tramo.desde}`} from={desde} durationInFrames={frames}>
            <Escena tramo={tramo} frames={frames} indice={indice} entrada={adelanto || 12} />
          </Sequence>
        );
      })}

      </AbsoluteFill>

      <Vineta />

      {impacto.flash > 0 ? <AbsoluteFill style={{ backgroundColor: "white", opacity: impacto.flash }} /> : null}

      {contador ? <Contador key={contador} valor={contador} desde={contadorDesde} /> : null}

      {actual?.overlay ? <Overlay key={actual.id} tipo={actual.overlay} desde={f(actual.inicio)} /> : null}

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
      {timeline.audio ? (
        <Audio src={staticFile(timeline.audio)} trimBefore={f(timeline.audioDesde ?? 0)} />
      ) : null}

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
