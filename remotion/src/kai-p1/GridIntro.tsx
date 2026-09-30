import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";

const ZOOM_FRAMES = 10; // "rápido" — ~0.33s a 30fps

// Etiquetas de cada panel de la grilla (imagen kai-p1-01.png: 2x2 + 1
// franja abajo). Posiciones estimadas sobre esa imagen en particular.
const ETIQUETAS: Array<{ texto: string; left: string; top: string }> = [
  { texto: "LOVE BOMBING", left: "27%", top: "35%" },
  { texto: "GUILT TRAP", left: "73%", top: "35%" },
  { texto: "SILENT TREATMENT", left: "27%", top: "60%" },
  { texto: "GASLIGHTING", left: "73%", top: "60%" },
  { texto: "THE SWITCH", left: "50%", top: "84%" },
];

// Centro del panel superior-izquierdo (love bombing), destino del zoom.
const DESTINO_ZOOM = { x: 27, y: 23 };

const Etiqueta: React.FC<{ texto: string; left: string; top: string }> = ({ texto, left, top }) => (
  <div
    style={{
      position: "absolute", left, top, transform: "translate(-50%, -50%)",
      fontFamily: "Inter, sans-serif", fontWeight: 800, fontSize: 26, color: "#FFFFFF",
      WebkitTextStroke: "2.5px #000000", paintOrder: "stroke fill", textAlign: "center", whiteSpace: "nowrap",
    }}
  >
    {texto}
  </div>
);

// Gancho visual de apertura de la línea 4 (regla del .md): grilla completa
// con título + etiquetas, zoom rápido al panel de love bombing al llegar
// "Today, we start with the first one", corte a ese panel a pantalla
// completa (imagen aparte, sin recortar la grilla).
export const GridIntro: React.FC<{
  archivoGrid: string; archivoPanel: string; triggerFrame: number;
}> = ({ archivoGrid, archivoPanel, triggerFrame }) => {
  const frame = useCurrentFrame();

  if (frame >= triggerFrame + ZOOM_FRAMES) {
    return (
      <AbsoluteFill style={{ backgroundColor: "#000000" }}>
        <Img src={staticFile(`kai-p1-images/${archivoPanel}`)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    );
  }

  const avanceZoom = interpolate(frame, [triggerFrame, triggerFrame + ZOOM_FRAMES], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const escala = interpolate(avanceZoom, [0, 1], [1, 2.6]);
  const originX = interpolate(avanceZoom, [0, 1], [50, DESTINO_ZOOM.x]);
  const originY = interpolate(avanceZoom, [0, 1], [50, DESTINO_ZOOM.y]);
  const opacidadUi = interpolate(avanceZoom, [0, 0.5], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000", overflow: "hidden" }}>
      <Img
        src={staticFile(`kai-p1-images/${archivoGrid}`)}
        style={{
          width: "100%", height: "100%", objectFit: "cover",
          transform: `scale(${escala})`, transformOrigin: `${originX}% ${originY}%`,
        }}
      />
      <AbsoluteFill style={{ opacity: opacidadUi }}>
        <div
          style={{
            position: "absolute", top: "3%", left: 0, right: 0, textAlign: "center",
            fontFamily: "Anton, sans-serif", fontSize: 46, color: "#FFFFFF",
            WebkitTextStroke: "3px #000000", paintOrder: "stroke fill", padding: "0 6%", lineHeight: 1.1,
          }}
        >
          5 WAYS LOVE CAN BE A TRAP
        </div>
        {ETIQUETAS.map((e) => (
          <Etiqueta key={e.texto} {...e} />
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
