# show-receipts

[中文](README.md) · **English**

> Before a document goes out, have the AI check every claim in it against the materials you actually have.

A Claude Code skill that audits a README, proposal, report or product page before you publish it. It checks each claim against your own evidence: the repo's files, your notes, your data. Every finding cites where the evidence is, and anything it can't verify offline is marked *unverified* rather than *wrong*.

![A README before revision, next to the show-receipts report on it](assets/compare.png)

*The example above is in Chinese because the README it checks is Chinese.*

---

## The problem

AI-drafted READMEs and pitches tend to fail in the same few ways:

- demo numbers from a prototype show up as "current value" or "live in production";
- the doc mentions `npm install`, a `src/` directory or a LICENSE file that the repo doesn't have;
- "studies show…" or "the industry average is…" with no source;
- two months of work becomes "half a year of polishing".

This skill makes the AI check those claims against the repo, your notes and your data before anything is published.

## What it is, and what it isn't

Two rounds of controlled evaluation (below) point to a clear conclusion:

- **It does not make the model find more problems.** Both models we tested (Opus and Haiku) already find nearly all of these issues without the skill.
- **It makes the report focused and checkable.**
  - With the skill, about 90% of findings are actual claim-vs-evidence problems. Without it, about 70% are; the rest is design feedback, copy editing and domain advice.
  - Every finding names the file and line its evidence comes from, and is graded *backed / unverified / unsupported*.
  - External facts it can't check offline are marked *unverified*. It doesn't tell you you're wrong based on the model's own memory.

If you want a broad review of everything, you're better off without it. If you want a last pass on "does every sentence here hold up", that's what it's for.

## The six problem types

| Type | Examples |
|---|---|
| Demo data presented as real | "current value", "launched", "100k users", when it's only prototype sample data |
| Things that don't exist | files, directories, commands, links, a license the repo doesn't have |
| Numbers or quotes with no source | "studies show", "according to industry data", with nothing to back it |
| Inflation | durations and scale stretched; "first", "only", "best in class" |
| Capabilities with no evidence | "supports X", with nothing in the code or notes |
| Internal contradictions | the same number stated differently in two places, or differently from your notes |

Detailed rules (in Chinese): [references/categories.md](references/categories.md). Rewrite patterns: [references/rewrites.md](references/rewrites.md).

## Install

In Claude Code, clone it into your personal skills directory:

```bash
git clone https://github.com/panglezym/show-receipts ~/.claude/skills/show-receipts
```

Or put it in a single project at `.claude/skills/show-receipts/`.

The check script uses only the Python standard library. It has been tested on Python 3.9.

## Use

In Claude Code, just ask:

- "Check this README before I publish it."
- "Is anything in here made up? Do these numbers hold up?"

Point it at your materials (repo directory, notes, data) for best results. It still runs without them, but the report will say there was nothing to check against, and most findings will be *unverified*.

To run only the mechanical checks (paths, command dependencies, license, repeated numbers) with no model involved:

```bash
python3 scripts/check.py README.md --root .
```

It exits with code 1 when it finds missing paths, so you can put it in CI.

## Evaluation

Both rounds were controlled comparisons: same document, same model, same prompt, one run with the skill and one without, scored against an answer key frozen before the runs.

| | Round 1 | Round 2 |
|---|---|---|
| Model | Opus | Haiku |
| Cases | Earlier versions of 3 real READMEs | The same 3, plus 3 new fictional READMEs with planted problems |
| Core problems found | without 20/20, with 20/20 | without 49/50, with 50/50 |
| Share of findings in scope | without ~70%, with ~90% | without 72%, with 91% |
| Unverifiable external facts marked "must fix" | without 1, with 0 | 0 in both |
| Backed decoy claims marked wrong | not tested | 0 in both |
| Cost | ~20% slower | ~50% slower, ~20% more tokens |

Round 2 was pre-registered: the skill had to find at least 10 percentage points more problems to count as "finds more". It found 2 points more, so this README **does not claim** it finds more problems.

**Limitations:**

- Each case was run once per arm; the sample is small.
- The six problem types were derived from the round 1 cases, so round 1 is in-sample.
- The new round 2 cases were written by another model and may not read like real-world documents.
- There was a single scorer, on the skill author's side. Every scoring decision is published for review.
- In the evaluation, agents followed SKILL.md by hand. Claude Code's automatic triggering of the skill was not tested.

The full record, answer keys and all 18 raw reports are in [eval/](eval/) (in Chinese). Both rounds were run on version 0.1.0; later changes are in [CHANGELOG.md](CHANGELOG.md).

## What's in the repo

```
.
├── SKILL.md              # the skill: triggers, workflow, report format
├── references/
│   ├── categories.md     # rules for the six problem types
│   └── rewrites.md       # rewrite patterns
├── scripts/
│   └── check.py          # mechanical checks, standard library only
├── examples/             # before/after versions and file lists of 3 real cases
├── eval/                 # design, answer keys, raw reports and results of both rounds
├── assets/compare.png    # the image at the top of this page
├── CHANGELOG.md
├── LICENSE
├── README.md
└── README.en.md
```

## License

[MIT](LICENSE) · © 2026 赵永明
