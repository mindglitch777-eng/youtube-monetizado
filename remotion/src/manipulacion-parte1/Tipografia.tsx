import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { LineaTimeline } from "./tipos";

// Tipografía cinética — remaster (Fase B) sobre el análisis de las 5
// referencias: nunca la MISMA oración completa que el subtítulo de abajo
// al mismo tiempo (esa era la capa base permanente y sigue mostrando la
// línea entera; el texto grande de acá SOLO muestra la palabra/frase
// clave). Jerarquía de tamaño fija en todo el video — nunca un tamaño
// arbitrario por fuera de estos tres:
export const TAMANOS = { HOOK: 148, REVELACION: 100, NARRATIVO: 46 };

export const framePalabra = (linea: LineaTimeline, desdeFrameLinea: number, fps: number, indice: number) =>
  desdeFrameLinea + Math.round(linea.palabras[indice].inicio * fps);

export const indiceDePalabra = (linea: LineaTimeline, coincide: (texto: string) => boolean) =>
  linea.palabras.findIndex((p) => coincide(p.texto.toLowerCase().replace(/[^a-z']/g, "")));

const useResorte = (desdeFrame: number, config?: Parameters<typeof spring>[0]["config"]) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - desdeFrame, fps, config: { damping: 14, stiffness: 130, ...config } });
};

// Réplica del "glitch" de aberración cromática que usa el Video 4 de
// referencia en sus números/palabras de impacto: dos copias fantasma
// (rojo/cian) que arrancan separadas y colapsan sobre el texto real en
// ~6 frames.
const Glitch: React.FC<{ texto: string; frame: number; desdeFrame: number; estilo: React.CSSProperties }> = ({
  texto,
  frame,
  desdeFrame,
  estilo,
}) => {
  const offset = interpolate(frame - desdeFrame, [0, 7], [10, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (offset < 0.4) return null;
  return (
    <>
      <div style={{ ...estilo, position: "absolute", inset: 0, color: "#FF3B3B", opacity: 0.65, mixBlendMode: "screen", transform: `${estilo.transform} translateX(${-offset}px)` }}>
        {texto}
      </div>
      <div style={{ ...estilo, position: "absolute", inset: 0, color: "#3BA7FF", opacity: 0.65, mixBlendMode: "screen", transform: `${estilo.transform} translateX(${offset}px)` }}>
        {texto}
      </div>
    </>
  );
};

// Auto-ajuste: una palabra/frase larga a tamaño HOOK/REVELACIÓN se sale del
// cuadro con whiteSpace:nowrap — nunca se recorta, se achica hasta entrar en
// el 92% del ancho (la jerarquía de tamaños sigue siendo la misma, esto es
// solo el límite físico de la pantalla).
const useTamanoAjustado = (texto: string, tamano: number) => {
  const { width } = useVideoConfig();
  const anchoDisponible = width * 0.86;
  const anchoEstimado = texto.length * tamano * 0.78;
  return anchoEstimado > anchoDisponible ? tamano * (anchoDisponible / anchoEstimado) : tamano;
};

type Entrada = "escala" | "rotacion";

// Primitiva reusable de "palabra/frase clave": entrada agresiva (golpe de
// escala grande->chico, o golpe de rotación), nunca fade+resorte suave
// solamente. Varía de ángulo/posición según `rotacionReposo` (0 =
// horizontal, ±90 = vertical, valores intermedios = diagonal).
export const TextoImpacto: React.FC<{
  texto: string;
  desdeFrame: number;
  tamano?: number;
  color?: string;
  rotacionReposo?: number;
  entrada?: Entrada;
  glitch?: boolean;
}> = ({ texto, desdeFrame, tamano = TAMANOS.REVELACION, color = "#FFFFFF", rotacionReposo = 0, entrada = "escala", glitch = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = spring({ frame: frame - desdeFrame, fps, config: { damping: 12, stiffness: 250 } });
  const escala = entrada === "escala" ? interpolate(t, [0, 1], [2.2, 1]) : interpolate(t, [0, 1], [0.6, 1]);
  const rotacionInicial = rotacionReposo + (rotacionReposo >= 0 ? 32 : -32);
  const rotacion = entrada === "rotacion" ? interpolate(t, [0, 1], [rotacionInicial, rotacionReposo]) : rotacionReposo;
  const opacidad = interpolate(t, [0, 1], [0, 1], { extrapolateRight: "clamp" });
  const tamanoFinal = useTamanoAjustado(texto, tamano);

  const estilo: React.CSSProperties = {
    fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: tamanoFinal, lineHeight: 1.05,
    textAlign: "center", color, textTransform: "uppercase", whiteSpace: "nowrap",
    transform: `scale(${escala}) rotate(${rotacion}deg)`,
    textShadow: `0 0 44px ${color}66, 0 10px 26px rgba(0,0,0,0.85)`,
  };

  return (
    <div style={{ position: "relative" }}>
      {glitch && <Glitch texto={texto} frame={frame} desdeFrame={desdeFrame} estilo={estilo} />}
      <div style={{ ...estilo, opacity: opacidad }}>{texto}</div>
    </div>
  );
};

// Jerarquía de dos niveles (el patrón dominante de las referencias: frase
// de contexto chica + palabra/frase clave grande) — contexto entra
// primero y se queda quieto; el keyword pega el golpe unos frames después.
export const DosNiveles: React.FC<{
  contexto: string;
  keyword: string;
  desdeFrame: number;
  color?: string;
  rotacion?: number;
  entrada?: Entrada;
  glitch?: boolean;
  tamanoKeyword?: number;
}> = ({ contexto, keyword, desdeFrame, color = "#FFFFFF", rotacion = 0, entrada = "escala", glitch = false, tamanoKeyword = TAMANOS.REVELACION }) => {
  const t = useResorte(desdeFrame, { damping: 18, stiffness: 200 });
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
      <div
        style={{
          fontFamily: "Montserrat, sans-serif", fontWeight: 700, fontSize: TAMANOS.NARRATIVO, color: "rgba(255,255,255,0.75)",
          textTransform: "uppercase", letterSpacing: 1, opacity: interpolate(t, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(t, [0, 1], [16, 0])}px)`,
        }}
      >
        {contexto}
      </div>
      <TextoImpacto texto={keyword} desdeFrame={desdeFrame + 6} tamano={tamanoKeyword} color={color} rotacionReposo={rotacion} entrada={entrada} glitch={glitch} />
    </div>
  );
};

// Línea 2: 3 palabras clave (partner / friend / family) entran una por vez
// — la anterior se apaga cuando entra la siguiente, nunca las 3 juntas
// formando la oración completa — cada una con su propio glow de color.
const COLORES_GLOW = ["#FF3B3B", "#3BA7FF", "#FF9B3B"];
export const PalabrasConGlow: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const claves = ["partner", "friend", "family"];
  const indices = claves.map((c) => indiceDePalabra(linea, (tx) => tx.includes(c))).filter((i) => i >= 0);
  return (
    <div style={{ position: "relative", width: "90%", height: 180, display: "flex", alignItems: "center", justifyContent: "center" }}>
      {indices.map((iPalabra, orden) => {
        const desde = framePalabra(linea, desdeFrameLinea, fps, iPalabra);
        const siguiente = orden + 1 < indices.length ? framePalabra(linea, desdeFrameLinea, fps, indices[orden + 1]) : desde + fps * 2;
        const t = spring({ frame: frame - desde, fps, config: { damping: 10, stiffness: 240 } });
        const salida = interpolate(frame, [siguiente - 3, siguiente], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const color = COLORES_GLOW[orden % COLORES_GLOW.length];
        if (frame < desde - 2) return null;
        return (
          <span
            key={iPalabra}
            style={{
              position: "absolute", fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: TAMANOS.REVELACION,
              color, textTransform: "uppercase",
              textShadow: `0 0 20px ${color}, 0 0 60px ${color}, 0 0 110px ${color}, 0 6px 18px rgba(0,0,0,0.8)`,
              opacity: t * salida, transform: `scale(${interpolate(t, [0, 1], [1.7, 1])})`,
            }}
          >
            {linea.palabras[iPalabra].texto.replace(/[.,]/g, "")}
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
// tamaño REVELACIÓN, va con <Contador/> arriba.
export const NombreTactica: React.FC<{ texto: string; desdeFrame: number; color: string }> = ({ texto, desdeFrame, color }) => (
  <TextoImpacto texto={texto} desdeFrame={desdeFrame} tamano={TAMANOS.REVELACION} color={color} entrada="escala" glitch />
);

// Línea 7: gancho de retención — dos niveles + flash de color momentáneo.
export const TextoGanchoRetencion: React.FC<{ contexto: string; keyword: string; desdeFrame: number }> = ({ contexto, keyword, desdeFrame }) => {
  const frame = useCurrentFrame();
  const flash = interpolate(frame - desdeFrame, [0, 4, 14], [1, 0, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "relative", width: "92%" }}>
      <DosNiveles contexto={contexto} keyword={keyword} desdeFrame={desdeFrame} color="#FFD83D" rotacion={-9} entrada="rotacion" />
      <div style={{ position: "absolute", inset: -80, background: "#FF3B3B", opacity: flash * 0.55, mixBlendMode: "screen" }} />
    </div>
  );
};

// Línea 9/13: título mínimo sobre un clip real (no compite con el subtítulo
// base, va arriba del clip como refuerzo del punto) — frase corta, no la
// oración completa.
export const RefuerzoSobreClip: React.FC<{ texto: string; desdeFrame: number; color: string }> = ({ texto, desdeFrame, color }) => {
  const t = useResorte(desdeFrame);
  return (
    <div
      style={{
        position: "absolute", top: 150, left: "50%", transform: `translateX(-50%) translateY(${interpolate(t, [0, 1], [-20, 0])}px)`,
        opacity: t, padding: "12px 30px", borderLeft: `6px solid ${color}`, background: "rgba(0,0,0,0.6)",
      }}
    >
      <span style={{ fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: 34, color: "#FFFFFF", textTransform: "uppercase", letterSpacing: 1 }}>
        {texto}
      </span>
    </div>
  );
};

// Línea 10: 3 frases citadas, una por una, rápido, tipografía de cita.
export const CitasSecuenciales: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
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
// 3 veces, cada una con su propio golpe. El tercer "control" es el más
// grande/fuerte.
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
            fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: TAMANOS.NARRATIVO + 8, color: "rgba(255,255,255,0.55)",
            position: "relative", opacity: interpolate(tachado, [0, 1], [1, 0.35]), textTransform: "uppercase",
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
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
        {indicesControl.map((iPalabra, orden) => {
          const desde = framePalabra(linea, desdeFrameLinea, fps, iPalabra);
          const t = spring({ frame: frame - desde, fps, config: { damping: 8, stiffness: 260 } });
          const tamano = TAMANOS.REVELACION - 40 + orden * 22; // el tercero, el más fuerte, llega a tamaño REVELACIÓN
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

// Línea 15: dos niveles + "trap" con efecto de escala que se contrae,
// entrada diagonal.
export const TextoConContraccion: React.FC<{ linea: LineaTimeline; desdeFrameLinea: number }> = ({ linea, desdeFrameLinea }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = useResorte(desdeFrameLinea, { damping: 16, stiffness: 190 });
  const iTrap = indiceDePalabra(linea, (tx) => tx.includes("trap"));
  const desdeTrap = iTrap >= 0 ? framePalabra(linea, desdeFrameLinea, fps, iTrap) : desdeFrameLinea;
  const contraccion = interpolate(frame, [desdeTrap, desdeTrap + 10, desdeTrap + 22], [1, 0.5, 1.15], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
      <div
        style={{
          fontFamily: "Montserrat, sans-serif", fontWeight: 700, fontSize: TAMANOS.NARRATIVO, color: "rgba(255,255,255,0.75)",
          textTransform: "uppercase", letterSpacing: 1, opacity: interpolate(t, [0, 1], [0, 1]),
        }}
      >
        THE HARDER IT CAN
      </div>
      <div
        style={{
          fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: TAMANOS.REVELACION, color: "#FFFFFF",
          transform: `rotate(-8deg) scale(${contraccion})`, textShadow: "0 0 34px #FF3B3B, 0 10px 26px rgba(0,0,0,0.85)",
          opacity: interpolate(t, [0, 1], [0, 1]),
        }}
      >
        TRAP YOU
      </div>
    </div>
  );
};

// Línea 16: MÁS LENTA que el resto, blur de entrada suave — contraste de
// ritmo deliberado antes del cierre. Sigue siendo frase corta, no la
// oración completa.
export const TextoLento: React.FC<{ texto: string; desdeFrame: number }> = ({ texto, desdeFrame }) => {
  const t = useResorte(desdeFrame, { damping: 26, stiffness: 40 });
  const blur = interpolate(t, [0, 1], [18, 0], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: TAMANOS.REVELACION - 20, lineHeight: 1.2,
        textAlign: "center", color: "rgba(255,255,255,0.92)", width: "80%", textTransform: "uppercase",
        opacity: interpolate(t, [0, 1], [0, 1]), filter: `blur(${blur}px)`,
      }}
    >
      {texto}
    </div>
  );
};

// Línea 17: corte seco, "That's Part 2." — SIN resorte ni escala de entrada
// (aparece de golpe, ya asentado, a propósito), solo el glitch cromático
// como acento momentáneo.
export const TextoCorteSeco: React.FC<{ texto: string }> = ({ texto }) => {
  const frame = useCurrentFrame();
  const tamano = useTamanoAjustado(texto, TAMANOS.REVELACION + 8);
  const estilo: React.CSSProperties = {
    fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: tamano, color: "#FFFFFF",
    textAlign: "center", whiteSpace: "nowrap",
  };
  return (
    <div style={{ position: "relative" }}>
      <Glitch texto={texto} frame={frame} desdeFrame={0} estilo={estilo} />
      <div style={estilo}>{texto}</div>
    </div>
  );
};
