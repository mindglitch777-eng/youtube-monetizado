import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Inter y Playfair Display (licencia OFL), guardadas en remotion/fuentes/:
// el render no depende de internet. Mismo patrón que ../Subtitulos.tsx con
// Montserrat. Importar este módulo una sola vez (por su efecto) alcanza
// para que Captions.tsx y Plate.tsx tengan las fuentes disponibles.
loadFont({ family: "Inter", url: staticFile("fuentes/Inter-Bold.ttf"), weight: "700" });
loadFont({ family: "Inter", url: staticFile("fuentes/Inter-ExtraBold.ttf"), weight: "800" });
loadFont({ family: "Playfair Display", url: staticFile("fuentes/PlayfairDisplay-ExtraBold.ttf"), weight: "800" });
loadFont({
  family: "Playfair Display",
  url: staticFile("fuentes/PlayfairDisplay-BoldItalic.ttf"),
  weight: "700",
  style: "italic",
});
