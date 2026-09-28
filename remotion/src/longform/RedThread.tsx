import React, { useMemo } from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export type PuntoHilo = { startFrame: number; count: number; state: "tension" | "snap" };

// Motivo visual recurrente: hilos rojos que se acumulan un capítulo a la
// vez y se cortan en la "primera grieta" — nunca se explica con palabras
// (sección 5 del PACK, "Hilo rojo"). Vive en el nivel superior de
// LongForm.tsx (no por-toma), busca la toma activa por frame absoluto.
export const RedThread: React.FC<{ puntos: PuntoHilo[] }> = ({ puntos }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const activo = useMemo(() => {
    let actual = puntos[0];
    for (const p of puntos) {
      if (p.startFrame <= frame) actual = p;
      else break;
    }
    return actual;
  }, [puntos, frame]);

  // Frame en el que cada hilo (1..5) aparece por primera vez, para animar
  // su entrada individualmente aunque los demás ya estén asentados.
  const frameDeAparicion = useMemo(() => {
    const mapa: Record<number, number> = {};
    for (const p of puntos) {
      for (let i = 1; i <= p.count; i++) {
        if (mapa[i] === undefined) mapa[i] = p.startFrame;
      }
    }
    return mapa;
  }, [puntos]);

  // Punto justo antes de un snap (para saber cuántos hilos había antes de
  // cortarse) y frame en que arrancó el snap actual.
  const { conteoPreSnap, snapFrame } = useMemo(() => {
    let anterior = 0;
    for (const p of puntos) {
      if (p.state === "snap") return { conteoPreSnap: anterior, snapFrame: p.startFrame };
      anterior = p.count;
    }
    return { conteoPreSnap: 0, snapFrame: -1 };
  }, [puntos]);

  const enSnap = activo.state === "snap" && snapFrame >= 0 && frame - snapFrame < 10;
  const conteo = enSnap ? conteoPreSnap : activo.count;
  if (conteo <= 0) return null;

  const retraccion = enSnap ? interpolate(frame - snapFrame, [0, 10], [0, 1], { extrapolateRight: "clamp" }) : 0;

  return (
    <svg width={width} height={height} style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
      <defs>
        <filter id="hiloGlow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {Array.from({ length: conteo }, (_, i) => i + 1).map((n) => {
        const apareceEn = frameDeAparicion[n] ?? 0;
        const entrada = spring({ frame: frame - apareceEn, fps, config: { damping: 16, stiffness: 90 } });
        const sag = 60 - 9 * conteo;
        const y = height - 46 - n * 5;
        const anchoVisible = interpolate(entrada, [0, 1], [0, width], { extrapolateRight: "clamp" });
        const caida = enSnap ? interpolate(retraccion, [0, 1], [0, 90]) : 0;
        const opacidadSnap = enSnap ? interpolate(retraccion, [0, 1], [1, 0]) : 1;
        return (
          <path
            key={n}
            d={`M 0 ${y} Q ${width / 2} ${y + sag + caida} ${anchoVisible} ${y}`}
            fill="none" stroke="#ff2d55" strokeWidth={3} strokeLinecap="round" opacity={opacidadSnap}
            filter="url(#hiloGlow)"
          />
        );
      })}
    </svg>
  );
};
