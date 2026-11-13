## What changes

<!-- One paragraph. State the behaviour change, not the diff. -->

## Which rule owns it

<!-- reference file, and whether this is a campus requirement or a repository method -->

## Verification

- [ ] `python scripts/validate_package.py` exits 0
- [ ] `sh -n install.sh` passes (if the installer changed)
- [ ] `.\install.ps1 -DryRun` passes on Windows (if the installer changed)
- [ ] `Version` in `SKILL.md` and the newest `CHANGELOG.md` entry agree
- [ ] A `tests/prompts/` case covers the change, if behaviour changed

Validator output:

```
paste here
```

## Not verified

<!-- Anything you could not check against the guide or a real document. Say so here. -->
