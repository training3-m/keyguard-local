# Archive

Old or alternative requirement sets live here. **Nothing in `archive/` is used to build the app.** Only `docs/requirements/` is the active set.

## Contents

| Folder | Set | Summary |
|---|---|---|
| `requirements-civickey/` | **CivicKey Store** (older, alternative) | Calm civic design. Owner-only management with no customer accounts or staff. Orders saved as JSON in `data/orders/`. No confirmation email file. |
| `requirements-keyguard/` | **KeyGuard Local** (current, v2.0) | *Created only if you swap.* Gaming/RGB design, customer accounts with sign-in required, staff and owner roles, `.eml` emails in `outbox/`. |

The active set today is **KeyGuard Local**, in `docs/requirements/` (`00-` to `03-` files).

## Swapping sets

Run these from the project root in PowerShell. Each swap first moves the active set into `archive/`, so nothing is lost.

### Use CivicKey instead of KeyGuard

```powershell
New-Item -ItemType Directory -Force archive\requirements-keyguard | Out-Null
Move-Item docs\requirements\0*.md archive\requirements-keyguard\
Move-Item archive\requirements-civickey\*.md docs\requirements\
```

### Switch back to KeyGuard

```powershell
Move-Item docs\requirements\*.md archive\requirements-civickey\
Move-Item archive\requirements-keyguard\0*.md docs\requirements\
```

After any swap, update the "Active set" line above and the README in the project root if needed.

## Rules

- Keep one set per folder, named `requirements-<name>/`.
- Never mix files from two sets in `docs/requirements/`. The sets disagree on design, roles and how orders are saved.
- `.gitkeep` in `docs/requirements/` stays where it is. The commands above only move `.md` files.
