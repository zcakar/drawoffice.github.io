## Copilot / AI Agent Instructions — drawoffice.github.io

Purpose: give a new AI coding agent the minimal, actionable knowledge
to be productive in this repository — key architecture, build/release
flows, conventions, and examples specific to this codebase.

- **Big picture**: this repo hosts the ONLYOFFICE plugins marketplace site and
  plugin assets. Primary concerns are static plugin code under
  `sdkjs-plugins/content/`, plugin styling under `sdkjs-plugins/v1/`, and
  the plugin manager site under `store/`.

- **Key directories & files**:
  - `sdkjs-plugins/content/` — each plugin lives in a subfolder here.
  - `sdkjs-plugins/v1/` — shared plugin CSS, assets and `plugins.css`.
  - `packer/pack.py` — Python utility that produces `.plugin` archives.
  - `.github/workflows/pack-plugins.yml` — CI job that runs the packer,
    bumps a `vX.Y.Z` tag and uploads `artifacts/*.plugin` as a release.
  - `.dev/config.json` (per plugin) — optional file with packaging hints
    (notably `excludes`). Example: `sdkjs-plugins/content/<plugin>/.dev/config.json`.

- **Why things are structured this way**:
  - Plugins are packaged as zip archives renamed to `.plugin` for marketplace
    releases. The `pack.py` script centralizes packaging rules and path
    rewriting so plugins can reference shared `v1` assets during runtime.

- **Important packaging details** (refer to `packer/pack.py`):
  - Default excludes: `deploy/*`, `node_modules/*`, `.dev/*`.
  - `pack.py` will read `.dev/config.json` and merge `excludes`.
  - HTML path rewrite: URLs matching
    `https://onlyoffice.github.io/sdkjs-plugins/v1/...` are rewritten to
    `./../v1/...` before archiving. This behavior is implemented by
    `OLD_PATH_PATTERN` → `NEW_PATH` in the script.
  - Output: archives are created in `artifacts/` (or `deploy/` in `--old-mode`).

- **Local developer workflows (concise commands)**:
  - Pack all plugins (new mode):
    `python3 packer/pack.py`
  - Pack in legacy mode (put `.plugin` into each plugin `deploy/`):
    `python3 packer/pack.py --old-mode`
  - CI release flow: `.github/workflows/pack-plugins.yml` bumps a tag,
    runs `packer/pack.py`, and uploads `artifacts/*.plugin` as a release.

- **Conventions & patterns to follow when editing**:
  - Use `.dev/config.json` per plugin to control packaging exclusions.
  - Keep plugin HTML references to `https://onlyoffice.github.io/sdkjs-plugins/v1/...`
    if the plugin expects shared assets — packer will rewrite them.
  - Archives are ZIPs renamed to `.plugin`; the packer ensures `.plugin`
    files are produced and renamed safely.

- **Examples and snippets**:
  - Read excludes from a plugin: see `PluginPacker.get_plugin_excludes()` in
    `packer/pack.py` (merges `DEFAULT_EXCLUDES` with `.dev/config.json`).
  - Path rewrite logic lives in `replace_html_paths()` — useful if you add
    new HTML file types or additional URL patterns.

- **Integration points & cross-repo notes**:
  - This repo is primarily static/content oriented. Other local folders in
    the workspace (e.g., `DocumentServer`, `DocSpace`) are separate projects.
  - CI uses GitHub Actions to tag and release plugin artifacts — be cautious
    when changing `.github/workflows/pack-plugins.yml` because it controls
    release tagging and artifact upload.

- **What to avoid / watch for**:
  - Don’t remove the HTML path-rewrite without handling shared `v1` asset
    references; plugins rely on stable paths.
  - Packaging relies on `.dev/config.json` for excludes; accidental
    inclusion of `node_modules` or large build output will bloat `.plugin` files.

If anything here is unclear or you want more examples (for a specific
plugin folder, or the release/tagging flow), tell me which area to expand.
