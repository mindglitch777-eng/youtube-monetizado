import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import type { SfxEvento } from "./tipos";

const DB = (db: number) => Math.pow(10, db / 20);
const NIVEL_SFX = DB(-12); // RULES.md, REGLA DE SONIDO

const ARCHIVO_POR_TIPO: Record<SfxEvento["tipo"], string> = {
  whoosh: "whoosh.mp3",
  impacto: "impacto-contador.mp3",
  latido: "latido.mp3",
  riser: "riser.mp3",
  notificacion: "notificacion.mp3",
};

// Los archivos reales bajados de Mixkit no siempre son cortos (p.ej.
// "latido.mp3" es un ritmo de 8s) — se corta cada uno a una ventana que
// alcanza para su uso como acento puntual, sin que se pise con la línea
// siguiente.
const DURACION_FRAMES_POR_TIPO: Record<SfxEvento["tipo"], number> = {
  whoosh: 20, impacto: 15, latido: 20, riser: 42, notificacion: 30,
};

// Capa de SFX puntuales (whoosh en ganchos/contador, impacto de contador,
// latido al inicio del gancho, riser+golpe de la grilla, notificación de
// celular) — cada uno como su propio <Audio> en un <Sequence> puntual, 2-3
// frames antes del corte que acompaña (RULES.md, REGLA DE SONIDO).
// `disponibles` filtra los tipos cuyo archivo no se pudo descargar.
export const CapaSfx: React.FC<{ eventos: SfxEvento[]; disponibles: Set<string> }> = ({ eventos, disponibles }) => (
  <>
    {eventos.map((ev, i) => {
      const archivo = ARCHIVO_POR_TIPO[ev.tipo];
      if (!disponibles.has(archivo)) return null;
      const duracion = ev.hasta ? Math.max(1, ev.hasta - ev.frame) : DURACION_FRAMES_POR_TIPO[ev.tipo];
      return (
        <Sequence key={i} from={ev.frame} durationInFrames={duracion} layout="none">
          <Audio src={staticFile(`sonido-kai/${archivo}`)} volume={NIVEL_SFX} />
        </Sequence>
      );
    })}
  </>
);
