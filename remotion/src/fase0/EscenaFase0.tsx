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

const Personaje: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const t = spring({ frame: frame - CAMBIO_POSE_FRAME, fps, config: { damping: 11, stiffness: 90, mass: 1.1 } });
  const anguloHombro = interpolate(t, [0, 1], [8, -95]);
  const anguloCodo = interpolate(t, [0, 1], [10, -8]);
  const inclinacionTorso = interpolate(t, [0, 1], [0, -7]);

  return (
    <g transform={`rotate(${inclinacionTorso})`}>
      <rect x={-92} y={-30} width={30} height={150} rx={15} fill="url(#luzCuerpo)" transform="rotate(7 -77 -30)" />
      <rect x={-60} y={-90} width={120} height={210} rx={60} fill="url(#luzCuerpo)" />
      <circle cx={0} cy={-150} r={58} fill="url(#luzCuerpo)" />
      <g transform={`translate(85, -30) rotate(${anguloHombro})`}>
        <rect x={-15} y={0} width={30} height={130} rx={15} fill="url(#luzCuerpo)" />
        <g transform={`translate(0, 130) rotate(${anguloCodo})`}>
          <rect x={-13} y={0} width={26} height={105} rx={13} fill="url(#luzCuerpo)" />
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
  const cy = height / 2;

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
        <ellipse cx={cx} cy={cy + 245} rx={150} ry={34} fill="url(#sombraPiso)" />
        <rect x={0} y={cy + 250} width={width} height={height - (cy + 250)} fill={COLOR_PISO} opacity={0.5} />
        <g transform={`translate(${cx + panX}, ${cy}) scale(${escalaCamara})`}>
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
