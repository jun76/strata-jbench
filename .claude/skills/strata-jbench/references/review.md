<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Checking the results

## 2.5 Checking the results
1. Read `run-status/STATUS.md` and `run-status/ALERTS.log` (STATUS.md's first line gives the environment and RUN_ID).
2. `python3 -I scripts/build_cases.py` puts the results into the case list (`preview/cases/<division>/<env>/`), and
   `python3 -I scripts/build_results.py` into the charts, `preview/RESULTS.html`, and `preview/summary.csv` (every
   environment, with an `env` column); the supervisor runs both after each Tier. `preview/` reads both `results/` and
   `published/` and is for checking; it says "Preview" at the top.
   The page has one tab per Tier (an overview with the summary table first), each opening with what the Tier asks,
   its conditions, what its numbers are and how to read them; only the tab shown is drawn (`#tab-<id>` opens one, and
   a section's `#s-…` opens the tab holding it). The charts switch environments with the buttons at the top, and with
   results in two or more environments, "Across environments" appears in the overview (`?env=<env>` opens a given
   environment).
   When the same case is in several RUN_IDs of one environment, both use the RUN_ID whose name sorts last. To
   measure again under changed conditions, delete the old RUN_ID's results or use a RUN_ID that sorts later (`test-`
   RUN_IDs are never shown). Another environment is another case.
3. The coding cases' pages are judged by their capture (`scripts/page_shot.mjs`, called by the runner: the page runs
   10 s in headless Chrome over the DevTools protocol, then its errors, whether it froze and whether anything was
   drawn go into the manifest's `screenshot`; a page that answers but is never painted while requests are still open, a
   CDN not answering, is `stalled`, not frozen, and is captured again after a minute, up to four times). After changing that step, `python3 -I scripts/recheck_artifacts.py
   results/<division>/<env>/<RUN_ID>` captures a run's pages again without asking the models again (while nothing
   is measured), then rebuild the pages as in step 2.
