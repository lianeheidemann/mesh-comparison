# Agent instructions — Mesh Comparison

Repository-wide instructions for Codex, Claude Code and other coding agents. See also the [harness overview](docs/harness/README.md).

## Scope

The project evaluates an existing reconstructed mesh (RM) against an existing ground-truth mesh (GT); it does **not** reconstruct meshes. Metric definitions are in the [README](README.md#user-content-metrics) and the [ADRs](docs/adr/); record any change to them in a new ADR. Do not claim scientific validation without executing suitable tests.

## Workflow

- **Before editing:** read the relevant modules, tests and docs; state the change, expected numerical impact, validation and rollback; reuse and extend existing tests and code. Work only on the requested branch; never merge into `main` or broaden scope without authorization.
- **While editing:** keep changes minimal and reviewable. Add deterministic tests with known expected values and justified tolerances for any numerical change. Never weaken tests, hide failures, derive expected values from the modified code alone, or claim a test ran when it did not. Record seeds, parameters, versions and CPU/GPU differences when relevant. New Python files start with a `#` comment stating their purpose.
- **After editing:** run the smallest relevant tests first, then broader checks. Report each as **passed**, **failed**, **not run** or **environment-blocked**. For numerical changes, compare before/after outputs on identical inputs and report the differences. Summarize changed files, results, limitations and follow-ups.

## AI provenance in commits

The companion manuscript discloses AI-assisted development, so every agent commit records it.

- Run `git config core.hooksPath .githooks` once per clone; the `commit-msg` hook adds the trailer for Claude Code (`CLAUDECODE=1`). Other agents add it themselves:
  ```
  AI-Agent: <tool> <tool version>; model: <model>; reasoning: <level>
  ```
  Write `unknown` for values you cannot determine (or when a `Co-Authored-By` trailer already names the model); never guess.
- Keep `Co-Authored-By` trailers; do not squash or rewrite commits in a way that drops them.
- Summary: `git log --format='%(trailers:key=AI-Agent,valueonly)' | sort | uniq -c` or the `AI usage report` workflow.

If an instruction here conflicts with a higher-priority instruction, follow the latter and report the limitation.

## README and links

- When `README.md` changes, update its **Table of contents** in the same change: every `##`/`###` heading, same order and hierarchy.
- Link headings as `#user-content-<slug>` (also from other documents: `README.md#user-content-<slug>`); plain `#<slug>` does not scroll on GitHub (verified 25/10/2026). Slug: lowercase, punctuation removed (accents kept), spaces → `-`.
- Check that every relative link and anchor in changed documents resolves.

## Review checklist

- [ ] Affected code paths and tests verified; tests reused or extended
- [ ] Exact test commands and outcomes reported, without invented evidence
- [ ] Numerical changes, tolerances, provenance and limitations reported
- [ ] Metric-definition changes recorded in an ADR and in the docs
- [ ] Documentation updated; work kept within the authorized branch and scope
