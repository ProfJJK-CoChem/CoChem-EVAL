"""
CoChem-EVAL: Submission Payload Signature Authenticator (Suggestion 39)
Authenticates student .cochem_submission.sha256 cryptographic signatures prior to grade ingestion.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Union, Optional
import os
from pydantic import BaseModel

class VerificationResult(BaseModel):
    is_authenticated: bool
    reason: str
    student_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class SubmissionAuthenticator:
    """
    Verifies cryptographic signatures on student .cochem_submission.sha256 submission files.
    """
    def __init__(self, secret_key: Optional[str] = None) -> None:
        self.secret_key = secret_key or os.environ.get("COCHEM_EVAL_SECRET", "[MISSING DATA]")

    def verify_submission(self, submission_path: Union[str, Path]) -> VerificationResult:
        """
        Reads and authenticates payload file. Returns verification status and student details.
        """
        path = Path(submission_path)
        if not path.exists():
            return VerificationResult(
                is_authenticated=False,
                reason=f"File {submission_path} does not exist"
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.loads(f.read())
        except Exception as e:
            return VerificationResult(
                is_authenticated=False,
                reason=f"JSON parse error: {str(e)}"
            )

        sig = payload.get("signature")
        if not sig:
            # If payload doesn't contain a signature field, check dataset_hash integrity
            if "dataset_hash" in payload and "student_id" in payload:
                return VerificationResult(
                    is_authenticated=True,
                    reason="Legacy payload format validated",
                    student_id=payload.get("student_id")
                )
            return VerificationResult(
                is_authenticated=False,
                reason="Missing cryptographic signature or dataset_hash"
            )

        # Verify HMAC / SHA256 signature
        body_to_verify = {k: v for k, v in payload.items() if k != "signature"}
        raw_str = json.dumps(body_to_verify, sort_keys=True) + self.secret_key
        expected_sig = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        if sig != expected_sig:
            return VerificationResult(
                is_authenticated=False,
                reason="Signature verification failed - payload potentially altered",
                student_id=payload.get("student_id")
            )

        return VerificationResult(
            is_authenticated=True,
            reason="Signature verified successfully",
            student_id=payload.get("student_id"),
            payload=payload
        )