# Optional `watermarks-remover` integration

Optional. This reference adds document inspection and authorized metadata/Unicode hygiene to the KP skill. It is not a built-in detector, and the KP skill must never claim a check ran unless the tool actually produced output.

Upstream project: <https://github.com/guillaumemeyer/watermarks-remover>

Two upstream tool paths are relevant:

| Path | Location upstream | Needs a server | Covers |
|---|---|---|---|
| Local CLI | `skills/clean-user-facing-text/scripts/` | No | text Unicode artifacts, text stylometry scoring |
| HTTP service | `service/scripts/server.py` | Yes | PDF, Office, image, audio, video, optional detector backends |

Use the local CLI first. Reach for the service only when a layer the CLI does not handle is in scope.

## Path A — local CLI (preferred, no service)

The upstream skill `skills/clean-user-facing-text` is self-contained: it vendors `inspect_text.py`, `clean_text.py`, `text_unicode.py`, `common.py`, and `score_stylometry.py`. Run from that skill directory with Python 3.10+.

Detect-only audit (never rewrites, lists flagged spans):

```bash
python scripts/inspect_text.py --audit report.txt
python scripts/inspect_text.py --stylometry --json report.txt
```

Deterministic Unicode/artifact pass, writing to a new file:

```bash
python scripts/clean_text.py report.txt -o report.clean.txt --stats --no-normalize-spaces
```

Rules for this path:
- `--audit` and `--stylometry` are inspection. They do not establish authorship.
- `clean_text.py` writes a separate output file. Never overwrite the only original.
- Re-run `--audit` on the output and report before/after counts.
- Do not treat a stylometry tier as a verdict on the student's work, and do not present it to the supervisor as one.

## Path B — HTTP service (formats the CLI does not cover)

Install and start it from a clone of the upstream repository; do not vendor its code into this repo without reviewing license, dependencies, and maintenance status. Upstream documents (verify against its current README, commands may change):

```bash
make serve
```

On Windows:

```powershell
py service/scripts/server.py --host 127.0.0.1 --port 8765
```

Server-side options include `--host`, `--port`, `--api-key`, and a `-V`/version flag.

Configuration used by the client side:

| Variable | Default | Meaning |
|---|---|---|
| `WATERMARKS_SERVICE_URL` | `http://127.0.0.1:8765` | Service base URL |
| `WATERMARKS_SERVER_API_KEY` | unset | Sent when the server was started with `--api-key` |

Never paste an API key into report content, chat logs, or this repository. For anything other than localhost, use HTTPS and a trusted endpoint.

Endpoints:

| Endpoint | Method | Destructive |
|---|---|---|
| `/health` | GET | no |
| `/capabilities` | GET | no |
| `/inspect` | POST | no |
| `/detect` | POST | no |
| `/clean` | POST | yes |

The service exposes additional routes beyond this list; consult its current OpenAPI contract rather than assuming a route set or option name.

Request sequence:
1. `GET /health`; if unreachable, stop and say the service is not running.
2. `GET /capabilities`; use only detectors and backends reported as available.
3. Send the file to `/inspect` or `/detect` using the current request schema.
4. Summarize the result and state its limits.
5. Only after explicit authorization and a permissible purpose, call `/clean`.
6. Write returned bytes to a new path; keep the original.
7. Re-inspect the output and report before/after status.

## What this cannot do

Do not claim the service proves AI authorship, detects every watermark, or removes every watermark. Statistical text marks are probabilistic and depend on which detector backends are installed. C2PA and vendor provenance credentials may be cryptographically verifiable but are not necessarily removable, and removing them is often inappropriate.

## Safety policy for KP

Allowed: inspect hidden Unicode or private metadata; remove accidental formatting/control artifacts; remove private device or location metadata from an authorized derivative copy when retention rules permit; normalize whitespace for interoperability.

Not allowed: strip provenance, attribution, signatures, acknowledgements, or required disclosures to misrepresent authorship, evade academic review, conceal another author's work, or pass another party's work off as the student's own. The KP humanizer in `humanizer.md` is for writing quality, not detector evasion.

When the request's purpose is to hide authorship from an evaluator, decline that purpose and offer transparent editing, citation repair, and evidence-based revision instead.
