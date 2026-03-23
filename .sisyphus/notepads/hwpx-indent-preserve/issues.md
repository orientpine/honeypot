# Issues — hwpx-indent-preserve

(No issues yet — will be updated during execution)

- 2026-03-23: `python -m pytest` unavailable in this environment (`python: command not found`); used `python3 -m pytest` to execute RED verification and capture evidence.
- 2026-03-23: `test_analyze_indent.py` RED run depends on the root-level fixture `dev/hwpx_indent/제안서_최종_포맷완료_v6.hwpx`; tests include an existence assertion for fast failure if fixture is missing in other environments.
- 2026-03-23: `scripts/md_merger.py` absent by design in RED phase; tests intentionally fail with "md_merger.py not found (expected RED)" to lock in TDD workflow.
- 2026-03-23: `test_xml_writer_indent.py` RED verification also requires `python3` entrypoint in this container; evidence saved to `.sisyphus/evidence/task-3-red-phase.txt` with all 8 failures.
