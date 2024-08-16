import streamlit as st
from streamlit_option_menu import option_menu

def initialize_page_config(layout="centered", sidebar="expanded"):
    st.set_page_config(page_title="EV Database", page_icon="⚡", layout=layout, initial_sidebar_state=sidebar, menu_items=None)
    st.markdown("""
                <style>
                    .st-emotion-cache-79elbk {
                        display: none;
                    }
                </style>
                """, unsafe_allow_html=True)

def check_session_state(session_state):
    if 'logged_in' not in session_state:
        session_state['logged_in'] = False

    if 'username' not in session_state:
        session_state['username'] = None
        
    if 'user_id' not in session_state:
        session_state['user_id'] = None

    return session_state

def show_sidebar(selected_index=-1):
    with st.sidebar:
        st.image("sources/Logo.png", use_column_width=True)
        st.markdown("<hr style='border: 2px solid #777772; margin: 0px'>", unsafe_allow_html=True)
        if st.session_state['logged_in'] == True:
            st.query_params.clear()
            menu_selected = option_menu(
                None,
                ["Account","Home", "Report"],
                default_index=selected_index,
                styles={
                    "container": {"padding": "0!important", "background-color": "#ffffff"},
                    "icon": {"display": "none"},
                    "nav-link": {"background-color": "#ffffff", "color": "#777772", "font-size": "20px", "text-align": "center", "font-weight": "bold", "transition": "background-color 0.3s ease, color 0.3s ease", "font-family": "Blinker"},
                    "nav-link-selected": {"background-color": "#777772", "color": "#ffffff", "font-size": "20px", "text-align": "center", "font-weight": "bold", "transition": "background-color 0.3s ease, color 0.3s ease"},
                }
            )
            st.markdown("<hr style='border: 2px solid #777772; margin-top: -10px'>", unsafe_allow_html=True)
        else:
            menu_selected = option_menu(
                None,
                ["Account"],
                styles={
                    "container": {"padding": "0!important", "background-color": "#ffffff"},
                    "icon": {"display": "none"},
                    "nav-link": {"background-color": "#ffffff", "color": "#777772", "font-size": "20px", "text-align": "center", "font-weight": "bold" , "font-family": "Blinker"},
                    "nav-link-selected": {"background-color": "#777772", "color": "#ffffff", "font-size": "20px", "text-align": "center", "font-weight": "bold"},
                }
            )
            if menu_selected == "Account":
                st.markdown(
                    """
                    <style>
                    .center-screen {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin-top: -10px;
                    }
                    .center-content {
                        display: flex;
                        justify-content: space-around;
                        width: 100%;
                    }
                    .custom-button {
                        background-color: #ffffff;
                        border: 4px solid #777772;
                        color: #777772;
                        padding: 5px 40px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 20px;
                        cursor: pointer;
                        border-radius: 12px;
                        transition: background-color 0.3s, transform 0.3s, color 0.3s;
                        font-family: Blinker;
                    }
                    .custom-button:hover {
                        background-color: #777772;
                        transform: scale(0.95);
                        color: #ffffff;
                    }
                    </style>
                    <div class="center-screen">
                        <div class="center-content">
                            <form method="get" action="/Account?">
                                <input type="hidden" name="action" value="login">
                                <input class="custom-button" type="submit" value="Login">
                            </form>
                            <form method="get" action="/Account?">
                                <input type="hidden" name="action" value="register">
                                <input class="custom-button" type="submit" value="Register">
                            </form>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("<hr style='border: 2px solid #777772; margin: 0px'>", unsafe_allow_html=True)
        
        return menu_selected