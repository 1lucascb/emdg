---
title: GitHub Pages deployment
order: 2
tags: [deployment, github-actions]
---

# GitHub Pages deployment

The workflow in `.github/workflows/docs.yml` builds the Markdown under `docs/`
and publishes the resulting site to GitHub Pages.

## One-time repository setup

1. Open the repository's **Settings → Pages**.
2. Set the Pages **Build and deployment** source to **GitHub Actions**.
3. Ensure Actions are enabled for the repository and that the workflow is
   allowed to deploy Pages.

The workflow requests `contents: read`, `pages: write`, and `id-token: write`;
the latter two permissions are needed to upload and deploy the Pages artifact.

## Deployment behavior

The workflow runs after pushes to `main` and can also be started manually from
the repository's **Actions** tab using **Run workflow**. It sets up Python 3.13,
builds the site into `_site/index.html`, uploads `_site` as the Pages artifact,
and deploys it. The generated `index.html` is the site's entry point. The
workflow uses the checked-out package directly and does not install additional
Python dependencies.

After the first successful deployment, GitHub Actions shows the published URL
in the deployment job's `github-pages` environment.

## Changing the deployment source

To publish different documentation, update the source directory in the build
command in `.github/workflows/docs.yml`. Keep the output at
`_site/index.html`, or ensure the uploaded artifact contains an `index.html` at
its root. The site's Tailwind CSS, Marked, Highlight.js, and Mermaid assets are
loaded from public CDNs, so visitors need internet access for the complete
rendering experience.
