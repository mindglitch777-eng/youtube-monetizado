import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import largo from './data/timeline.json';
import short from './data/timeline_short.json';

export const Root: React.FC = () => (
  <>
    <Composition id="Largo" component={Video} durationInFrames={Math.ceil(largo.duracion * 30)} fps={30} width={1920} height={1080}
      defaultProps={{tl: largo as any, formato: 'largo', audio: 'mezcla.wav'}} />
    <Composition id="Short" component={Video} durationInFrames={Math.ceil(short.duracion * 30)} fps={30} width={1080} height={1920}
      defaultProps={{tl: short as any, formato: 'short', audio: 'mezcla_short.wav'}} />
  </>
);
