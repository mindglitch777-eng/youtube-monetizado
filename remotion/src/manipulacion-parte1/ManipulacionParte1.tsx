import { CameraMotionBlur } from "@remotion/motion-blur";
import React, { useMemo } from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CapaSubtitulos } from "./CapaSubtitulos";
import { useCamara } from "./Camara";
import { Anzuelo, FiguraAutoridad, Grieta, Numero5 } from "./Iconos";
import {
  BannerSuperior,
  CitasSecuenciales,
  Contador,
  NombreTactica,
  PalabrasConGlow,
  ReglaDeTresControl,
  RefuerzoSobreClip,
  TextoConContraccion,
  TextoCorteSeco,
  TextoGanchoRetencion,
  TextoHook,
  TextoLento,
  framePalabra,
  indiceDePalabra,
} from "./Tipografia";
import { ClipReal } from "./ClipReal";
import type { TimelineStandalone } from "./tipos";

const NEGRO = "#050505";
const SONIDOS = {
  whoosh: "assets/sonido/transicion.mp3",
  impacto: "assets/sonido/impacto.mp3",
  stingDuro: "assets/sonido/cierre-duro.mp3",
  musica: "assets/musica/fondo.mp3",
};

export const ManipulacionParte1: React.FC<{ timeline: TimelineStandalone }> = ({ timeline }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  const lineas = timeline.segmentos;
  const f = (segundos: number) => Math.round(segundos * fps);
  const desdeFrameDe = (n: number) => f(lineas[n - 1].inicio); // n: número de línea (1-based)

  // --- Puntos de disparo de sonido y de golpe de cámara, calculados una
  // sola vez a partir del timeline real (no a mano por segundo). ---
  const { golpesCamara, hitsSonido, whooshes } = useMemo(() => {
    const linea3 = lineas[2];
    const linea11 = lineas[10];
    const iAccidente = indiceDePalabra(linea3, (t) => t.includes("accident"));
    const frameAccidente = iAccidente >= 0 ? framePalabra(linea3, f(linea3.inicio), fps, iAccidente) : f(linea3.inicio);
    const indicesControl = linea11.palabras
      .map((p, i) => (p.texto.toLowerCase().includes("control") ? i : -1))
      .filter((i) => i >= 0);
    const framesControl = indicesControl.map((i) => framePalabra(linea11, f(linea11.inicio), fps, i));
    const frameFlashLinea7 = f(lineas[6].inicio);

    return {
      golpesCamara: [frameAccidente, frameFlashLinea7, ...framesControl],
      hitsSonido: [desdeFrameDe(1), frameFlashLinea7, desdeFrameDe(10), ...framesControl],
      whooshes: lineas.slice(1).map((l) => f(l.inicio)), // todas menos la línea 1 (no hay corte "antes" del video)
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lineas, fps]);

  const camara = useCamara(golpesCamara);

  // Banner "Part 1 of 3" persiste líneas 5, 6 y 7 (hasta que arranca el
  // contador de la táctica 1 en la línea 8).
  const bannerDesde = desdeFrameDe(5);
  const bannerHasta = desdeFrameDe(8);
  const mostrarBanner = frame >= bannerDesde && frame < bannerHasta;

  // Música de fondo (bajo de tensión, bajo volumen constante) — se corta
  // en seco justo antes del cierre abrupto de la línea 17, sin swell de cierre.
  const finLinea16 = desdeFrameDe(17);
  const volumenMusica = interpolate(frame, [0, 20, finLinea16 - 10, finLinea16], [0, 0.14, 0.14, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: NEGRO }}>
      <Audio src={staticFile(timeline.audio)} />
      <Audio src={staticFile(SONIDOS.musica)} volume={volumenMusica} />
      {whooshes.map((desde, i) => (
        <Sequence key={`w${i}`} from={Math.max(desde - Math.round(fps * 0.15), 0)} durationInFrames={fps}>
          <Audio src={staticFile(SONIDOS.whoosh)} volume={0.7} />
        </Sequence>
      ))}
      {hitsSonido.map((desde, i) => (
        <Sequence key={`h${i}`} from={desde} durationInFrames={fps}>
          <Audio src={staticFile(SONIDOS.impacto)} volume={0.85} />
        </Sequence>
      ))}
      <Sequence from={desdeFrameDe(17)} durationInFrames={durationInFrames - desdeFrameDe(17)}>
        <Audio src={staticFile(SONIDOS.stingDuro)} volume={1} />
      </Sequence>

      {/* Todo el árbol visual (tipografía, íconos, clips) envuelto en
          CameraMotionBlur: el desenfoque real se intensifica solo en los
          frames donde `camara` cambia más rápido (los golpes), sin
          calcularlo aparte. */}
      <CameraMotionBlur shutterAngle={175} samples={6}>
        <AbsoluteFill style={{ transform: camara.transform }}>
          <Escena1 lineas={lineas} f={f} />
          <Escena2 lineas={lineas} f={f} />
          <EscenaIconoYCaption n={3} lineas={lineas} f={f} icono={<Grieta desdeFrame={0} intensidad={1} />} />
          <EscenaNumero5 lineas={lineas} f={f} />
          <EscenaFigura n={6} lineas={lineas} f={f} icono={<FiguraAutoridad desdeFrame={0} />} />
          <Escena7 lineas={lineas} f={f} />
          <EscenaTactica n={8} contador={1} color="#FF3B3B" lineas={lineas} f={f} />
          <EscenaClip n={9} archivo="content/2026-09-25-manipulation-tactics-part-1/clips/clip-a-gaslighting.mp4" color="#FF3B3B" lineas={lineas} f={f} />
          <Escena10 lineas={lineas} f={f} />
          <Escena11 lineas={lineas} f={f} />
          <EscenaTactica n={12} contador={2} color="#FF9B3B" lineas={lineas} f={f} />
          <EscenaClip n={13} archivo="content/2026-09-25-manipulation-tactics-part-1/clips/clip-b-love-bombing.mp4" color="#FF9B3B" lineas={lineas} f={f} />
          <EscenaFigura n={14} lineas={lineas} f={f} icono={<Anzuelo desdeFrame={0} />} />
          <EscenaIconoYCaption n={15} lineas={lineas} f={f} icono={<Grieta desdeFrame={0} intensidad={2} />} extra={<TextoConContraccion linea={lineas[14]} desdeFrameLinea={0} />} />
          <Escena16 lineas={lineas} f={f} />
          <Escena17 lineas={lineas} f={f} />
        </AbsoluteFill>
      </CameraMotionBlur>

      {mostrarBanner && <BannerSuperior texto="Part 1 of 3" desdeFrame={bannerDesde} />}

      {/* Capa base permanente: activa el 100% del tiempo, incluso sobre
          clips reales e íconos (RULES.md, sección Subtítulos). */}
      <CapaSubtitulos lineas={lineas} />
    </AbsoluteFill>
  );
};

// --- Helpers de una escena por línea: cada una vive en su propio
// <Sequence> (rango [inicio, inicio+duracion) de esa línea) y se centra en
// pantalla salvo que el tratamiento diga lo contrario. ---

type Props = { lineas: TimelineStandalone["segmentos"]; f: (s: number) => number };

const Contenedor: React.FC<{ n: number; f: Props["f"]; lineas: Props["lineas"]; children: React.ReactNode }> = ({ n, f, lineas, children }) => {
  const linea = lineas[n - 1];
  return (
    <Sequence from={f(linea.inicio)} durationInFrames={f(linea.duracion)} layout="none">
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>{children}</AbsoluteFill>
    </Sequence>
  );
};

const Escena1: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={1} f={f} lineas={lineas}>
    <TextoHook texto={lineas[0].texto} desdeFrame={0} />
  </Contenedor>
);

const Escena2: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={2} f={f} lineas={lineas}>
    <PalabrasConGlow linea={lineas[1]} desdeFrameLinea={0} />
  </Contenedor>
);

const EscenaIconoYCaption: React.FC<Props & { n: number; icono: React.ReactNode; extra?: React.ReactNode }> = ({
  n,
  lineas,
  f,
  icono,
  extra,
}) => (
  <Contenedor n={n} f={f} lineas={lineas}>
    {icono}
    {extra}
  </Contenedor>
);

const EscenaNumero5: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={4} f={f} lineas={lineas}>
    <Numero5 desdeFrame={0} />
  </Contenedor>
);

const EscenaFigura: React.FC<Props & { n: number; icono: React.ReactNode }> = ({ n, lineas, f, icono }) => (
  <Contenedor n={n} f={f} lineas={lineas}>
    {icono}
  </Contenedor>
);

const Escena7: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={7} f={f} lineas={lineas}>
    <TextoGanchoRetencion texto={lineas[6].texto} desdeFrame={0} />
  </Contenedor>
);

const EscenaTactica: React.FC<Props & { n: number; contador: number; color: string }> = ({ n, contador, color, lineas, f }) => {
  const linea = lineas[n - 1];
  const nombre = linea.texto.split(":")[1]?.trim().replace(/\.$/, "") ?? linea.texto;
  return (
    <Contenedor n={n} f={f} lineas={lineas}>
      <Contador n={contador} desdeFrame={0} color={color} />
      <NombreTactica texto={nombre} desdeFrame={6} color={color} />
    </Contenedor>
  );
};

const EscenaClip: React.FC<Props & { n: number; archivo: string; color: string }> = ({ n, archivo, color, lineas, f }) => {
  const linea = lineas[n - 1];
  return (
    <Sequence from={f(linea.inicio)} durationInFrames={f(linea.duracion)} layout="none">
      <ClipReal archivo={archivo} desdeFrame={0} duracionFrames={f(linea.duracion)} />
      <RefuerzoSobreClip texto={linea.texto.split(".")[0]} desdeFrame={6} color={color} />
    </Sequence>
  );
};

const Escena10: React.FC<Props> = ({ lineas, f }) => (
  <>
    <Contenedor n={10} f={f} lineas={lineas}>
      <CitasSecuenciales linea={lineas[9]} desdeFrameLinea={0} />
    </Contenedor>
    <Sequence from={f(lineas[9].inicio)} durationInFrames={f(lineas[9].duracion)} layout="none">
      <Grieta desdeFrame={0} intensidad={1.5} />
    </Sequence>
  </>
);

const Escena11: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={11} f={f} lineas={lineas}>
    <ReglaDeTresControl linea={lineas[10]} desdeFrameLinea={0} />
  </Contenedor>
);

const Escena16: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={16} f={f} lineas={lineas}>
    <TextoLento texto={lineas[15].texto} desdeFrame={0} />
  </Contenedor>
);

const Escena17: React.FC<Props> = ({ lineas, f }) => (
  <Contenedor n={17} f={f} lineas={lineas}>
    <TextoCorteSeco texto={lineas[16].texto} />
  </Contenedor>
);
