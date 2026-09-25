import React from "react";
import { AbsoluteFill } from "remotion";

// Miniatura: número grande, texto mínimo, alto contraste — tiene que
// destacar en un feed a tamaño chico de celular (RULES.md, sección
// Miniatura y título). Estática a propósito (es una imagen, no una escena).
export const Miniatura: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#050505" }}>
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 18 }}>
      <div
        style={{
          fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 460, lineHeight: 1, color: "#FF3B3B",
          textShadow: "0 0 90px rgba(255,59,59,0.55), 0 20px 40px rgba(0,0,0,0.9)",
        }}
      >
        5
      </div>
      <div
        style={{
          fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 92, color: "#FFFFFF",
          letterSpacing: 1, textAlign: "center", lineHeight: 1.05, textShadow: "0 10px 26px rgba(0,0,0,0.85)",
        }}
      >
        MANIPULATION
        <br />
        TACTICS
      </div>
      <div
        style={{
          marginTop: 8, fontFamily: "Montserrat, sans-serif", fontWeight: 800, fontSize: 42, color: "#FFD83D",
          letterSpacing: 3, textTransform: "uppercase",
        }}
      >
        Part 1
      </div>
    </AbsoluteFill>
    {/* Grieta, coherente con el puzzle visual del short. */}
    <svg width={260} height={400} viewBox="0 0 110 170" style={{ position: "absolute", top: 0, right: 0, opacity: 0.8 }}>
      <path
        d="M110 0 L72 58 L90 95 L55 150"
        fill="none" stroke="#FFFFFF" strokeWidth="3" strokeLinecap="round"
        style={{ filter: "drop-shadow(0 0 8px rgba(255,255,255,0.7))" }}
      />
    </svg>
  </AbsoluteFill>
);
