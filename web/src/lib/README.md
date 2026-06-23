# Resume data

`resume.ts` imports the root `resume.json` catalog and resolves the exact `default` label at build
time. It mirrors the Python resolver rules: records must explicitly include `default`, and nested
experience or education highlights are filtered independently.

Edit `resume.json`, then run `uv run scripts/resume check` from the repository root.
