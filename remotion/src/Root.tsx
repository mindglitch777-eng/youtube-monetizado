import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import {Serie} from './Serie';
import largo from './data/timeline.json';
import s00 from './data/shorts/short_00.json';
import s01 from './data/shorts/short_01.json';
import s02 from './data/shorts/short_02.json';
import s03 from './data/shorts/short_03.json';
import s04 from './data/shorts/short_04.json';
import s05 from './data/shorts/short_05.json';
import s06 from './data/shorts/short_06.json';
import s07 from './data/shorts/short_07.json';

export const Root: React.FC = () => (
  <>
    <Composition id="Largo" component={Video} durationInFrames={Math.ceil(largo.duracion * 30)} fps={30} width={1920} height={1080}
      defaultProps={{tl: largo as any, formato: 'largo', audio: 'mezcla.wav'}} />
    <Composition id="Short00" component={Serie} durationInFrames={Math.ceil(s00.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s00 as any, audio: 'mezcla_short_00.wav'}} />
    <Composition id="Short01" component={Serie} durationInFrames={Math.ceil(s01.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s01 as any, audio: 'mezcla_short_01.wav'}} />
    <Composition id="Short02" component={Serie} durationInFrames={Math.ceil(s02.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s02 as any, audio: 'mezcla_short_02.wav'}} />
    <Composition id="Short03" component={Serie} durationInFrames={Math.ceil(s03.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s03 as any, audio: 'mezcla_short_03.wav'}} />
    <Composition id="Short04" component={Serie} durationInFrames={Math.ceil(s04.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s04 as any, audio: 'mezcla_short_04.wav'}} />
    <Composition id="Short05" component={Serie} durationInFrames={Math.ceil(s05.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s05 as any, audio: 'mezcla_short_05.wav'}} />
    <Composition id="Short06" component={Serie} durationInFrames={Math.ceil(s06.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s06 as any, audio: 'mezcla_short_06.wav'}} />
    <Composition id="Short07" component={Serie} durationInFrames={Math.ceil(s07.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: s07 as any, audio: 'mezcla_short_07.wav'}} />
  </>
);
