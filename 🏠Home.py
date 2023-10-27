import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

st.write("# 🔮 Crystal Content Manager 🕺")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    Welcome to Crystal's content manager. 
    This tool is designed to help manage All-Things Crystal content.
    **👈 Select a page from the sidebar** to view/edit content
    
    ### Want to learn more?
    Well, you can't. This is a private tool. 😎
"""
)
st.divider()
st.write("## 📚 Resources")

st.markdown("This is the resource part of the page... but it's empty 😞")


st.divider()
st.write("##  Drew Bot 🤖")
st.markdown("Get drewbot to write content stuff for you... work in progress 🚧")
