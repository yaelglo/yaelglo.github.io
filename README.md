# Yael Goldberg — Unity developer portfolio

Personal portfolio and Merge Alchemy case study, hosted at https://yaelglo.github.io/.

## Local preview

Run `python -m http.server 8000 --bind 127.0.0.1 --directory site` and open http://127.0.0.1:8000/.

## Production build

Run `python scripts/build.py --require-resume`, then `python scripts/check_production.py`.

The dependency-free static build writes `.build/pages/`, validates relative links and exact-case asset paths, and adds the production social/canonical URLs. It requires the actual `site/assets/resume.pdf` and includes no recordings or development comparisons.

## Deployment

GitHub Pages uses the workflow in `.github/workflows/pages.yml`. Pushes to `main` build and deploy the validated artifact. The repository is named `yaelglo.github.io`, so the site is served at `/` without a repository subpath.

## Attribution

Merge Alchemy's game design and technical direction are by Yael Goldberg. All production game code was written by AI coding agents under her direction. See the case study for responsibilities and development decisions.

The Manrope font license is included in `site/assets/manrope-license.txt`.
