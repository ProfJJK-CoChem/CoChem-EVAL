# **CoChem-EVAL: Secure Grading & Canvas Sync**

## **Overview**

**CoChem-EVAL** is the instructor-side grading hub for the CoChem ecosystem. It aggregates the raw JSON telemetry from student gameplay (`CoChem-PLAY`) and code repository trace histories (`CoChem-LABS`/`CURE`), evaluating them for both physical accuracy and algorithmic complexity.

---

## **Key Design Principles**

* **AST-Based Static Grading:** Evaluating student Python notebooks via execution is a major security vulnerability (e.g. malicious scripts executing shell commands). To prevent this, EVAL parses the notebooks statically using Python's Abstract Syntax Tree (`ast`). It grades code blocks by mapping logic constructs, loops, and variables without ever executing the code itself.
* **FERPA-Compliant Data Isolation:** All student data is ingested and processed in ephemeral sandboxes. Results are mapped back to Canvas gradebook formatting locally, without exporting sensitive data to external servers.

---

## **File Topology & Components**

EVAL is structured as a lightweight Streamlit dashboard:

1. **[app.py](file:///d:/GitHub-Repo/CoChem-EVAL/app.py)** (Streamlit Application):
   * Provides the frontend instructor cockpit interface.
   * Handles user inputs (GitHub PAT tokens, organization names, assignment prefixes).
   * Generates download triggers for the compiled gradebooks and plagiarism audit logs.
   * Gracefully falls back to mock structures if the backend `core.cochem_eval_aggregator` parser is offline.

2. **`core/cochem_eval_aggregator.py`** (Expected backend parser):
   * Handles remote repository pulling, AST-weighting, and score aggregation.

---

## **Workflow & How to Run**

To launch the instructor dashboard and compile grades:

1. **Start the Dashboard**:
   Ensure `streamlit` and the requirements are installed, then boot the dashboard:
   ```bash
   streamlit run app.py
   ```

2. **Ingest Roster & Evaluate**:
   * Upload your Canvas Roster CSV.
   * Input your GitHub Credentials.
   * Click **Initiate Evaluation Pipeline** to fetch student code repos, verify ICI metrics, and check for copy-paste syntax hashes.

3. **Export Compiled Grades**:
   Download the compiled `Canvas_Gradebook_Export.csv` and upload it directly into your LMS gradebook interface.