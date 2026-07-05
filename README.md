# dsa-sync

A local CLI that turns every solved LeetCode problem into a clean, auto-maintained GitHub archive — one command, no browser extensions, no OAuth.

## Why I built this

I wanted something like LeetHub, which auto-commits your solutions to GitHub as you solve problems. The catch is that LeetHub (and most tools like it) needs OAuth access to your entire GitHub account through a browser extension, and I just wasn't comfortable handing that over. So I built a local version instead: it never talks to GitHub directly. It only ever shells out to the `git` binary already on my machine, using whatever auth I've already set up — SSH key, credential manager, whatever. No tokens stored anywhere, no login screens, nothing running in the background.

## How it works

Solve a problem, then run `dsa-sync`. Type the problem number, and it pulls the title, difficulty, and topic tags from LeetCode's public (unauthenticated) API. Paste your solution in, and it scaffolds the folder, writes both READMEs, updates the repo-wide stats, commits with a message like `LC 217: Contains Duplicate`, and pushes.

```
dsa-sync v1.0.0 — syncing to ~/projects/dsa

Problem number › 217
  Fetched: 217. Contains Duplicate — Easy — Array, Hash Table
  Correct? [Y/n] › y
Language › C++ (default, Enter to accept)

Solution:
  [1] Paste here  [2] File path  [3] Empty file
Choice › 1
(paste, finish with a line containing only "EOF")

Creating LeetCode/0217-Contains-Duplicate/     done
Writing solution.cpp                           done
Writing README.md                              done
Updating .dsa-sync/problems.json               done
Regenerating root README.md                    done
git add                                        done
git commit "LC 217: Contains Duplicate"        done
git push                                       done

Synced. Total problems: 163
```

If LeetCode's API is unreachable, it just asks you for the title, difficulty, and tags manually instead of failing. It's meant to work fully offline if it has to.

## Install

```
git clone https://github.com/swapnil5053/Dsa-Sync.git
cd Dsa-Sync
pipx install .
```

Then run `dsa-sync` once. Since there's no config yet, it'll walk you through a guided first-run setup that points it at your solutions repo.

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
default_language: C++             # default answer for the language prompt
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
- Never stores credentials. It only calls `git` locally — auth is whatever your machine already has configured.
- Problem statements aren't embedded by default, out of respect for LeetCode's terms of service. The per-problem README just links to the problem instead.

## References

Helpful while building this:
[<!-- add article/link here -->]()
