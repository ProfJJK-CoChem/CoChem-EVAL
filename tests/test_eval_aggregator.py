from typing import Any, Dict, List, Optional
import os
import pytest
import pandas as pd
from pathlib import Path
from core.cochem_eval_aggregator import EvaluationOrchestrator

def test_evaluation_orchestrator_init() -> None:
    test_org = os.environ.get("GITHUB_ORG", "CoChem-University")
    orchestrator = EvaluationOrchestrator(github_token=os.environ.get("GITHUB_TOKEN"), org_name=test_org)
    assert orchestrator.org_name == test_org

@pytest.mark.parametrize("code, expected_funcs, expected_valid", [
    ("def foo():\n    return 42\n", 1, True),
    ("for i in range(10):\n    print(i)\n", 0, True),
    ("import os\nclass A:\n    pass\n", 0, True),
    ("def foo():\n    return 42\n\ndef bar():\n    pass\n", 2, True),
    ("def foo(\n", 0, False) # Syntax error
])
def test_ast_feature_extraction(code: str, expected_funcs: int, expected_valid: bool) -> None:
    orchestrator = EvaluationOrchestrator()
    res = orchestrator._extract_ast_features(code)
    assert res.valid is expected_valid
    assert res.functions == expected_funcs

def test_process_roster(tmp_path) -> None:
    roster_file = tmp_path / "roster_actual.csv"
    df = pd.DataFrame([
        {"Student": "Student Alpha", "ID": "101", "SIS User ID": "101", "SIS Login ID": "student_alpha", "Section": "A"},
        {"Student": "Student Beta", "ID": "102", "SIS User ID": "102", "SIS Login ID": "student_beta", "Section": "A"}
    ])
    df.to_csv(roster_file, index=False)
    
    repo_a = tmp_path / "HW1-IntroChem-student_alpha"
    repo_a.mkdir()
    (repo_a / "submission.py").write_text("def my_func():\n    return 1\n", encoding="utf-8")
    
    repo_b = tmp_path / "HW1-IntroChem-student_beta"
    repo_b.mkdir()
    (repo_b / "submission.py").write_text("def my_func():\n    return 2\n", encoding="utf-8")
    
    logs = []
    orchestrator = EvaluationOrchestrator(ui_status_callback=lambda msg: logs.append(msg))
    canvas_df, audit_df = orchestrator.process_roster(str(roster_file))
    
    assert len(canvas_df) == 2
    assert len(audit_df) == 2
    assert "Grade" in canvas_df.columns
    assert "Plagiarism_Flag" in audit_df.columns
    assert len(logs) > 0

def test_eval_rai_and_exporter(tmp_path) -> None:
    from core.cochem_eval_rai import RAIScorer
    from core.cochem_eval_export import LMSExporter

    scorer = RAIScorer(default_k=5.0)
    score1 = scorer.calculate_rai(100.0, 0)
    score2 = scorer.calculate_rai(100.0, 5)
    assert score1 == 100.0
    assert score2 < 100.0

    exporter = LMSExporter()
    df = pd.DataFrame([{"Student": "Student Alpha", "ID": "S101", "Grade": 95.0}])
    canvas_path = exporter.export_canvas(df, tmp_path / "canvas_actual.csv", anonymize=True)
    assert canvas_path.exists()

def test_eval_scout_and_telemetry() -> None:
    from core.scout_heuristic import PIRecruitmentScout
    from core.cochem_eval_telemetry import EvalTelemetryCollector

    collector = EvalTelemetryCollector("Student_001")
    collector.log_rotation(30.0)
    collector.log_hint_request(1)
    summary = collector.get_summary()
    assert summary.webgl_rotations == 1

    scout = PIRecruitmentScout()
    rpi = scout.calculate_rpi(30.0, 20, 8)
    assert rpi > 0

def test_eval_authenticator(tmp_path: Path) -> None:
    from core.cochem_eval_authenticator import SubmissionAuthenticator
    os.environ["COCHEM_EVAL_SECRET"] = os.environ.get("COCHEM_EVAL_SECRET", "default_secret_key_01")
    auth = SubmissionAuthenticator()
    
    sub_file = tmp_path / "sub.sha256"
    sub_file.write_text('{"student_id": "U123", "dataset_hash": "abc"}')
    res = auth.verify_submission(sub_file)
    assert res.is_authenticated is True
    assert res.student_id == "U123"