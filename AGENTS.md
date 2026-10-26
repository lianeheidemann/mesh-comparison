# Agent instructions — Mesh Comparison

These repository-wide instructions apply to Codex, Claude Code, and other coding agents. Also consult [docs/harness/README.md](docs/harness/README.md) for the project's harness workflow.

## Scope

The project compares an existing ground-truth mesh (GT) against an existing reconstructed mesh (RM). It does **not** itself reconstruct a 3D mesh from a single image. The metric definitions in use are described in the [README](README.md#user-content-evaluation-metrics) and in the [ADRs](docs/adr/); record any change to them in a new ADR and in the documentation. Do not claim the methodology has been scientifically validated without executing suitable tests.

## Required agent workflow

**Before editing**
- Read this file and the relevant current source modules, tests and documentation.
- Describe the requested change, relevant modules, expected numerical impact, proposed validation and rollback.
- Inspect existing tests and documentation before adding new implementations; reuse and extend them rather than rebuilding completed work.
- Keep edits on the explicitly requested branch. Never merge into `main`, change unrelated files, or broaden scope without authorization.

**While editing**
- Prefer minimal, reviewable changes.
- Add or extend deterministic tests with known expected values and justified numerical tolerances for any changed numerical behavior.
- Do not weaken tests, hide failures, replace expected results with outputs from the modified implementation alone, or assert that a test ran when it did not.
- Preserve reproducibility: note input hashes, parameter values, library versions, seeds, renderer/backend and CPU/GPU differences when relevant.
- For Python code, add a meaningful first-line `#` comment describing the file's purpose when creating new files, unless an interpreter-required first line takes precedence.

**After editing**
- Run the smallest relevant tests first, then appropriate broader checks when the environment allows. Clearly distinguish **not run**, **passed**, **failed**, and **environment-blocked**.
- For numerical changes, compare baseline and modified outputs using identical meshes, parameters and dependency versions; report tolerances and actual differences.
- Summarize changed files, test commands/results, limitations and any follow-up work.
- Do not claim complete validation solely from CSV-schema tests, code inspection or successful rendering.

## AI provenance in commits

The companion manuscript discloses AI-assisted development of this software, so every commit made by an AI agent must record it.

- Before the first commit in a clone, run `git config core.hooksPath .githooks`. The `commit-msg` hook adds the trailer automatically for Claude Code (detected via `CLAUDECODE=1`); other agents must write it themselves.
- End each agent commit message with one trailer per agent, using the real tool version and model:
  ```
  AI-Agent: <tool> <tool version>; model: <model>; reasoning: <level>
  ```
  Write `unknown` for any value you cannot determine, or when the model is already named in a `Co-Authored-By` trailer. Never guess a version or model.
- Keep existing `Co-Authored-By` trailers. Do not squash or rewrite commits in a way that drops these trailers.
- Summary: `git log --format='%(trailers:key=AI-Agent,valueonly)' | sort | uniq -c`, or the `AI usage report` workflow (runs on every push to `main`).

If an instruction in this file conflicts with a higher-priority instruction, follow the higher-priority instruction and report the limitation.

## README and documentation links

Whenever `README.md` is updated, update its **Table of contents** in the same change:

- List every `##` and `###` section with the same hierarchy and order; remove entries for sections that no longer exist.
- Link headings as `#user-content-<slug>`, never `#<slug>`, both inside the README and from other documents (`README.md#user-content-<slug>`). On 25/10/2026 it was verified on GitHub (mobile and desktop) that `#<slug>` changes the URL but does not scroll the page, while `#user-content-<slug>` jumps to the heading.
- Use GitHub's slug: lowercase, punctuation removed (accents kept), spaces turned into `-`; e.g. `Perceptual summary — desktop screenshot` → `perceptual-summary--desktop-screenshot`.
- Before finishing, check that every relative link and anchor in the changed documents points to an existing file and heading.

## Review checklist

- [ ] Verified the current code paths and tests affected by the change
- [ ] Reused existing tests; added targeted regression coverage if needed
- [ ] Recorded exact tests and outcomes without inventing evidence
- [ ] Reported numerical changes, tolerances, provenance and limitations
- [ ] Recorded metric-definition changes in an ADR and in the documentation
- [ ] Updated documentation and stayed within the authorized branch/scope
