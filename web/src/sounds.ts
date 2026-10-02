// Port of sounds.py using the Web Audio API in place of pygame.mixer.
import { soundFiles } from './assets';
import type { SoundName } from './game';

let context: AudioContext | null = null;
let gain: GainNode | null = null;
let volume = 0.5;
const buffers = new Map<string, AudioBuffer>();

/** Browsers only allow audio after a user gesture, so this runs on the first click or key press. */
export function unlockAudio(): void {
  if (context) {
    if (context.state === 'suspended') void context.resume();
    return;
  }
  try {
    context = new AudioContext();
  } catch {
    return; // No audio device: the Python version skips sounds in the same situation.
  }
  gain = context.createGain();
  gain.gain.value = volume;
  gain.connect(context.destination);
  const ctx = context;
  for (const [name, url] of Object.entries(soundFiles)) {
    fetch(url)
      .then((response) => response.arrayBuffer())
      .then((data) => ctx.decodeAudioData(data))
      .then((buffer) => buffers.set(name, buffer))
      .catch(() => {});
  }
}

export function play_sound(name: SoundName): void {
  const buffer = buffers.get(name);
  if (!context || !gain || !buffer) return;
  const source = context.createBufferSource();
  source.buffer = buffer;
  source.connect(gain);
  source.start();
}

export function sound_volumes(volume_in: number): void {
  volume = volume_in;
  if (gain) gain.gain.value = volume_in;
}
