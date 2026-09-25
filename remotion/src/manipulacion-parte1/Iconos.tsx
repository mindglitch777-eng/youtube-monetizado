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
// decorativa — no una escena ilustrada completa. Nunca queda estática: leve
// rotación/balanceo continuo, igual que los íconos de los videos de
// referencia (nada se queda quieto del todo).
export const FiguraAutoridad: React.FC<{ desdeFrame: number; color?: string }> = ({ desdeFrame, color = "#3BA7FF" }) => {
  const frame = useCurrentFrame();
  const t = useEntrada(desdeFrame);
  const y = interpolate(t, [0, 1], [30, 0]);
  const idle = Math.sin(frame / 20) * 3;
  return (
    <svg
      width={190} height={230} viewBox="0 0 70 85"
      style={{ opacity: t, transform: `translateY(${y}px) rotate(${idle}deg)`, filter: `drop-shadow(0 0 22px ${color}88)` }}
    >
      <circle cx="35" cy="22" r="14" fill={color} />
      <path d="M12 85 C12 55 20 44 35 44 C50 44 58 55 58 85 Z" fill={color} />
      <rect x="20" y="50" width="30" height="6" rx="3" fill="#000" opacity="0.35" />
    </svg>
  );
};

// Línea 14: anzuelo — forma clásica de gancho de pesca (vara recta + curva
// en J + púa), no ambigua a tamaño chico. "No es pasión, es un anzuelo".
// Balanceo continuo (idle) además del balanceo de entrada.
export const Anzuelo: React.FC<{ desdeFrame: number; color?: string }> = ({ desdeFrame, color = "#FF9B3B" }) => {
  const frame = useCurrentFrame();
  const t = useEntrada(desdeFrame, { damping: 9, stiffness: 160 });
  const balanceo = Math.sin(frame / 6) * 4 * t + Math.sin(frame / 25) * 3;
  return (
    <svg
      width={170} height={260} viewBox="0 0 100 150"
      style={{
        opacity: t, transform: `translateY(${interpolate(t, [0, 1], [-40, 0])}px) rotate(${balanceo}deg)`,
        transformOrigin: "50px 0px", filter: `drop-shadow(0 0 22px ${color}aa)`,
      }}
    >
      {/* Vara recta colgando */}
      <line x1="50" y1="0" x2="50" y2="72" stroke={color} strokeWidth="9" strokeLinecap="round" />
      {/* Curva en J del anzuelo */}
      <path
        d="M50 72 C50 104 26 112 20 92 C16 78 28 74 34 84"
        fill="none" stroke={color} strokeWidth="9" strokeLinecap="round"
      />
      {/* Púa (la puntita que engancha) */}
      <path d="M34 84 L44 80" fill="none" stroke={color} strokeWidth="7" strokeLinecap="round" />
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
  const pulso = 1 + Math.sin(frame / 10) * 0.04;
  const largo = interpolate(t, [0, 1], [0, 1]) * intensidad * pulso;
  return (
    <svg
      width={340} height={460} viewBox="0 0 110 170"
      style={{ position: "absolute", top: 0, right: 0, opacity: interpolate(t, [0, 0.3, 1], [0, 1, 0.92]) }}
    >
      <path
        d={`M110 0 L${110 - 38 * largo} ${58 * largo} L${110 - 20 * largo} ${95 * largo} L${110 - 55 * largo} ${150 * largo}`}
        fill="none" stroke="#FFFFFF" strokeWidth="4" strokeLinecap="round"
        style={{ filter: "drop-shadow(0 0 14px rgba(255,255,255,0.95))" }}
      />
      <path
        d={`M${110 - 38 * largo} ${58 * largo} L${110 - 14 * largo} ${70 * largo}`}
        fill="none" stroke="#FFFFFF" strokeWidth="2.6" strokeLinecap="round" opacity={0.85}
      />
      <path
        d={`M${110 - 20 * largo} ${95 * largo} L${110 + 4 * largo} ${112 * largo}`}
        fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" opacity={0.7}
      />
    </svg>
  );
};
