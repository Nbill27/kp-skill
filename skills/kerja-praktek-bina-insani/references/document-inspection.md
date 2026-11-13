# Document Inspection — Hidden Characters and Provenance Metadata

## Purpose

Inspect documents for text-integrity and metadata issues that can affect rendering, search, interoperability, privacy, or recordkeeping. This is not an authorship detector and must not be represented as proof that text was or was not written by AI.

## Distinguish the layers

| Layer | Examples | What inspection can establish |
|---|---|---|
| Invisible or unusual Unicode | zero-width characters, bidi controls, unusual spaces, tag characters, homoglyphs | Presence and count of code points; context and likely effect |
| File metadata | EXIF, XMP, PDF document properties, Office custom properties | Which metadata fields exist and whether they expose private information |
| Provenance credentials | C2PA / Content Credentials and related manifests | Whether a recognized manifest or credential is present and whether a verifier can validate it |
| Statistical text watermark | Token-sampling patterns that may require a specific detector/key/model | Only a detector-specific score or hypothesis; not definitive authorship evidence |
| Visible graphic watermark | Text/logo overlay embedded in pixels | Requires image inspection and may be destructive to remove |

## Default workflow: inspect first

1. Identify file type, source, owner, and user authorization.
2. Preserve the original file unchanged; perform inspection on a copy when feasible.
3. Inspect the actual file bytes and supported metadata containers. Never infer from the filename alone.
4. Report findings by layer, including tool/backend availability and limitations.
5. Explain which findings are deterministic (e.g., a specific Unicode code point was found) and which are probabilistic or unsupported.
6. Ask for explicit confirmation before any destructive clean operation unless the user explicitly requested a safe, authorized cleanup in the same request.
7. Save cleaned output to a new filename; never overwrite the only original.
8. Re-inspect the output and provide a before/after report.

## Safe cleanup use cases

When the user owns the content or has authorization, supported cleanup may be appropriate for:
- Removing accidental zero-width or malformed control characters that break search, copying, or rendering.
- Removing private location/device metadata before public sharing, where provenance retention is not required.
- Normalizing whitespace and Unicode representation for interoperability.
- Cleaning metadata from a derivative copy when the original must remain intact and no retention rule requires the metadata.

## Prohibited purpose and preservation rules

Do not remove or alter copyright notices, source attribution, signatures, audit trails, legally or institutionally required provenance credentials, or ownership marks to misrepresent authorship, evade academic review, conceal the origin of a document, or pass another party's work off as the user's own.

For academic KP work, retain required acknowledgements, citations, authorship declarations, supervisor/company approvals, and any provenance information required by campus policy. When uncertain, inspect and report only; ask the supervisor or document owner before removal.

## Tooling

Two tool paths exist for the `watermarks-remover` project; see `watermarks-remover.md` for install, commands, and limits:

- **Local CLI** — text/Unicode and stylometry checks, no server required.
- **HTTP service** — PDF, Office, image, audio, and video layers plus optional detector backends.

A skill installation alone does not install or start either path. Never claim an operation ran unless you obtained a real response from the tool or service, or ran the CLI and read its output.

## Suggested report

| Item | Result |
|---|---|
| Input file | [name/type/size] |
| Authorization | [confirmed / not confirmed] |
| Tool path and version | [CLI command + version, service version, or not run] |
| Layer inspected | [Unicode / metadata / C2PA / statistical / pixel] |
| Findings | [specific facts] |
| Confidence/limitations | [deterministic or probabilistic; backend gaps] |
| Action | [inspect only / cleaned authorized copy / not performed] |
| Output | [new filename or none] |
| Integrity check | [before/after results] |
