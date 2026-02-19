# CLAUDE.md

This file provides context and guidance for AI assistants working in this repository.

## Repository Overview

**Name:** hello-world
**Owner:** Stanley-Choi
**Description:** A minimal introductory repository — "First repository ever"
**Created:** March 2017

This is a bare-bones starter repository containing only a single `README.md`. There is no application code, build system, test suite, or package manager configuration.

## Repository Structure

```
hello-world/
└── README.md    # Single-line project description
```

## Development Workflows

### Branching

- The default branch is `master`.
- Feature and task branches follow the pattern `claude/<description>`.

### Making Changes

Since there is no build system or test runner, the workflow is straightforward:

1. Check out (or create) the appropriate branch.
2. Make changes to files.
3. Commit with a descriptive message.
4. Push to the remote.

```bash
git checkout -b <branch-name>
# ... make changes ...
git add <files>
git commit -m "Descriptive commit message"
git push -u origin <branch-name>
```

### Commits

- Write clear, imperative commit messages (e.g., "Add CLAUDE.md with project documentation").
- Keep commits focused on a single logical change.

## Key Conventions

- **No build step required** — there is no compiled language, bundler, or transpiler.
- **No test suite** — there are no tests to run before committing.
- **No linter/formatter** — no code style enforcement tooling is configured.
- **Markdown only (currently)** — all existing content is Markdown. Follow standard Markdown formatting conventions if adding `.md` files.

## Notes for AI Assistants

- This repository is essentially empty. Any substantial feature work will require building structure from scratch (e.g., adding a `src/` directory, a `package.json`, etc.).
- When adding new languages or tooling, update this file to document the build commands, test commands, and relevant conventions.
- Keep changes minimal and targeted. Do not add boilerplate or scaffolding unless explicitly requested.
