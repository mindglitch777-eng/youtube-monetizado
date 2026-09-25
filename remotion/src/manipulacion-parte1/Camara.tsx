import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Cámara nunca estática: paneo + zoom lento y constante durante todo el
// short, más "golpes" de cámara (shake) puntuales en los momentos de
// impacto marcados (RULES.md, sección Cámara y tono visual). El desenfoque
// real de estos movimientos lo da CameraMotionBlur envolviendo todo el
// árbol visual en ManipulacionParte1.tsx — automáticamente más fuerte en
// los frames donde este transform cambia más rápido (los golpes).
export function useCamara(framesDeGolpe: number[]) {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const avance = frame / durationInFrames;
  const panX = interpolate(avance, [0, 1], [-22, 22]);
  const panY = interpolate(avance, [0, 1], [8, -8]);
  const zoom = interpolate(avance, [0, 1], [1, 1.09]);

  let shakeX = 0;
  let shakeRot = 0;
  let shakeZoom = 0;
  for (const golpe of framesDeGolpe) {
    const t = spring({ frame: frame - golpe, fps, config: { damping: 7, stiffness: 300 }, durationInFrames: 12 });
    const decaimiento = interpolate(frame - golpe, [0, 12], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    shakeX += Math.sin((frame - golpe) * 3) * 10 * t * decaimiento;
    shakeRot += Math.sin((frame - golpe) * 2.3) * 1.6 * t * decaimiento;
    shakeZoom += 0.045 * t * decaimiento;
  }

  return {
    transform: `translate(${panX + shakeX}px, ${panY}px) scale(${zoom + shakeZoom}) rotate(${shakeRot}deg)`,
  };
}
