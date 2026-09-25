import { CameraMotionBlur } from "@remotion/motion-blur";
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// FASE 0 — escena de prueba (5-10s), decisión 3D vs 2D ya tomada: 2D.
// Ver justificación completa en la respuesta al usuario; en resumen: el
// render 3D real (@remotion/three) tardó ~2x más por frame que esta versión
// 2D, y la iluminación direccional real generaba zonas en sombra que le
// restaban legibilidad a la silueta plana (el estilo del canal, RULES.md,
// pide siluetas planas sin rasgos — el volumen 3D jugaba en contra, no a
// favor). Por eso el personaje sigue siendo SVG/CSS, pero con la misma
// física de resorte para la pose y con motion blur real de cámara.

const COLOR_CUERPO_CLARO = "#B08D63";
const COLOR_CUERPO_OSCURO = "#5E4830";
const COLOR_PISO = "#241A12";
const COLOR_FONDO = "#100C08";

const CAMBIO_POSE_FRAME = 75; // ~2.5s a 30fps: momento en que el personaje pasa a señalar

// Bounding box vertical del personaje de pie, en coordenadas locales
// (origen en el centro vertical del cuerpo): de -ALTO_MITAD a +ALTO_MITAD.
// Ajustado en el encuadre para que el grupo completo (Escena, más abajo)
// ocupe del 35% al 75% de la altura del video, no solo la mitad superior.
export const ALTO_PERSONAJE = 600;
const ALTO_MITAD = ALTO_PERSONAJE / 2;

// Torso: path en vez de óvalo/rect simétrico — ensancha en los hombros
// (±68) y se angosta hacia la cintura (±40) antes de volver a abrir un
// poco en la cadera (±52), como una silueta humana real, no geometría
// genérica. Cabeza más chica en relación al cuerpo (r=42 sobre ~600 de
// alto total, ~1/7 — proporción humana, no la cabeza sobredimensionada
// de la versión anterior).
const Personaje: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const t = spring({ frame: frame - CAMBIO_POSE_FRAME, fps, config: { damping: 11, stiffness: 90, mass: 1.1 } });
  const anguloHombro = interpolate(t, [0, 1], [8, -95]);
  const anguloCodo = interpolate(t, [0, 1], [10, -8]);
  const inclinacionTorso = interpolate(t, [0, 1], [0, -7]);

  return (
    <g transform={`rotate(${inclinacionTorso})`}>
      {/* Pierna izquierda: cadera -> rodilla (joint independiente) -> tobillo,
          mismo patrón de huesos que el brazo (segmento + grupo rotado). */}
      <g transform="translate(-24, 40) rotate(4)">
        <rect x={-17} y={0} width={34} height={140} rx={17} fill="url(#luzCuerpo)" />
        <g transform="translate(0, 140) rotate(6)">
          <rect x={-14} y={0} width={28} height={118} rx={14} fill="url(#luzCuerpo)" />
          <rect x={-19} y={112} width={42} height={18} rx={8} fill="url(#luzCuerpo)" />
        </g>
      </g>
      {/* Pierna derecha */}
      <g transform="translate(24, 40) rotate(-3)">
        <rect x={-17} y={0} width={34} height={140} rx={17} fill="url(#luzCuerpo)" />
        <g transform="translate(0, 140) rotate(-5)">
          <rect x={-14} y={0} width={28} height={118} rx={14} fill="url(#luzCuerpo)" />
          <rect x={-19} y={112} width={42} height={18} rx={8} fill="url(#luzCuerpo)" />
        </g>
      </g>
      {/* Brazo izquierdo: queda quieto, apoyado */}
      <g transform="translate(-64, -150) rotate(7)">
        <rect x={-15} y={0} width={30} height={105} rx={15} fill="url(#luzCuerpo)" />
      </g>
      {/* Torso: hombros anchos -> cintura angosta -> cadera con leve vuelo */}
      <path
        d="M -68,-222 C -78,-210 -78,-195 -74,-180 C -64,-120 -50,-60 -40,-30
           C -55,-10 -58,20 -52,40 Q -52,52 -40,54 L 40,54 Q 52,52 52,40
           C 58,20 55,-10 40,-30 C 50,-60 64,-120 74,-180 C 78,-195 78,-210 68,-222 Z"
        fill="url(#luzCuerpo)"
      />
      {/* Cabeza, sin rasgos (RULES.md), proporción real respecto al cuerpo */}
      <circle cx={0} cy={-258} r={42} fill="url(#luzCuerpo)" />
      {/* Brazo derecho: el que anima la pose (hombro + codo articulados) */}
      <g transform={`translate(64, -150) rotate(${anguloHombro})`}>
        <rect x={-15} y={0} width={30} height={105} rx={15} fill="url(#luzCuerpo)" />
        <g transform={`translate(0, 105) rotate(${anguloCodo})`}>
          <rect x={-13} y={0} width={26} height={90} rx={13} fill="url(#luzCuerpo)" />
        </g>
      </g>
    </g>
  );
};

// Texto kinetic-protagonista: NO es un subtítulo chico abajo — es un elemento
// grande, centrado, con entrada de resorte (escala + blur), que domina el
// frame igual que el personaje.
const TextoProtagonista: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const APARECE_EN = 20;
  const entrada = spring({ frame: frame - APARECE_EN, fps, config: { damping: 13, stiffness: 140 } });
  const escala = interpolate(entrada, [0, 1], [0.4, 1]);
  const opacidad = interpolate(entrada, [0, 1], [0, 1], { extrapolateRight: "clamp" });
  const desenfoque = interpolate(entrada, [0, 1], [18, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 220 }}>
      <div
        style={{
          transform: `scale(${escala})`,
          opacity: opacidad,
          filter: `blur(${desenfoque}px)`,
          fontFamily: "Montserrat, sans-serif",
          fontWeight: 900,
          fontSize: 108,
          lineHeight: 1.05,
          textAlign: "center",
          color: "#F4E9DB",
          textShadow: "0 8px 30px rgba(0,0,0,0.55)",
          width: "88%",
        }}
      >
        HE NEVER LISTENS
      </div>
    </AbsoluteFill>
  );
};

const Escena: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  // Cámara: paneo lateral + acercamiento continuos durante todo el clip, nunca
  // estática. CameraMotionBlur (más abajo) hace que el desenfoque de este
  // movimiento — y el del brazo en pose — se intensifique solo cuando la
  // velocidad entre frames es mayor (el cambio de pose), sin tener que
  // calcularlo a mano.
  const avance = frame / (durationInFrames || 1);
  const panX = interpolate(avance, [0, 1], [-30, 30]);
  const escalaCamara = interpolate(avance, [0, 1], [1, 1.18]);

  const cx = width / 2;

  // Encuadre: el personaje de pie (ALTO_PERSONAJE en coordenadas locales,
  // centrado en su propio origen) tiene que ocupar del 35% al 75% de la
  // altura del video, no solo la mitad superior. escalaBase lo estira a ese
  // tamaño en pantalla; centroY ubica el centro vertical del cuerpo en el
  // punto medio de esa franja (55% de la altura).
  const escalaBase = (height * 0.4) / ALTO_PERSONAJE; // 0.75 - 0.35 = 0.4 de la altura
  const centroY = height * 0.55;
  const pisoY = centroY + (ALTO_PERSONAJE / 2) * escalaBase;

  return (
    <AbsoluteFill style={{ backgroundColor: COLOR_FONDO }}>
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <linearGradient id="luzCuerpo" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={COLOR_CUERPO_CLARO} />
            <stop offset="100%" stopColor={COLOR_CUERPO_OSCURO} />
          </linearGradient>
          <radialGradient id="sombraPiso" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#000000" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#000000" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse cx={cx + panX} cy={pisoY + 12} rx={170} ry={36} fill="url(#sombraPiso)" />
        <rect x={0} y={pisoY + 18} width={width} height={height - (pisoY + 18)} fill={COLOR_PISO} opacity={0.5} />
        <g transform={`translate(${cx + panX}, ${centroY}) scale(${escalaBase * escalaCamara})`}>
          <Personaje frame={frame} fps={fps} />
        </g>
      </svg>
      <TextoProtagonista frame={frame} fps={fps} />
    </AbsoluteFill>
  );
};

export const EscenaFase0: React.FC = () => {
  const frame = useCurrentFrame();

  // SFX: aquí va el sonido de impacto (golpe/whoosh corto) en el momento del
  // cambio de pose — CAMBIO_POSE_FRAME, frame 75 (~2.5s). Placeholder mudo
  // hasta que el usuario provea el archivo real; no se manda audio todavía.
  const enCambioDePose = frame >= CAMBIO_POSE_FRAME && frame < CAMBIO_POSE_FRAME + 2;
  void enCambioDePose; // marcador del punto de disparo, sin efecto todavía

  return (
    <CameraMotionBlur shutterAngle={170} samples={5}>
      <Escena />
    </CameraMotionBlur>
  );
};
