from typing import Any, Dict, List, Optional
import streamlit as st
import pandas as pd
import os
import tempfile

# Graceful failure routing: Ensure backend exists before proceeding
try:
    from core.cochem_eval_aggregator import EvaluationOrchestrator
except ImportError:
    EvaluationOrchestrator = None

def highlight_plagiarism(row) -> Any:
    """
    Pandas styling function to flag anomalous submissions.
    Safely checks for the column before applying CSS.
    """
    is_flagged = row.get('Plagiarism_Flag', False)
    # Ensure boolean evaluation in case of NaNs or mixed types
    color = 'background-color: #ffcccc' if is_flagged == True else ''
    return [color] * len(row)

def main() -> Any:
    st.set_page_config(
        page_title="CoChem-EVAL | Automated Grading",
        page_icon="🧪",
        layout="wide"
    )

    # Initialize Session State for Persistent UI
    if 'canvas_df' not in st.session_state:
        st.session_state.canvas_df = None
    if 'audit_df' not in st.session_state:
        st.session_state.audit_df = None

    st.title("🧪 CoChem-EVAL Orchestrator")
    st.markdown("Automated, FERPA-compliant grading pipeline for computational chemistry workflows.")

    # Stage 4.0: App Backend Initialization (Sidebar)
    with st.sidebar:
        st.header("Pipeline Configuration")
        if EvaluationOrchestrator is None:
            st.error("Backend Error: `core.cochem_eval_aggregator` not found.", icon="🚨")
            
        gh_token = st.text_input("GitHub PAT (Requires repo scope)", type="password")
        org_name = st.text_input("GitHub Organization Name", value="CoChem-University")
        hw_prefix = st.text_input("Assignment Prefix", value="HW1-IntroChem-")
        
        st.markdown("---")
        st.warning("All cloned student data will be executed in a sandboxed, ephemeral RAM disk and purged upon completion.")

    # Main UI Panel
    st.subheader("1. Ingest Roster")
    roster_file = st.file_uploader("Upload Canvas Roster (CSV)", type=["csv"])

    if roster_file is not None:
        st.success("Roster ingested successfully. Ready for processing.")
        
        # Stage 4.1: Streamlit Callback Injection
        if st.button("🚀 Initiate Evaluation Pipeline"):
            if not gh_token:
                st.error("Execution Halted: GitHub Token is required to clone repositories.")
                st.stop()
            
            if not EvaluationOrchestrator:
                st.error("Execution Halted: Backend Orchestrator is offline. Check core modules.")
                st.stop()

            with st.status("Evaluating Submissions...", expanded=True) as status:
                st.write("Initializing ephemeral storage...")
                
                # Write uploaded roster to temporary file for the backend
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                    tmp.write(roster_file.getvalue())
                    tmp_path = tmp.name

                try:
                    # Instantiate Backend
                    orchestrator = EvaluationOrchestrator(
                        github_token=gh_token,
                        org_name=org_name,
                        assignment_prefix=hw_prefix,
                        ui_status_callback=st.write 
                    )
                    
                    st.write("Fetching repositories and triggering AST Evaluation...")
                    
                    # Store results in session state to survive widget reruns
                    c_df, a_df = orchestrator.process_roster(tmp_path)
                    st.session_state.canvas_df = c_df
                    st.session_state.audit_df = a_df
                    
                    status.update(label="Evaluation Complete! RAM Disk Purged.", state="complete", expanded=False)
                    
                except Exception as e:
                    status.update(label="Evaluation Failed", state="error")
                    st.error(f"Pipeline Error: {str(e)}")
                    st.stop()
                finally:
                    # Cleanup temp roster
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

        # Stage 4.2: Output Matrix Rendering & Export (Decoupled from Button logic)
        if st.session_state.canvas_df is not None and st.session_state.audit_df is not None:
            st.markdown("---")
            st.subheader("2. Evaluation Results")
            
            tab1, tab2 = st.tabs(["Canvas Gradebook", "Internal Audit Log"])
            
            with tab1:
                st.markdown("### Canvas Import Matrix")
                st.dataframe(st.session_state.canvas_df, use_container_width=True)
                
                csv_canvas = st.session_state.canvas_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Canvas Import CSV",
                    data=csv_canvas,
                    file_name="Canvas_Gradebook_Export.csv",
                    mime="text/csv",
                )
                
            with tab2:
                st.markdown("### AST Security & Plagiarism Audit")
                if not st.session_state.audit_df.empty and 'Plagiarism_Flag' in st.session_state.audit_df.columns:
                    styled_audit = st.session_state.audit_df.style.apply(highlight_plagiarism, axis=1)
                    st.dataframe(styled_audit, use_container_width=True)
                else:
                    st.dataframe(st.session_state.audit_df, use_container_width=True)
                
                csv_audit = st.session_state.audit_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Internal Audit Log (CSV)",
                    data=csv_audit,
                    file_name="CoChem_Audit_Log.csv",
                    mime="text/csv",
                )

if __name__ == "__main__":
    main()