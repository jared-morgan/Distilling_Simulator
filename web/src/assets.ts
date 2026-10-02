// Loads the images and font the desktop version reads from media/, plus the sounds.
// The images come straight from the repository's media/ folder so both versions share them.
// The sounds are MP3 conversions of media/*.ogg, since Safari can't decode Ogg Vorbis everywhere.

const imageUrls = import.meta.glob('../../media/*.png', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
const soundUrls = import.meta.glob('./sounds/*.mp3', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
import fontUrl from '../../media/Roboto-Regular.ttf?url';

export const FONT_FAMILY = 'Roboto Simulator';

const images = new Map<string, HTMLImageElement>();

function baseName(path: string): string {
  return path.slice(path.lastIndexOf('/') + 1).replace(/\.[^.]+$/, '');
}

export function image(name: string): HTMLImageElement {
  const img = images.get(name);
  if (!img) throw new Error(`Missing image ${name}`);
  return img;
}

export const soundFiles: Record<string, string> = Object.fromEntries(
  Object.entries(soundUrls).map(([path, url]) => [baseName(path), url]),
);

export async function loadAssets(): Promise<void> {
  const imageLoads = Object.entries(imageUrls).map(async ([path, url]) => {
    const img = new Image();
    img.src = url;
    await img.decode();
    images.set(baseName(path), img);
  });
  const font = new FontFace(FONT_FAMILY, `url(${fontUrl})`);
  const fontLoad = font.load().then((loaded) => document.fonts.add(loaded));
  await Promise.all([...imageLoads, fontLoad]);
}
