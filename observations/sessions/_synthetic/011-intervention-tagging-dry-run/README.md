# Synthetic Dry-Run: 011 Intervention Tagging

This is a non-counted dry-run bundle for [spec 011](../../../specs/011-intervention-tagging/spec.md). The `_synthetic` prefix keeps it out of counted POC sessions.

Purpose:

- prove the `interventions.json` schema works against a small transcript
- demonstrate same-bundle citation keys (`interventions.json#iv-001`)
- demonstrate a span-targeted `directive_redirect`
- demonstrate the H1 directive signal count (`1`)

Validation:

```bash
python -c 'from pathlib import Path; from tools.peer_session.interventions import validate_interventions_file, directive_signal_count; p=Path("observations/sessions/_synthetic/011-intervention-tagging-dry-run/interventions.json"); records=validate_interventions_file(p, transcript_path=p.with_name("transcript.md")); print(len(records), directive_signal_count(records))'
```

Expected output:

```text
2 1
```

