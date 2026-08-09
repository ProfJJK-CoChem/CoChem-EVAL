import os
import pytest
import pandas as pd
from pathlib import Path
from core.cochem_eval_aggregator import EvaluationOrchestrator

def test_evaluation_orchestrator_init():
    orchestrator = EvaluationOrchestrator(github_token="fake_token", org_name="TestOrg")
    assert orchestrator.org_name == "TestOrg"

def test_ast_feature_extraction():
    orchestrator = EvaluationOrchestrator()
    code = "def foo():\n    return 42\n"
    res = orchestrator._extract_ast_features(code)
    assert res["valid"] is True
    assert res["functions"] == 1

def test_process_roster(tmp_path):
    roster_file = tmp_path / "test_roster.csv"
    df = pd.DataFrame([
        {"Student": "Alice Smith", "ID": "101", "SIS User ID": "101", "SIS Login ID": "asmith", "Section": "A"},
        {"Student": "Bob Jones", "ID": "102", "SIS User ID": "102", "SIS Login ID": "bjones", "Section": "A"}
    ])
    df.to_csv(roster_file, index=False)
    
    logs = []
    orchestrator = EvaluationOrchestrator(ui_status_callback=lambda msg: logs.append(msg))
    canvas_df, audit_df = orchestrator.process_roster(str(roster_file))
    
    assert len(canvas_df) == 2
    assert len(audit_df) == 2
    assert "Grade" in canvas_df.columns
    assert "Plagiarism_Flag" in audit_df.columns
    assert len(logs) > 0
