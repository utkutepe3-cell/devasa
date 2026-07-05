# AGENTS.md

## Cursor Cloud specific instructions

`devasa` is a **static front-end project** — plain HTML/CSS/JS with no build step, no
package manager, and no runtime dependencies. Node 22 and Python 3.12 are preinstalled
on the VM, so the startup update script is a no-op.

The application code currently lives on feature branches (e.g. the TSYS Virtual Terminal
demo: `index.html`, `app.js`, `styles.css`); the `main` branch may only contain
`README.md`. When app files are present, run and test it as a static site:

- Serve locally: `python3 -m http.server 8080` (run from the directory containing
  `index.html`), then open `http://localhost:8080`.
- There is nothing to build, lint, or compile by default and there are no automated
  tests; verify changes by loading the page in a browser and exercising the UI.
