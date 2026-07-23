# **CoChem-EVAL: Secure Grading & Canvas Sync**

## **Overview**

**CoChem-EVAL** is the instructor-side grading hub. It aggregates the raw JSON telemetry from CoChem-PLAY and student-submitted Jupyter Notebooks from CoChem-LABS, evaluating them for both accuracy and algorithmic complexity without ever exposing the instructor's computer to malicious code.

## **Scientific & Technical Trade-offs**

* **AST Static Analysis vs. Subprocess Execution:** Grading student Python code is incredibly dangerous (e.g., a student could submit a script containing os.system("rm \-rf /")). EVAL completely forbids code execution. Instead, it utilizes Python's Abstract Syntax Tree (ast) to mathematically parse the student's notebook. It grades them based on loop complexity, library usage, and logic pathways without ever turning the code "on."  
* **FERPA-Compliant Dashboards:** The Streamlit dashboard is heavily segregated. Instructors log in to see the full Canvas mapping, but students can only view their cryptographically hashed student\_id when accessing the CoChem-SCOUT Draft Board rankings.

## **Installation**

git clone \[https://github.com/CoChem/CoChem-EVAL.git\](https://github.com/CoChem/CoChem-EVAL.git)  
cd CoChem-EVAL

## **How to Run**

1. **Launch the Instructor Dashboard:**  
   streamlit run app.py  
2. **Ingest Submissions:**  
   Point the dashboard to the directory of student telemetry files.  
3. **Export to LMS:**  
   Click "Generate Gradebook". EVAL will output canvas\_gradebook\_import.csv with headers mathematically aligned to native Canvas/Blackboard ingestion formats.