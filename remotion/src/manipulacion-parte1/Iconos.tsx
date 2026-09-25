import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Íconos SVG simples, chicos y decorativos — nunca ilustración de escena
// completa (RULES.md: sin rasgos faciales, siluetas simples). Todos entran
// con resorte, nunca aparecen estáticos de golpe.

const useEntrada = (desdeFrame: number, config?: { damping?: number; stiffness?: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - desdeFrame, fps, config: { damping: 12, stiffness: 140, ...config } });
};

// Línea 4: el número "5" dibujado en SVG (no imagen IA), entra con resorte.
export const Numero5: React.FC<{ desdeFrame: number; color?: string }> = ({ desdeFrame, color = "#FF3B3B" }) => {
  const t = useEntrada(desdeFrame, { damping: 10, stiffness: 120 });
  const escala = interpolate(t, [0, 1], [0.3, 1]);
  const rotacion = interpolate(t, [0, 1], [-25, 0]);
  return (
    <svg width={260} height={320} viewBox="0 0 130 160" style={{ transform: `scale(${escala}) rotate(${rotacion}deg)`, opacity: t }}>
      <text
        x="65" y="130" textAnchor="middle" fontFamily="Montserrat, sans-serif" fontWeight={900}
        fontSize={160} fill={color} style={{ filter: `drop-shadow(0 0 24px ${color}aa)` }}
      >
        5
      </text>
    </svg>
  );
};

// Línea 6: silueta mínima de una figura de autoridad (terapeuta), chica y
// decorativa — no una escena ilustrada completa.
export const FiguraAutoridad: React.FC<{ desdeFrame: number; color?: string }> = ({ desdeFrame, color = "#3BA7FF" }) => {
  const t = useEntrada(desdeFrame);
  const y = interpolate(t, [0, 1], [30, 0]);
  return (
    <svg width={140} height={170} viewBox="0 0 70 85" style={{ opacity: t, transform: `translateY(${y}px)` }}>
      <circle cx="35" cy="22" r="14" fill={color} />
      <path d="M12 85 C12 55 20 44 35 44 C50 44 58 55 58 85 Z" fill={color} />
      <rect x="20" y="50" width="30" height="6" rx="3" fill="#000" opacity="0.35" />
    </svg>
  );
};

// Línea 14: anzuelo simple — "no es pasión, es un anzuelo".
export const Anzuelo: React.FC<{ desdeFrame: number; color?: string }> = ({ desdeFrame, color = "#FF9B3B" }) => {
  const t = useEntrada(desdeFrame, { damping: 9, stiffness: 160 });
  const balanceo = Math.sin(useCurrentFrame() / 6) * 4 * t;
  return (
    <svg
      width={150} height={220} viewBox="0 0 75 110"
      style={{ opacity: t, transform: `translateY(${interpolate(t, [0, 1], [-40, 0])}px) rotate(${balanceo}deg)`, transformOrigin: "37px 0px" }}
    >
      <line x1="37" y1="0" x2="37" y2="55" stroke={color} strokeWidth="4" />
      <path
        d="M37 55 C37 85 15 92 15 72 C15 60 28 58 32 68"
        fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
      />
    </svg>
  );
};

// Puzzle visual recurrente: una grieta que crece en una esquina, sin
// explicación verbal — aparece en las líneas 3, 10 y 15, no se resuelve
// hasta la Parte 3.
export const Grieta: React.FC<{ desdeFrame: number; intensidad: number }> = ({ desdeFrame, intensidad }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = spring({ frame: frame - desdeFrame, fps, config: { damping: 20, stiffness: 60 } });
  const largo = interpolate(t, [0, 1], [0, 1]) * intensidad;
  return (
    <svg
      width={220} height={340} viewBox="0 0 110 170"
      style={{ position: "absolute", top: 0, right: 0, opacity: interpolate(t, [0, 0.3, 1], [0, 0.9, 0.75]) }}
    >
      <path
        d={`M110 0 L${110 - 38 * largo} ${58 * largo} L${110 - 20 * largo} ${95 * largo} L${110 - 55 * largo} ${150 * largo}`}
        fill="none" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round"
        style={{ filter: "drop-shadow(0 0 6px rgba(255,255,255,0.7))" }}
      />
      <path
        d={`M${110 - 38 * largo} ${58 * largo} L${110 - 14 * largo} ${70 * largo}`}
        fill="none" stroke="#FFFFFF" strokeWidth="1.8" strokeLinecap="round" opacity={0.8}
      />
    </svg>
  );
};
