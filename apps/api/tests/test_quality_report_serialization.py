from app.api.serializers import _normalize_quality_report


def test_normalize_quality_report_returns_structured_defects() -> None:
    report = _normalize_quality_report(
        {
            "status": "PASS",
            "defect_list": [
                {
                    "id": "QT-001",
                    "description": "Missing contact path",
                    "severity": "high",
                    "location": "workspace/frontend/app/page.tsx",
                    "suggestion": "Add contact form",
                }
            ],
            "retest_scope": ["contact area"],
            "remediation_requirement": "Fix high-severity issues before release.",
        }
    )

    assert report is not None
    assert report.status == "FAIL"
    assert report.defect_list[0].id == "QT-001"
    assert report.defect_list[0].severity == "high"
    assert report.defect_list[0].location == "workspace/frontend/app/page.tsx"
