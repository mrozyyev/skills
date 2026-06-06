---
name: pagescms
description: |
  Open-source CMS for static sites stored in GitHub. Configures a `.pages.yml` to edit content, collections, media, and files directly via GitHub commits — no separate database. Use when setting up a CMS for a static site repo (Hugo, Jekyll, Astro, Next.js static export), when creating or editing `.pages.yml` config files, when building content models with fields and frontmatter editors, or when the user says "Pages CMS", "static site CMS", "headless CMS for GitHub", or "edit static site content".
---

# Pages CMS

Pages CMS is an open-source CMS for static sites stored in GitHub repositories. It edits files directly in the repo — no separate CMS database. The missing piece for most static sites is the editing experience, and Pages CMS provides a UI so non-technical editors can manage content without learning Git.

Official docs: https://pagescms.org/docs/
GitHub: https://github.com/pages-cms/pages-cms
Hosted app: https://app.pagescms.org

## Quick start

1. Go to [app.pagescms.org](https://app.pagescms.org), sign in with GitHub.
2. Install the GitHub App on the account/org that owns the repo.
3. Open the repo, create `.pages.yml` when prompted, start editing.

**Minimal `.pages.yml` config:**

```yaml
media: media
content:
  - name: pages
    label: Pages
    type: collection
    path: docs
    fields:
      - name: title
        type: string
      - name: body
        type: rich-text
```

## Configuration structure

`.pages.yml` lives at the repo root. Top-level keys:

| Key | Description |
|-----|-------------|
| `media` | Where uploads are stored and what public URLs are written. String, object, or array. |
| `content` | Editable collections (`type: collection`), single files (`type: file`), or nav groups (`type: group`). |
| `components` | Reusable field definitions shared across content models. |
| `settings` | Repository-wide behavior: commit templates, commit identity, content merge mode. |
| `actions` | GitHub Actions workflow buttons at repo/collection/entry level. |

## Content types

- **collection** — many files with the same schema (e.g. blog posts in `content/posts/`)
- **file** — one file with its own schema (e.g. `data/site.json` for site settings)
- **group** — navigation-only organizer for nested entries

Each supports: `fields`, `format` (yaml-frontmatter, json-frontmatter, toml-frontmatter, yaml, json, toml, datagrid, code, raw), `filename` template, `view` (list display), `operations` (create/rename/delete), `subfolders`, `exclude`, and per-entry `actions`.

## Field types (14 total)

`string`, `text`, `rich-text`, `number`, `boolean`, `date`, `code`, `select`, `image`, `file`, `object`, `block`, `reference`, `uuid`

All fields support: `name`, `label`, `required`, `pattern` (regex, `string`/`text` only), `hidden`, `readonly`, `description`, `options`. Use `component` instead of `type` to reference a reusable field definition from `components`.

Special key: `body` maps to frontmatter body content (below the delimiters).

## Media configuration

```yaml
# String form (shortcut):
media: media

# Single object:
media:
  input: src/media
  output: /media
  rename: random

# Multiple sources:
media:
  - name: images
    label: Images
    input: media/images
    output: /media/images
    categories: [image]
  - name: docs
    label: Documents
    input: media/docs
    output: /media/docs
    extensions: [pdf, docx]
```

## Components (reusable fields)

```yaml
components:
  seo:
    type: object
    label: SEO
    fields:
      - name: title
        type: string
      - name: description
        type: text

content:
  - name: pages
    type: collection
    path: content/pages
    fields:
      - name: heading
        type: string
      - name: seo
        component: seo
        label: Meta  # overrides component label
```

## Settings (global behavior)

```yaml
settings:
  content:
    merge: true  # preserve keys outside the schema
  commit:
    identity: user  # "app" (default) or "user"
    templates:
      create: "content(create): {path}"
      update: "content(update): {path} by {userName}"
      delete: "content(delete): {path}"
      rename: "content(rename): {oldPath} -> {newPath}"
```
Template tokens: `{action}`, `{path}`, `{filename}`, `{name}`, `{owner}`, `{repo}`, `{branch}`, `{user}`, `{userName}`, `{userEmail}`, `{oldPath}`, `{newPath}`, `{oldFilename}`, `{newFilename}`.

## Workflows

### Setting up a new static site

1. Check existing repo structure — note where content files and media live.
2. Read current file formats to choose the right `format` value.
3. Create `.pages.yml` configuring `media` first, then `content` per existing file structure.
4. Test by opening in app.pagescms.org.

### Adding a new collection

1. Add a `content` entry with `type: collection`, `path`, and `fields`.
2. Set `format` to match existing file format (default is `yaml-frontmatter`).
3. Configure `view` for list display (`primary`, `sort`, `order`).
4. Optionally set `filename` template and `operations`.

### Adding a single file editor

1. Add a `content` entry with `type: file`, `path` pointing to the exact file.
2. Define `fields` to match the file's structure.
3. Use `format: json` for JSON files, `format: yaml` for YAML files.

### Configuring media uploads

1. Define `media` with `input` (repo path) and `output` (public URL path).
2. Set `rename` behavior: `false` (keep original), `safe` (slugify), or `random`.
3. Restrict with `extensions` or `categories`.

## Installing your own instance

- **Local**: Clone repo, PostgreSQL via Docker, `npm install`, `.env.local` with `DATABASE_URL`/`BETTER_AUTH_SECRET`/`CRYPTO_KEY`, `npm run setup:github-app`, `npm run db:migrate`, `npm run dev`.
- **Vercel**: One-click deploy from GitHub repo.
- **Self-host**: Docker image available.
- **GitHub App**: Register a GitHub App for authentication.

## Reference

- Full docs: https://pagescms.org/docs/
- Each field type has its own docs page at `https://pagescms.org/docs/configuration/fields/{type}/`
- Installing guides: https://pagescms.org/docs/guides/installing/
- Environment variables: https://pagescms.org/docs/development/environment-variables/
