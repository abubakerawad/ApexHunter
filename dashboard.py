import streamlit as st
import pandas as pd
import yaml
from apexhunter.engine import AutonomousEngine

st.set_page_config(page_title="ApexHunter Dashboard", layout="wide")

st.title("ApexHunter Dashboard")
st.markdown("Autonomous Threat Hunting Playbook Executor")

col1, col2 = st.columns(2)

with col1:
    st.header("Configuration")
    playbook_file = st.text_input("Playbook YAML Path", value="playbooks/ransomware_beacon_hunt.yaml")
    data_dir = st.text_input("Data Directory Path", value="sample_logs")
    model = st.selectbox("LLM Model", ["llama3", "phi3:medium", "mistral"])
    
    if st.button("Run Playbook"):
        with st.spinner("Running playbook execution..."):
            try:
                engine = AutonomousEngine(playbook_path=playbook_file, data_dir=data_dir, model=model)
                results = engine.run()
                st.session_state['results'] = results
                st.session_state['playbook'] = engine.playbook
                st.success("Execution completed!")
            except Exception as e:
                st.error(f"Execution failed: {e}")

with col2:
    st.header("Results")
    if 'results' in st.session_state:
        playbook = st.session_state['playbook']
        st.subheader(f"Playbook: {playbook.get('name')}")
        st.write(f"**Hypothesis:** {playbook.get('hypothesis')}")
        
        for res in st.session_state['results']:
            with st.expander(f"Step {res['step_id']}: {res['description']} ({res['hits_count']} hits)"):
                if res['hits_count'] > 0:
                    st.dataframe(pd.DataFrame(res['hits']))
                
                if res['llm_analysis']:
                    st.markdown("### LLM Analysis")
                    if 'error' in res['llm_analysis']:
                        st.error(res['llm_analysis']['error'])
                    else:
                        st.json(res['llm_analysis'])
