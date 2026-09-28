// Movimientos de cámara sobre imágenes/clips (sección 5 del PACK). Fuente
// 1024² escalada ×1,875 (1920×1920), la ventana visible es 1080 de alto
// (56%). Easing cúbico in-out, recorrido vertical total ≤ ±260px.
import { Easing, interpolate } from "remotion";

export type Motion =
  | "push_in" | "pull_out" | "pan_up" | "pan_down"
  | "push_in_left" | "push_in_right" | "pull_out_up";

const EASE = Easing.inOut(Easing.cubic);

export function transformDeMovimiento(motion: Motion, avance: number): { transform: string; transformOrigin: string } {
  const t = interpolate(avance, [0, 1], [0, 1], { easing: EASE, extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  switch (motion) {
    case "push_in":
      return { transform: `scale(${interpolate(t, [0, 1], [1.0, 1.12])})`, transformOrigin: "50% 50%" };
    case "pull_out":
      return { transform: `scale(${interpolate(t, [0, 1], [1.12, 1.0])})`, transformOrigin: "50% 50%" };
    case "pan_up": {
      const y = interpolate(t, [0, 1], [130, -130]);
      return { transform: `translateY(${y}px) scale(1.06)`, transformOrigin: "50% 50%" };
    }
    case "pan_down": {
      const y = interpolate(t, [0, 1], [-130, 130]);
      return { transform: `translateY(${y}px) scale(1.06)`, transformOrigin: "50% 50%" };
    }
    case "push_in_left":
      return { transform: `scale(${interpolate(t, [0, 1], [1.0, 1.12])})`, transformOrigin: "38% 50%" };
    case "push_in_right":
      return { transform: `scale(${interpolate(t, [0, 1], [1.0, 1.12])})`, transformOrigin: "62% 50%" };
    case "pull_out_up": {
      const focoY = interpolate(t, [0, 1], [62, 50]);
      return { transform: `scale(${interpolate(t, [0, 1], [1.12, 1.0])})`, transformOrigin: `50% ${focoY}%` };
    }
    default:
      return { transform: "scale(1.05)", transformOrigin: "50% 50%" };
  }
}
