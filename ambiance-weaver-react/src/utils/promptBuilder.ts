// AudioGen prompt: 主体+动作/变化+场景/氛围
export function buildAudioGenPrompt({
  subjects,
  actions,
  scenes,
  type = 'audio', // 新增参数，默认为 audio
  mode = 'default', // 新增mode参数
}: {
  subjects: string[]; // 必填，主体（如 rain, cafe chatter）
  actions?: string[]; // 可选，动作/变化（如 in the background, mixed with）
  scenes?: string[];  // 可选，场景/氛围（如 in a cozy cafe, at night）
  type?: 'audio' | 'music'; // 新增类型参数
  mode?: string; // 新增mode参数
}): string {
  let prompt = '';
  
  // 根据mode添加特定的prompt模板
  let modeTemplate = '';
  if (mode === 'asmr') {
    modeTemplate = 'Gentle ASMR soundscape with soft, delicate, and soothing ';
  } else if (mode === 'sleep') {
    modeTemplate = 'Calm and peaceful sleep soundscape with gentle, lulling ';
  } else if (mode === 'focus') {
    modeTemplate = 'Steady and consistent focus soundscape with subtle, non-distracting ';
  } else if (mode === 'creative') {
    modeTemplate = 'Inspiring and dynamic creative soundscape with flowing, energizing ';
  } else if (mode === 'mindful') {
    modeTemplate = 'Serene and tranquil mindful soundscape with balanced, harmonious ';
  } else if (mode === 'story') {
    modeTemplate = 'Narrative soundscape with immersive, atmospheric ';
  } else {
    modeTemplate = 'Ambient soundscape: ';
  }
  
  if (type === 'music') {
    prompt += 'Music: ';
  } else {
    prompt += modeTemplate;
  }
  
  if (subjects && subjects.length > 0) {
    prompt += subjects.join(' and ');
  }
  if (actions && actions.length > 0) {
    prompt += ' ' + actions.join(', ');
  }
  if (scenes && scenes.length > 0) {
    prompt += ' ' + scenes.join(', ');
  }
  
  // 为每个mode添加特定的结尾
  if (mode === 'asmr') {
    prompt += ', creating a deeply relaxing and intimate listening experience';
  } else if (mode === 'sleep') {
    prompt += ', perfect for deep sleep and relaxation';
  } else if (mode === 'focus') {
    prompt += ', designed to enhance concentration and productivity';
  } else if (mode === 'creative') {
    prompt += ', inspiring creative flow and artistic expression';
  } else if (mode === 'mindful') {
    prompt += ', supporting meditation and mindfulness practice';
  }
  
  return prompt.trim();
}

// MusicGen prompt: 情绪/氛围+风格/流派+乐器+节奏/结构+场景/用途
export function buildMusicGenPrompt({
  mood,
  genre,
  instruments,
  tempo,
  usage
}: {
  mood?: string;         // 可选，情绪/氛围（relaxing, energetic）
  genre: string;         // 必填，风格/流派（ambient, jazz）
  instruments: string[]; // 必填，乐器（piano, guitar）
  tempo?: string;        // 可选，节奏/结构（slow tempo, fast beat）
  usage?: string;        // 可选，场景/用途（for a cozy cafe）
}): string {
  let prompt = '';
  if (mood) prompt += mood + ' ';
  prompt += genre + ' track featuring ' + instruments.join(' and ');
  if (tempo) prompt += ', ' + tempo;
  if (usage) prompt += ', ' + usage;
  return prompt.trim();
} 