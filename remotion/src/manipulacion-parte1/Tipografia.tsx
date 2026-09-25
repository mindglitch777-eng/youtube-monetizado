import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { LineaTimeline } from "./tipos";

// Tipografía cinética: nunca texto estático. Cada tratamiento tiene su
// propia entrada animada (resorte, blur, escala) — ver RULES.md, sección
// Tipografía. Los helpers acá abajo convierten los tiempos de palabra
// (relativos a la línea) en frames absolutos, para sincronizar cada
// micro-animación con la voz real.

export const framePalabra = (linea: LineaTimeline, desdeFrameLinea: number, fps: number, indice: number) =>
  desdeFrameLinea + Math.round(linea.palabras[indice].inicio * fps);

export const indiceDePalabra = (linea: LineaTimeline, coincide: (texto: string) => boolean) =>
  linea.palabras.findIndex((p) => coincide(p.texto.toLowerCase().replace(/[^a-z']/g, "")));

const useResorte = (desdeFrame: number, config?: Parameters<typeof spring>[0]["config"]) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - desdeFrame, fps, config: { damping: 14, stiffness: 130, ...config } });
};

// Línea 1: hook — tipografía cinética enorme, entrada blur+resorte, fondo
// negro puro con glow sutil.
export const TextoHook: React.FC<{ texto: string; desdeFrame: number }> = ({ texto, desdeFrame }) => {
  const t = useResorte(desdeFrame, { damping: 11, stiffness: 110 });
  const escala = interpolate(t, [0, 1], [0.55, 1]);
  const blur = interpolate(t, [0, 1], [22, 0], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 128, lineHeight: 1.05,
        textAlign: "center", color: "#FFFFFF", width: "88%",
        textShadow: "0 0 60px rgba(255,255,255,0.35), 0 10px 30px rgba(0,0,0,0.8)",
        transform: `scale(${escala})`, filter: `blur(${blur}px)`, opacity: interpolate(t, [0, 1], [0, 1]),
      }}
    >
      {texto}
    </div>
  );
};

// Línea 2: cada palabra entra por separado, con su propio glow de color.
const COLORES_GLOW = ["#FF3B3B", "#3BA7FF", "#FF9B3B", "#FF3B3B", "#3BA7FF", "#FF9B3B", "#FFFFFF", "#FF3B3B", "#3BA7FF"];
export const PalabrasConGlow: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0.3em", width: "90%" }}>
      {linea.palabras.map((p, i) => {
        const desde = framePalabra(linea, desdeFrameLinea, fps, i);
        const t = spring({ frame: frame - desde, fps, config: { damping: 11, stiffness: 170 } });
        const color = COLORES_GLOW[i % COLORES_GLOW.length];
        return (
          <span
            key={i}
            style={{
              fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 78, color: "#FFFFFF",
              textShadow: `0 0 26px ${color}, 0 6px 18px rgba(0,0,0,0.7)`,
              opacity: t, transform: `translateY(${interpolate(t, [0, 1], [30, 0])}px) scale(${interpolate(t, [0, 1], [0.7, 1])})`,
            }}
          >
            {p.texto}
          </span>
        );
      })}
    </div>
  );
};

// Línea 5: banner fijo arriba de pantalla, tipografía distinta a los
// subtítulos, se mantiene varias líneas (lo controla el padre con su rango
// de frames, este componente solo se anima al entrar).
export const BannerSuperior: React.FC<{ texto: string; desdeFrame: number }> = ({ texto, desdeFrame }) => {
  const t = useResorte(desdeFrame, { damping: 16, stiffness: 160 });
  return (
    <div
      style={{
        position: "absolute", top: 90, left: "50%", transform: `translateX(-50%) translateY(${interpolate(t, [0, 1], [-40, 0])}px)`,
        opacity: t, background: "rgba(255,255,255,0.08)", border: "2px solid rgba(255,255,255,0.5)",
        borderRadius: 999, padding: "16px 42px", backdropFilter: "blur(6px)",
      }}
    >
      <span style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 700, fontSize: 34, letterSpacing: 2, color: "#FFFFFF", textTransform: "uppercase" }}>
        {texto}
      </span>
    </div>
  );
};

// Líneas 8/12: banner + contador "N/5" con resorte.
export const Contador: React.FC<{ n: number; desdeFrame: number; color: string }> = ({ n, desdeFrame, color }) => {
  const t = useResorte(desdeFrame, { damping: 9, stiffness: 200 });
  return (
    <div
      style={{
        position: "absolute", top: 210, left: "50%", transform: `translateX(-50%) scale(${interpolate(t, [0, 1], [0.4, 1])})`,
        opacity: t, display: "flex", alignItems: "baseline", gap: 4,
      }}
    >
      <span style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 64, color }}>{n}</span>
      <span style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 700, fontSize: 34, color: "rgba(255,255,255,0.6)" }}>/5</span>
    </div>
  );
};

// Líneas 8/12: nombre de la táctica ("GASLIGHTING" / "LOVE BOMBING"),
// revelación con blur+impacto, va con <Contador/> arriba.
export const NombreTactica: React.FC<{ texto: string; desdeFrame: number; color: string }> = ({ texto, desdeFrame, color }) => {
  const t = useResorte(desdeFrame, { damping: 12, stiffness: 150 });
  const blur = interpolate(t, [0, 1], [16, 0], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 92, textAlign: "center",
        color: "#FFFFFF", textTransform: "uppercase", letterSpacing: 1,
        textShadow: `0 0 40px ${color}, 0 10px 26px rgba(0,0,0,0.8)`,
        opacity: interpolate(t, [0, 1], [0, 1]), filter: `blur(${blur}px)`,
        transform: `scale(${interpolate(t, [0, 1], [0.7, 1])})`,
      }}
    >
      {texto}
    </div>
  );
};

// Línea 7: gancho de retención — tipografía de impacto, flash de color
// momentáneo, más grande que el resto.
export const TextoGanchoRetencion: React.FC<{ texto: string; desdeFrame: number }> = ({ texto, desdeFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = useResorte(desdeFrame, { damping: 10, stiffness: 150 });
  const flash = interpolate(frame - desdeFrame, [0, 4, 14], [1, 0, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "relative", width: "92%", textAlign: "center" }}>
      <div
        style={{
          fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 96, lineHeight: 1.1,
          color: "#FFFFFF", opacity: interpolate(t, [0, 1], [0, 1]),
          transform: `scale(${interpolate(t, [0, 1], [1.25, 1])})`,
          textShadow: "0 10px 30px rgba(0,0,0,0.85)",
        }}
      >
        {texto}
      </div>
      <div style={{ position: "absolute", inset: -60, background: "#FF3B3B", opacity: flash * 0.55, mixBlendMode: "screen" }} />
    </div>
  );
};

// Línea 9/13: título mínimo sobre un clip real (no compite con el subtítulo
// base, va arriba del clip como refuerzo del punto).
export const RefuerzoSobreClip: React.FC<{ texto: string; desdeFrame: number; color: string }> = ({ texto, desdeFrame, color }) => {
  const t = useResorte(desdeFrame);
  return (
    <div
      style={{
        position: "absolute", top: 130, left: "50%", transform: `translateX(-50%) translateY(${interpolate(t, [0, 1], [-20, 0])}px)`,
        opacity: t, padding: "10px 28px", borderLeft: `6px solid ${color}`, background: "rgba(0,0,0,0.55)",
      }}
    >
      <span style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: 30, color: "#FFFFFF", textTransform: "uppercase", letterSpacing: 1 }}>
        {texto}
      </span>
    </div>
  );
};

// Línea 10: 3 frases citadas, una por una, rápido, tipografía de cita.
export const CitasSecuenciales: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // Cada cita es un tramo entre comillas simples en el texto narrado.
  const citas = linea.texto.match(/'[^']+'/g) ?? [linea.texto];
  const palabrasPorCita = Math.ceil(linea.palabras.length / citas.length);
  return (
    <div style={{ position: "relative", width: "88%", height: 200, textAlign: "center" }}>
      {citas.map((cita, i) => {
        const iPalabra = Math.min(i * palabrasPorCita, linea.palabras.length - 1);
        const desde = framePalabra(linea, desdeFrameLinea, fps, iPalabra);
        const siguienteDesde = i + 1 < citas.length
          ? framePalabra(linea, desdeFrameLinea, fps, Math.min((i + 1) * palabrasPorCita, linea.palabras.length - 1))
          : desde + fps * 3;
        const t = spring({ frame: frame - desde, fps, config: { damping: 13, stiffness: 190 } });
        const salida = interpolate(frame, [siguienteDesde - 3, siguienteDesde], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        if (frame < desde - 2) return null;
        return (
          <div
            key={i}
            style={{
              position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontStyle: "italic", fontSize: 68,
              color: "#FFD83D", opacity: t * salida, transform: `scale(${interpolate(t, [0, 1], [0.75, 1])})`,
              textShadow: "0 8px 24px rgba(0,0,0,0.8)",
            }}
          >
            {cita}
          </div>
        );
      })}
    </div>
  );
};

// Línea 11 — regla de tres: "confusion" se tacha/desvanece, "control" entra
// 3 veces, cada una con su propio golpe (la cámara reacciona en el padre;
// acá solo la tipografía). El tercer "control" es el más grande/fuerte.
export const ReglaDeTresControl: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const iConfusion = indiceDePalabra(linea, (t) => t.includes("confusion"));
  const indicesControl = linea.palabras
    .map((p, i) => (p.texto.toLowerCase().includes("control") ? i : -1))
    .filter((i) => i >= 0);

  const desdeConfusion = iConfusion >= 0 ? framePalabra(linea, desdeFrameLinea, fps, iConfusion) : desdeFrameLinea;
  const tachado = interpolate(frame, [desdeConfusion + 6, desdeConfusion + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
      {iConfusion >= 0 && (
        <div
          style={{
            fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: 54, color: "rgba(255,255,255,0.55)",
            position: "relative", opacity: interpolate(tachado, [0, 1], [1, 0.35]),
          }}
        >
          confusion
          <div
            style={{
              position: "absolute", left: 0, right: 0, top: "50%", height: 6, background: "#FF3B3B",
              transform: `scaleX(${tachado})`, transformOrigin: "left", boxShadow: "0 0 14px #FF3B3B",
            }}
          />
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        {indicesControl.map((iPalabra, orden) => {
          const desde = framePalabra(linea, desdeFrameLinea, fps, iPalabra);
          const t = spring({ frame: frame - desde, fps, config: { damping: 8, stiffness: 260 } });
          const tamano = 58 + orden * 18; // el tercero, el más fuerte
          return (
            <span
              key={iPalabra}
              style={{
                fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: tamano, color: "#FF3B3B",
                opacity: t, transform: `scale(${interpolate(t, [0, 1], [1.6, 1])})`,
                textShadow: `0 0 ${30 + orden * 15}px #FF3B3B`,
              }}
            >
              CONTROL
            </span>
          );
        })}
      </div>
    </div>
  );
};

// Línea 15: tipografía cinética, "trap" con efecto de escala que se contrae.
export const TextoConContraccion: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = useResorte(desdeFrameLinea, { damping: 14 });
  const iTrap = indiceDePalabra(linea, (tx) => tx.includes("trap"));
  const desdeTrap = iTrap >= 0 ? framePalabra(linea, desdeFrameLinea, fps, iTrap) : desdeFrameLinea;
  const contraccion = interpolate(frame, [desdeTrap, desdeTrap + 10, desdeTrap + 22], [1, 0.55, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ width: "85%", textAlign: "center", opacity: interpolate(t, [0, 1], [0, 1]) }}>
      {linea.palabras.map((p, i) => (
        <span
          key={i}
          style={{
            fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 74, color: "#FFFFFF", margin: "0 0.12em",
            display: "inline-block", transform: i === iTrap ? `scale(${contraccion})` : undefined,
            textShadow: i === iTrap ? "0 0 30px #FF3B3B" : "0 8px 20px rgba(0,0,0,0.7)",
          }}
        >
          {p.texto}
        </span>
      ))}
    </div>
  );
};

// Línea 16: MÁS LENTA que el resto, blur de entrada suave — contraste de
// ritmo deliberado antes del cierre.
export const TextoLento: React.FC<{ texto: string; desdeFrame: number }> = ({ texto, desdeFrame }) => {
  const t = useResorte(desdeFrame, { damping: 26, stiffness: 40 });
  const blur = interpolate(t, [0, 1], [14, 0], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        fontFamily: "Montserrat, sans-serif", fontWeight: 700, fontSize: 68, lineHeight: 1.25,
        textAlign: "center", color: "rgba(255,255,255,0.92)", width: "80%",
        opacity: interpolate(t, [0, 1], [0, 1]), filter: `blur(${blur}px)`,
      }}
    >
      {texto}
    </div>
  );
};

// Línea 17: corte seco, "That's Part 2." — sin resorte, aparece de golpe a
// propósito (abrupto).
export const TextoCorteSeco: React.FC<{ texto: string }> = ({ texto }) => (
  <div style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 104, color: "#FFFFFF", textAlign: "center" }}>
    {texto}
  </div>
);
