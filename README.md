# Running

## Desktop (Python)
Requires Python 3.13+ and the modules dearpygui, numpy, pygame, pyperclip and sounddevice.

```
uv sync
uv run Distilling_Sim.pyw
```

Or install the modules with pip and run `Distilling_Sim.pyw` directly.

To build a standalone executable:

```
pyinstaller Distilling_Sim.pyw --onefile --noconsole --icon piece_white.ico
```

## Web (TypeScript)

```
cd web
npm install
npm run dev     # local server with hot reload
npm test        # unit tests
npm run build   # static site in web/dist
```

Pushing to `main` deploys to GitHub Pages via `.github/workflows/pages.yml` (set Settings > Pages > Source to "GitHub Actions").
