import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ACENTOS } from "./Estilos";
import type { PlateData } from "./tipos";

const SERIF = "'Playfair Display', 'DM Serif Display', Georgia, serif";
const SANS = "Inter, -apple-system, sans-serif";

// Fondo animado de toda placa (N10: nunca negro plano) — degradado +
// franjas de luz difusas diagonales + resplandor radial del acento.
const FondoPlaca: React.FC<{ acento: string }> = ({ acento }) => {
  const frame = useCurrentFrame();
  const desplazo = (frame * 40) / 30; // ~40px/s a 30fps
  return (
    <AbsoluteFill style={{ background: "linear-gradient(160deg, #050505 0%, #0d0d12 100%)" }}>
      <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "screen" }}>
        <div
          style={{
            position: "absolute", inset: "-50%", background:
              `repeating-linear-gradient(115deg, transparent 0px, transparent 180px, ${acento} 180px, ${acento} 220px, transparent 220px, transparent 400px)`,
            transform: `translate(${desplazo % 400}px, ${desplazo % 300}px)`,
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 900px 600px at 50% 50%, ${acento}2e 0%, transparent 70%)`,
        }}
      />
    </AbsoluteFill>
  );
};

// Entrada escalonada palabra por palabra: resorte (damping 14, stiffness
// 120), blur 14->0, translateY 28->0.
const PalabraEscalonada: React.FC<{ texto: string; indiceGlobal: number; style: React.CSSProperties }> = ({
  texto,
  indiceGlobal,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const desde = Math.round(indiceGlobal * 0.07 * fps);
  const t = spring({ frame: frame - desde, fps, config: { damping: 14, stiffness: 120 } });
  const blur = interpolate(t, [0, 1], [14, 0], { extrapolateRight: "clamp" });
  const y = interpolate(t, [0, 1], [28, 0], { extrapolateRight: "clamp" });
  return (
    <span
      style={{
        ...style, display: "inline-block", margin: "0 0.16em",
        opacity: interpolate(t, [0, 1], [0, 1]), filter: `blur(${blur}px)`, transform: `translateY(${y}px)`,
      }}
    >
      {texto}
    </span>
  );
};

// Una línea completa dividida en palabras con stagger, contando el índice
// global de palabra a través de TODAS las líneas de la placa (para que el
// escalonado siga fluyendo entre líneas). `estatica` = ya estaba visible
// (para `list` con reveal_from: las líneas previas no vuelven a animar).
const Linea: React.FC<{ texto: string; contador: { i: number }; estatica: boolean; style: React.CSSProperties }> = ({
  texto,
  contador,
  estatica,
  style,
}) => (
  <div style={{ textAlign: "center" }}>
    {texto.split(" ").map((palabra, k) => {
      const indice = contador.i++;
      return estatica
        ? <span key={k} style={{ ...style, display: "inline-block", margin: "0 0.16em" }}>{palabra}</span>
        : <PalabraEscalonada key={k} texto={palabra} indiceGlobal={indice} style={style} />;
    })}
  </div>
);

export const Plate: React.FC<{ data: PlateData; duracionFrames: number }> = ({ data, duracionFrames }) => {
  const frame = useCurrentFrame();
  const acento = ACENTOS[data.accent] ?? ACENTOS.amber;
  const pushIn = interpolate(frame, [0, duracionFrames], [1.0, 1.04], { extrapolateRight: "clamp" });
  const salida = interpolate(frame, [duracionFrames - 6, duracionFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const contador = { i: 0 };

  const estiloLinea: React.CSSProperties = { fontFamily: SERIF, fontWeight: 800, color: "#FFFFFF", lineHeight: 1.08 };
  const estiloSub: React.CSSProperties = { fontFamily: SANS, fontWeight: 700, color: acento, letterSpacing: "0.15em", textTransform: "uppercase" };

  let tamanoLinea = 140;
  if (data.kind === "note") tamanoLinea = 64;
  if (data.kind === "list") tamanoLinea = 72;
  if (data.kind === "cta" || data.kind === "question") tamanoLinea = 105;
  if (data.kind === "end") tamanoLinea = 110;
  if (data.kind === "concept") tamanoLinea = 150;
  if (data.kind === "chapter") tamanoLinea = 128;

  return (
    <AbsoluteFill style={{ opacity: salida }}>
      <FondoPlaca acento={acento} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", transform: `scale(${pushIn})` }}>
        {data.kind === "chapter" && data.n !== undefined && (
          <div
            style={{
              position: "absolute", fontFamily: SERIF, fontWeight: 800, fontSize: 520, color: "#FFFFFF",
              opacity: 0.06, lineHeight: 1,
            }}
          >
            {data.n}
          </div>
        )}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18, zIndex: 1 }}>
          {data.kind === "chapter" && (
            <div style={{ ...estiloSub, fontSize: 34 }}>MOVE {data.n}</div>
          )}
          {data.kind === "list"
            ? data.lines.map((linea, i) => (
                <Linea
                  key={i}
                  texto={linea}
                  contador={contador}
                  estatica={data.reveal_from !== undefined && i < data.reveal_from}
                  style={{ ...estiloLinea, fontSize: tamanoLinea, color: data.reveal_from !== undefined && i >= data.reveal_from ? acento : "#FFFFFF" }}
                />
              ))
            : data.lines.map((linea, i) => (
                <Linea key={i} texto={linea} contador={contador} estatica={false} style={{ ...estiloLinea, fontSize: tamanoLinea }} />
              ))}
          {data.sub && data.kind !== "end" && <div style={{ ...estiloSub, fontSize: 26 }}>{data.sub}</div>}
          {data.kind === "end" && data.sub && (
            <div
              style={{
                marginTop: 12, padding: "14px 38px", borderRadius: 999, border: `2px solid ${acento}`,
                fontFamily: SANS, fontWeight: 800, fontSize: 30, color: acento, letterSpacing: "0.1em",
              }}
            >
              {data.sub}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
