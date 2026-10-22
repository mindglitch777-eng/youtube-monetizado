import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import {Serie} from './Serie';
import {Largo2} from './Video2';
import v2largo from './data/v2/largo.json';
import {Short2} from './Video2Short';
import v2s0 from './data/v2/short_0.json';
import v2s1 from './data/v2/short_1.json';
import v2s2 from './data/v2/short_2.json';
import v2s3 from './data/v2/short_3.json';
import v2s4 from './data/v2/short_4.json';
import v2s5 from './data/v2/short_5.json';
import v2s6 from './data/v2/short_6.json';
import v2s7 from './data/v2/short_7.json';
import v2s8 from './data/v2/short_8.json';

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
    <Composition id="V2Largo" component={Largo2} durationInFrames={Math.ceil(v2largo.duracion * 30)} fps={30} width={1920} height={1080}
      defaultProps={{tl: v2largo as any, audio: 'v2_largo.wav'}} />
    <Composition id="V2Short0" component={Short2} durationInFrames={Math.ceil(v2s0.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s0 as any, audio: 'v2_short_0.wav'}} />
    <Composition id="V2Short1" component={Short2} durationInFrames={Math.ceil(v2s1.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s1 as any, audio: 'v2_short_1.wav'}} />
    <Composition id="V2Short2" component={Short2} durationInFrames={Math.ceil(v2s2.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s2 as any, audio: 'v2_short_2.wav'}} />
    <Composition id="V2Short3" component={Short2} durationInFrames={Math.ceil(v2s3.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s3 as any, audio: 'v2_short_3.wav'}} />
    <Composition id="V2Short4" component={Short2} durationInFrames={Math.ceil(v2s4.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s4 as any, audio: 'v2_short_4.wav'}} />
    <Composition id="V2Short5" component={Short2} durationInFrames={Math.ceil(v2s5.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s5 as any, audio: 'v2_short_5.wav'}} />
    <Composition id="V2Short6" component={Short2} durationInFrames={Math.ceil(v2s6.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s6 as any, audio: 'v2_short_6.wav'}} />
    <Composition id="V2Short7" component={Short2} durationInFrames={Math.ceil(v2s7.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s7 as any, audio: 'v2_short_7.wav'}} />
    <Composition id="V2Short8" component={Short2} durationInFrames={Math.ceil(v2s8.duracion * 30)} fps={30} width={1080} height={1920} defaultProps={{tl: v2s8 as any, audio: 'v2_short_8.wav'}} />
  </>
);
