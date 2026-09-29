import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Anton (contador/CTA/énfasis triple) e Inter (subtítulos), licencia OFL,
// guardadas en remotion/fuentes/ — el render no depende de internet.
loadFont({ family: "Anton", url: staticFile("fuentes/Anton.ttf"), weight: "400" });
loadFont({ family: "Inter", url: staticFile("fuentes/Inter-ExtraBold.ttf"), weight: "800" });
