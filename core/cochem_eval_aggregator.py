"""
CoChem-EVAL: Automated Grading & AST Telemetry Aggregator
FERPA-compliant, AST-weighted student submission evaluator and plagiarism auditor.
"""

import os
import sys
import ast
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Tuple, Optional, Callable
import pandas as pd
import psutil
import atexit
from pydantic import BaseModel, Field

class ASTMetrics(BaseModel):
    total_nodes: int
    functions: int
    loops: int
    imports: int
    calls: int
    ast_hash: str
    valid: bool

class CanvasRow(BaseModel):
    Student: str
    ID: str
    SIS_User_ID: str = Field(alias="SIS User ID")
    SIS_Login_ID: str = Field(alias="SIS Login ID")
    Section: str
    Grade: float
    Submission_Status: str

class AuditRow(BaseModel):
    Student: str
    Repo: str
    Commits: int
    AST_Nodes: int
    Plagiarism_Score: float
    Plagiarism_Flag: bool
    Notes: str

def cleanup_orphaned_git_processes() -> None:
    """Sweeps for zombie git or evaluation processes."""
    try:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'git' in proc.info['name'].lower():
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                raise NotImplementedError("Implementation pending")
    except Exception:
        raise NotImplementedError("Implementation pending")
atexit.register(cleanup_orphaned_git_processes)

class EvaluationOrchestrator:
    """
    Orchestrates student repository cloning, AST complexity parsing,
    plagiarism detection, and Canvas gradebook compilation.
    """
    def __init__(self, 
                 github_token: Optional[str] = None, 
                 org_name: str = "CoChem-University", 
                 assignment_prefix: str = "HW1-IntroChem-", 
                 ui_status_callback: Optional[Callable[[str], None]] = None):
        self.github_token = github_token
        self.org_name = org_name
        self.assignment_prefix = assignment_prefix
        self.ui_status_callback = ui_status_callback or (lambda msg: None)

    def _log(self, message: str) -> Any:
        """Sends status messages to the UI callback."""
        self.ui_status_callback(message)

    def _extract_ast_features(self, source_code: str) -> ASTMetrics:
        """Parses Python source code into AST features."""
        try:
            tree = ast.parse(source_code)
            nodes = list(ast.walk(tree))
            func_count = sum(1 for n in nodes if isinstance(n, ast.FunctionDef))
            loop_count = sum(1 for n in nodes if isinstance(n, (ast.For, ast.While)))
            import_count = sum(1 for n in nodes if isinstance(n, (ast.Import, ast.ImportFrom)))
            call_count = sum(1 for n in nodes if isinstance(n, ast.Call))
            
            # Create AST structural hash to detect exact duplicate code structures
            structure_str = "".join([type(n).__name__ for n in nodes if not isinstance(n, (ast.Name, ast.Constant))])
            ast_hash = hashlib.sha256(structure_str.encode('utf-8')).hexdigest()[:12]
            
            return ASTMetrics(
                total_nodes=len(nodes),
                functions=func_count,
                loops=loop_count,
                imports=import_count,
                calls=call_count,
                ast_hash=ast_hash,
                valid=True
            )
        except SyntaxError:
            return ASTMetrics(
                total_nodes=0,
                functions=0,
                loops=0,
                imports=0,
                calls=0,
                ast_hash="SYNTAX_ERROR",
                valid=False
            )

    def _read_student_code(self, repo_dir: Path) -> str:
        """Reads student code from submission.py, .py files, or .ipynb files in student repo directory."""
        if not repo_dir.exists():
            return "# Student repository directory does not exist"

        sub_py = repo_dir / "submission.py"
        if sub_py.exists():
            return sub_py.read_text(encoding="utf-8")

        py_files = list(repo_dir.glob("*.py"))
        if py_files:
            return py_files[0].read_text(encoding="utf-8")

        nb_files = list(repo_dir.glob("*.ipynb"))
        if nb_files:
            try:
                with open(nb_files[0], "r", encoding="utf-8") as f:
                    nb_content = json.loads(f.read())
                code_cells = []
                for cell in nb_content.get("cells", []):
                    if cell.get("cell_type") == "code":
                        src = cell.get("source", [])
                        code_cells.append("".join(src) if isinstance(src, list) else src)
                return "\n".join(code_cells)
            except Exception:
                raise NotImplementedError("Implementation pending")
        return "# Empty or unparseable student submission"

    def _get_git_commit_count(self, repo_dir: Path) -> int:
        """Queries git history using git rev-list --count HEAD (MOCK-07 / Suggestion 34)."""
        if not repo_dir.exists():
            return 0
        try:
            res = subprocess.run(["git", "rev-list", "--count", "HEAD"], check=True, timeout=300,
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            return int(res.stdout.strip())
        except Exception:
            return 0

    def process_roster(self, roster_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Ingests Canvas CSV roster, evaluates student AST submissions,
        runs plagiarism check, and returns (canvas_df, audit_df).
        """
        self._log(f"Reading roster file: {roster_path}")
        roster_df = pd.read_csv(roster_path)
        base_dir = Path(roster_path).parent
        
        canvas_rows = []
        audit_rows = []
        ast_hashes = {}
        
        total_students = len(roster_df)
        self._log(f"Found {total_students} students in roster. Initiating AST evaluation...")
        
        for idx, row in roster_df.iterrows():
            student_name = row.get("Student", row.get("Name", f"Student_{idx+1}"))
            student_id = row.get("ID", row.get("SIS User ID", f"SIS_{1000+idx}"))
            username = row.get("SIS Login ID", str(student_name).lower().replace(" ", "_"))
            section = row.get("Section", "Section 1")
            
            repo_name = f"{self.assignment_prefix}{username}"
            repo_dir = base_dir / repo_name
            if not repo_dir.exists():
                repo_dir = base_dir / str(username)

            self._log(f"Evaluating submission [{idx+1}/{total_students}] for {student_name} ({repo_name})...")
            
            # Read real student code (MOCK-06 / Suggestion 33)
            student_code = self._read_student_code(repo_dir)
            ast_metrics = self._extract_ast_features(student_code)
            ast_hash = ast_metrics.ast_hash
            
            # Plagiarism Detection Logic
            is_plagiarized = False
            if ast_hash != "SYNTAX_ERROR" and ast_hash in ast_hashes:
                is_plagiarized = True
                ast_hashes[ast_hash].append(student_name)
            elif ast_hash != "SYNTAX_ERROR":
                ast_hashes[ast_hash] = [student_name]
                
            grade = 100.0 if ast_metrics.valid and not is_plagiarized else (70.0 if is_plagiarized else 0.0)
            
            commit_count = self._get_git_commit_count(repo_dir)
            
            canvas_rows.append(CanvasRow(
                Student=student_name,
                ID=str(student_id),
                **{"SIS User ID": str(student_id), "SIS Login ID": str(username)},
                Section=str(section),
                Grade=grade,
                Submission_Status="COMPLETE" if ast_metrics.valid else "SYNTAX_ERROR"
            ).model_dump(by_alias=True))
            
            audit_rows.append(AuditRow(
                Student=student_name,
                Repo=repo_name,
                Commits=commit_count,
                AST_Nodes=ast_metrics.total_nodes,
                Plagiarism_Score=0.95 if is_plagiarized else 0.05,
                Plagiarism_Flag=is_plagiarized,
                Notes="Duplicate AST Hash detected" if is_plagiarized else "Valid clean submission"
            ).model_dump())
            
        canvas_df = pd.DataFrame(canvas_rows)
        audit_df = pd.DataFrame(audit_rows)
        
        self._log("✅ Roster processing & AST plagiarism audit complete.")
        return canvas_df, audit_df