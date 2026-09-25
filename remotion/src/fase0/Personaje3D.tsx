import { ThreeCanvas } from "@remotion/three";
import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";

// PRUEBA DE CONCEPTO — Fase 0, rama 3D real (@remotion/three).
// Un personaje-silueta con volumen genuino: geometría 3D + MeshStandardMaterial
// + luz direccional con sombra proyectada real sobre el piso. Dos poses
// (neutral → señalando) interpoladas por rotación de las articulaciones.

const COLOR_CUERPO = "#8A6B4A"; // silueta con contraste real contra el fondo (ver COLOR_FONDO)
const COLOR_PISO = "#241A12";
const COLOR_FONDO = "#100C08";

export const Personaje3D: React.FC<{ cambioEnFrame: number }> = ({ cambioEnFrame }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  // t: 0 = pose neutral, 1 = pose señalando. Transición con física de resorte,
  // no interpolación lineal — así el brazo "pesa" y rebota un poco al llegar.
  const t = spring({ frame: frame - cambioEnFrame, fps, config: { damping: 11, stiffness: 90, mass: 1.1 } });

  // Cámara: nunca 100% estática — paneo lateral lento + acercamiento continuo.
  const avance = frame / (durationInFrames || 1);
  const camX = interpolate(avance, [0, 1], [-0.6, 0.6]);
  const camZ = interpolate(avance, [0, 1], [6.2, 5.4]);

  const materialCuerpo = useMemo(
    () => new THREE.MeshStandardMaterial({ color: COLOR_CUERPO, roughness: 0.85, metalness: 0.05 }),
    [],
  );

  // Ángulo del brazo derecho: pegado al cuerpo (neutral) -> extendido señalando al frente.
  const hombroX = interpolate(t, [0, 1], [0.15, -1.35]); // levanta el brazo
  const hombroZ = interpolate(t, [0, 1], [0.1, 0.35]);
  const codo = interpolate(t, [0, 1], [0.2, -0.15]);
  const inclinacionTorso = interpolate(t, [0, 1], [0, -0.12]);

  return (
    <AbsoluteFill style={{ backgroundColor: COLOR_FONDO }}>
      <ThreeCanvas linear width={width} height={height} shadows>
        <perspectiveCamera makeDefault position={[camX, 1.1, camZ]} fov={35} />
        <ambientLight intensity={0.45} />
        <directionalLight
          position={[3, 5, 4]}
          intensity={1.6}
          castShadow
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
          shadow-camera-left={-4}
          shadow-camera-right={4}
          shadow-camera-top={4}
          shadow-camera-bottom={-4}
        />

        {/* Piso, para que la sombra proyectada sea real (no un óvalo dibujado). */}
        <mesh position={[0, -1.55, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[14, 14]} />
          <meshStandardMaterial color={COLOR_PISO} roughness={1} />
        </mesh>

        <group position={[0, 0, 0]} rotation={[0, 0, inclinacionTorso]}>
          {/* Torso */}
          <mesh position={[0, 0, 0]} castShadow material={materialCuerpo}>
            <capsuleGeometry args={[0.55, 1.1, 6, 12]} />
          </mesh>
          {/* Cabeza (sin rasgos, como en RULES.md) */}
          <mesh position={[0, 1.15, 0]} castShadow material={materialCuerpo}>
            <sphereGeometry args={[0.42, 20, 20]} />
          </mesh>
          {/* Brazo izquierdo: queda quieto, apoyado */}
          <group position={[-0.62, 0.35, 0]}>
            <mesh position={[0, -0.5, 0]} rotation={[0, 0, 0.12]} castShadow material={materialCuerpo}>
              <capsuleGeometry args={[0.15, 0.9, 6, 10]} />
            </mesh>
          </group>
          {/* Brazo derecho: el que anima la pose */}
          <group position={[0.62, 0.35, 0]} rotation={[hombroX, 0, hombroZ]}>
            <mesh position={[0, -0.45, 0]} castShadow material={materialCuerpo}>
              <capsuleGeometry args={[0.15, 0.8, 6, 10]} />
            </mesh>
            <group position={[0, -0.95, 0]} rotation={[codo, 0, 0]}>
              <mesh position={[0, -0.35, 0]} castShadow material={materialCuerpo}>
                <capsuleGeometry args={[0.13, 0.65, 6, 10]} />
              </mesh>
            </group>
          </group>
        </group>
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
