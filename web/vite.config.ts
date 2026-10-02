import { defineConfig } from 'vite';

export default defineConfig({
  // Relative asset paths so the build works under https://<user>.github.io/<repo>/.
  base: './',
  server: {
    // The game's images and font live in the repository's top-level media/ folder.
    fs: { allow: ['..'] },
  },
});
