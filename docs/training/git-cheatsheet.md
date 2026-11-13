# Git Cheat Sheet (KeyGuard Local)

Type these in the VS Code terminal (**Ctrl + `**). Press **q** to exit long lists.

## Where am I? What changed?

| Command | What it does |
|---|---|
| `git status` | Which branch you're on and which files are new or changed |
| `git branch -a` | All branches. `*` = the one you're on |
| `git log --oneline --graph --all` | History of saves (commits), newest first |
| `git show --stat <id>` | Which files one save changed (for example `git show --stat 6fe39e9`) |
| `git diff` | The exact lines you changed but haven't saved yet |

## Saving work (the class rules: by name, on a branch, never `main`)

```
git switch -c <branch-name>        # make a new branch and move to it
git add <file1> <file2>            # add files BY NAME, never git add -A
git status                         # check: no .env, no secrets.toml, no keys
git commit -m "US-CART-02: cart page"
git push -u origin <branch-name>   # upload the branch (not main)
```

## Going back (safest first)

| You want to… | Command | Safe? |
|---|---|---|
| Switch to another branch | `git switch main` | ✅ Nothing is lost |
| Look at the project at an old save | `git switch --detach <id>` | ✅ Just looking. Come back with `git switch <your-branch>` |
| Undo unsaved changes to one file | `git restore <file>` | ⚠️ Those unsaved changes are gone |
| Undo a whole save, keeping a record | `git revert <id>` | ✅ Adds a new "undo" save |
| `git reset --hard` | — | ❌ Avoid: deletes work with no undo |

## Explorer colors in VS Code

| Color | Letter | Meaning |
|---|---|---|
| Green | **U** / **A** | New file, not saved to Git yet |
| Orange | **M** | Changed since the last save |
| Red | **D** | Deleted |
| No color | — | Saved and unchanged |

Folders take the color of the files inside them.

## Same things without typing

- **Switch branch:** click the branch name in the bottom-left corner of VS Code.
- **History:** Source Control (**Ctrl + Shift + G**) → **Graph**.
- **One file's history:** Explorer → **Timeline** section.
- **Undo a file's unsaved changes:** Source Control → hover the file → **↶ Discard**.
