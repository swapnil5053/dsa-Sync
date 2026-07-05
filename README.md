# dsa-sync

A local CLI that turns every solved LeetCode problem into a clean, auto-maintained GitHub archive — one command, no browser extensions, no OAuth.

## Why I built this

I wanted something like LeetHub, which auto-commits your solutions as you solve problems. The catch is that LeetHub, and most tools like it, need OAuth access to your entire GitHub account through a browser extension, and I never got comfortable handing that over just to keep a solutions folder in sync. So I built a local version instead. It never talks to GitHub's API directly — it only ever shells out to the `git` binary already on my machine, using whatever auth I've already set up, SSH key or credential manager, whichever. No tokens stored anywhere, no login screens, nothing running in the background.

## How it works

Solve a problem, run `dsa-sync`, type the problem number. It pulls the title, difficulty, and topic tags straight from LeetCode's public, unauthenticated API, so you don't have to type any of that yourself. Pick a language from a short numbered list, paste your solution in, and it takes care of the rest: scaffolds the folder, writes both READMEs, updates the repo-wide stats, commits with a message like `LC 217: Contains Duplicate`, and pushes.

```
dsa-sync v1.0.0 - syncing to ~/projects/dsa

Problem number: 217
  Fetched: 217. Contains Duplicate - Easy - Array, Hash Table
Correct? [y/n] (y): y
Language:
  [1] C++ (default)
  [2] Python
  [3] Java
  [4] JavaScript
  [5] TypeScript
  [6] Go
  [7] Rust
  [8] Kotlin
  [9] C#
  [10] Ruby
  [11] C
Choice (1): 2

Solution:
(paste, finish with a line containing only "EOF")

Creating LeetCode/0217-Contains-Duplicate/     done
Writing solution.py                            done
Writing README.md                              done
Updating .dsa-sync/problems.json               done
Regenerating root README.md                    done
git add                                        done
git commit "LC 217: Contains Duplicate"        done
git push                                       done

Synced. Total problems: 163
```

If LeetCode's API is unreachable, it just asks for the title, difficulty, and tags manually instead of failing outright. It's meant to work fully offline if it has to.

## Install

```
git clone https://github.com/swapnil5053/Dsa-Sync.git
cd Dsa-Sync
pipx install .
```

Run `dsa-sync` once with no config in place, and it walks you through a short guided setup that points it at your solutions repo.

## Commands

| Command | What it does |
| --- | --- |
| `dsa-sync` | Sync a newly solved problem (default, no subcommand needed) |
| `dsa-sync stats` | Print repo statistics to the terminal |
| `dsa-sync list` | List every synced problem as a table |
| `dsa-sync regenerate` | Rebuild the root README from metadata, no new problem |
| `dsa-sync check` | Integrity check: metadata, folders, and READMEs all line up |
| `dsa-sync config` | Print the config file path and current values |

## Config

Lives at `~/.config/dsa-sync/config.yaml`:

```yaml
repository_path: ~/projects/dsa   # where your solutions repo lives
leetcode_dir: LeetCode            # subfolder solutions go into
default_language: Python          # pre-selected option on the language menu
git:
  auto_push: true                 # push after every commit
  commit_prefix: "LC"             # commit messages look like "LC 217: Contains Duplicate"
readme:
  recently_solved_count: 10       # how many problems show up in "Recently Solved"
  date_format: "%Y-%m-%d"         # date format used in the root README
  embed_statement: false          # fetch and embed the full problem statement (off by default)
```

## Notes

- Works offline. If LeetCode's API can't be reached, it falls back to manual entry instead of failing.
- Never stores credentials. It only calls `git` locally, and auth is whatever your machine already has configured.
- Problem statements aren't embedded by default, out of respect for LeetCode's terms of service. The per-problem README just links back to the problem instead.

## References

Helpful while building this:
[Typer docs](https://typer.tiangolo.com/)
[Rich docs](https://rich.readthedocs.io/)
[pipx documentation](https://pipx.pypa.io/)
