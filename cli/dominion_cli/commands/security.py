"""Security scanning and findings commands."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional

import typer

from ..core.config import current_phase, dominion_path, phase_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Security analysis and tracking")


@app.command()
def scan(
    phase: Annotated[int, typer.Option("--phase", help="Phase number")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Run security analysis and write findings to security-findings.toml."""
    pp = phase_path(phase)
    pp.mkdir(parents=True, exist_ok=True)

    findings_path = pp / "security-findings.toml"
    auditor_path = dominion_path("agents", "security-auditor.toml")
    research_path = pp / "research.toml"

    auditor = read_toml_optional(auditor_path)
    research = read_toml_optional(research_path)

    # Initialize security findings structure
    sec_findings: dict = {
        "meta": {
            "phase": phase,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        },
        "findings": [],
    }

    # Pull security-related findings from research if available
    if research:
        for f in research.get("findings", []):
            if f.get("category") in ("security", "vulnerability", "dependency"):
                sec_findings["findings"].append({
                    "id": f"SF{len(sec_findings['findings']) + 1}",
                    "title": f.get("title", ""),
                    "severity": f.get("severity", "medium"),
                    "status": "new",
                    "cwe": "",
                    "category": f.get("category", ""),
                    "method": "research-referral",
                    "discovered_phase": phase,
                    "evidence": f.get("evidence", []),
                    "description": f.get("description", ""),
                    "recommendation": f.get("recommendation", ""),
                })

    write_toml(findings_path, sec_findings)

    count = len(sec_findings["findings"])
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in sec_findings["findings"]:
        sev = f.get("severity", "low")
        if sev in severity_counts:
            severity_counts[sev] += 1

    data = {
        "phase": phase,
        "total": count,
        "critical": severity_counts["critical"],
        "high": severity_counts["high"],
        "medium": severity_counts["medium"],
        "low": severity_counts["low"],
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"Security Scan (Phase {phase}):")
    info(f"  Findings: {severity_counts['critical']} critical, {severity_counts['high']} high, {severity_counts['medium']} medium, {severity_counts['low']} low")
    info("Note: Full security analysis methodology should be performed by the Security Auditor agent.")


@app.command(name="findings")
def list_findings(
    phase: Annotated[Optional[int], typer.Option("--phase", help="Phase number")] = None,
    severity: Annotated[Optional[str], typer.Option("--severity", help="Filter by severity")] = None,
    status_filter: Annotated[Optional[str], typer.Option("--status", help="Filter by status")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List security findings with filters."""
    p = phase if phase is not None else current_phase()
    pp = phase_path(p)
    sec = read_toml_optional(pp / "security-findings.toml")

    if not sec:
        info(f"No security findings for phase {p}.")
        return

    items = sec.get("findings", [])
    if severity:
        items = [f for f in items if f.get("severity") == severity]
    if status_filter:
        items = [f for f in items if f.get("status") == status_filter]

    if not items:
        info(f"No security findings match filters for phase {p}.")
        return

    columns = ["ID", "Severity", "Status", "CWE", "Title"]
    rows = []
    for f in items:
        rows.append([
            f.get("id", ""),
            f.get("severity", ""),
            f.get("status", ""),
            f.get("cwe", ""),
            f.get("title", ""),
        ])
    table(f"Security Findings (Phase {p})", columns, rows, json)


@app.command(name="finding")
def show_finding(
    id: Annotated[str, typer.Argument(help="Finding ID (e.g. SF1)")],
    phase: Annotated[Optional[int], typer.Option("--phase", help="Phase number")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show full detail for one security finding."""
    p = phase if phase is not None else current_phase()
    pp = phase_path(p)
    sec = read_toml(pp / "security-findings.toml")

    items = sec.get("findings", [])
    match = next((f for f in items if f.get("id") == id), None)

    if not match:
        info(f"Finding {id} not found in phase {p}.")
        raise SystemExit(1)

    data = {
        "id": match.get("id"),
        "title": match.get("title", ""),
        "severity": match.get("severity", ""),
        "status": match.get("status", ""),
        "cwe": match.get("cwe", ""),
        "category": match.get("category", ""),
        "method": match.get("method", ""),
        "discovered_phase": match.get("discovered_phase", ""),
        "evidence": match.get("evidence", []),
        "description": match.get("description", ""),
        "recommendation": match.get("recommendation", ""),
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"Finding: {data['id']}")
    info(f"  Title: {data['title']}")
    info(f"  Severity: {data['severity']}")
    info(f"  Status: {data['status']}")
    info(f"  CWE: {data['cwe']}")
    info(f"  Category: {data['category']}")
    info(f"  Method: {data['method']}")
    info(f"  Discovered: Phase {data['discovered_phase']}")
    if data["evidence"]:
        info("  Evidence:")
        for e in data["evidence"]:
            info(f"    - {e}")
    if data["description"]:
        info(f"  Description: {data['description']}")
    if data["recommendation"]:
        info(f"  Recommendation: {data['recommendation']}")


@app.command()
def track(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Compare security findings across phases, show remediation progress."""
    phases_dir = dominion_path("phases")
    if not phases_dir.is_dir():
        info("No phases directory found.")
        return

    all_findings: dict[int, list[dict]] = {}
    for phase_dir in sorted(phases_dir.iterdir()):
        if phase_dir.is_dir():
            try:
                phase_num = int(phase_dir.name)
            except ValueError:
                continue
            sec = read_toml_optional(phase_dir / "security-findings.toml")
            if sec:
                all_findings[phase_num] = sec.get("findings", [])

    if not all_findings:
        info("No security findings across any phase.")
        return

    # Track findings by ID across phases
    finding_tracker: dict[str, dict] = {}
    for phase_num, findings_list in sorted(all_findings.items()):
        for f in findings_list:
            fid = f.get("id", "")
            if fid not in finding_tracker:
                finding_tracker[fid] = {
                    "id": fid,
                    "cwe": f.get("cwe", ""),
                    "severity": f.get("severity", ""),
                    "latest_status": f.get("status", ""),
                    "first_phase": phase_num,
                    "last_phase": phase_num,
                }
            else:
                finding_tracker[fid]["latest_status"] = f.get("status", "")
                finding_tracker[fid]["last_phase"] = phase_num

    fixed = [f for f in finding_tracker.values() if f["latest_status"] == "fixed"]
    regressed = [f for f in finding_tracker.values() if f["latest_status"] == "regressed"]
    open_findings = [f for f in finding_tracker.values() if f["latest_status"] in ("new", "acknowledged")]

    data = {
        "phases": {str(k): len(v) for k, v in all_findings.items()},
        "fixed": [{"id": f["id"], "cwe": f["cwe"], "severity": f["severity"]} for f in fixed],
        "regressed": [{"id": f["id"], "cwe": f["cwe"], "severity": f["severity"]} for f in regressed],
        "open": [{"id": f["id"], "cwe": f["cwe"], "severity": f["severity"]} for f in open_findings],
    }

    if json:
        output(data, json_mode=True)
        return

    info("Security Tracking:")
    for phase_num, count in sorted(all_findings.items()):
        info(f"  Phase {phase_num}: {len(count)} findings")

    info("")
    info("Remediation:")
    if fixed:
        info(f"  Fixed: {', '.join(f'{f['id']} ({f['cwe']}, {f['severity']})' for f in fixed)}")
    else:
        info("  Fixed: (none)")
    if regressed:
        info(f"  Regressed: {', '.join(f'{f['id']} ({f['cwe']}, {f['severity']})' for f in regressed)}")
    else:
        info("  Regressed: (none)")
    if open_findings:
        info(f"  Open: {', '.join(f'{f['id']} ({f['cwe']}, {f['severity']})' for f in open_findings)}")
    else:
        info("  Open: (none)")
