import streamlit as st
st.set_page_config(initial_sidebar_state="collapsed")



titl = st.markdown("""<h1 style="font-weight: bold  ">VibeCheck✅</h1>
""",unsafe_allow_html=True)

col1,col2 = st.columns(2)

with col1:
    st.page_link("pages/YouTube.py", label=r'''$\textsf{\Large YouTube}$''', icon = "▶️")
with col2:
    st.page_link("pages/Facebook.py", label=r'''$\textsf{\Large Facebook}$''', icon="📕")
    


    


