import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setCodec("h264");
Config.setPixelFormat("yuv420p");
Config.setCrf(18);
Config.setOverwriteOutput(true);

// El entorno de Claude Code no tiene salida de red a remotion.media (donde
// Remotion descarga su propio Chrome Headless Shell) pero sí trae Chromium
// preinstalado para Playwright — se lo reusa acá (mismo fix que ../remotion).
if (process.env.PLAYWRIGHT_BROWSERS_PATH) {
  Config.setBrowserExecutable(
    `${process.env.PLAYWRIGHT_BROWSERS_PATH}/chromium_headless_shell-1194/chrome-linux/headless_shell`,
  );
}
