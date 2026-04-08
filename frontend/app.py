import streamlit as st
from backend.orchestrator import run

st.title("AI City Brain")
st.subheader("Urban Traffic Intelligence System")

user_input = st.text_input("Enter a scenario:", "Rain at 6 PM in Whitefield")

if st.button("Analyze"):
    with st.spinner("Processing..."):
        result = run(user_input)
    st.success("Analysis Complete")
    st.metric("Congestion Level", result.get("congestion", "-"))
    st.metric("Recommended Mode", result.get("recommended_mode", "-"))
    st.write("**Explanation:**", result.get("explanation", "-"))
    st.json(result)