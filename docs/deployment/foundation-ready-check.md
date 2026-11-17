# Foundation Ready Check

The checklist from `docs/training/fast-track-playbook.md` §3.4. **All items must be true before tagging `foundation-v1`** and asking the trainer for sign-off (§3.5).

Status as of 2026-11-17: ✅ done · ⬜ to do (who).

| # | Ready-check item | Status | How it was checked / what's left |
|---|---|---|---|
| 1 | A teammate does a **fresh clone** and gets the app running by following only the README | ⬜ Teammate | README has exact Windows steps (Prompt F). Ask one teammate to try it, without help, and note anything unclear. |
| 2 | Every page in the site map opens and shows "Coming soon" without an error | ✅ | Agent API walk (guest) and AppTest page tests; checked by hand as each role |
| 3 | The demo customer, staff and owner can sign in and see the right menu; the wrong role sees "access denied" | ✅ | Checked by hand in the browser for all 3 accounts; guards tested in `tests/unit/test_app_pages.py` |
| 4 | The all-or-nothing function passes its SQL test on the dev project | ✅ | `supabase/tests/place_order_test.sql` → ALL PLACE_ORDER TESTS PASSED |
| 5 | `ruff check .` and `python -m pytest tests/unit -q` pass; CI is green on `main` | ✅ / ⬜ Lead | Pass locally (44 tests). CI is green on every pull request; confirm on `main` after merging #5–#7. |
| 6 | No `.env`, key or password in the repo: run `git ls-files` and look | ✅ | Checked before every push; the only "keys" are fakes in tests |
| 7 | `docs/architecture/service-contracts.md` lists a function for every story | ✅ | Written in Prompt E with a scripted check of all 31 stories |
| 8 | The **cloud demo** Supabase project has the migrations and seed applied, and email confirmation is off | ⬜ Lead | Follow [streamlit-cloud.md](streamlit-cloud.md) step 1 |
| 9 | **Dry run:** the Lead builds the smallest story with Prompt 3 and times it; over 30 minutes means simplify the story list | ⬜ Lead | Team story work, not done yet on purpose |

## Before tagging

1. Merge pull requests #5, #6 and #7 (in that order).
2. Apply `supabase/migrations/0009_community_total.sql` to the dev project.
3. Finish items 1, 8 and 9.
4. Then tag:

```powershell
git switch main
git pull
git tag -a foundation-v1 -m "Foundation ready"
git push origin foundation-v1
```
