import streamlit as st
from templates.sidebar import initialize_page_config, check_session_state, show_sidebar
from templates.db_connector import login, register
import re
import time

initialize_page_config()
st.session_state = check_session_state(st.session_state)
menu_selected = show_sidebar(0)

if st.session_state['logged_in'] and menu_selected == "Account":
    st.markdown(f"", unsafe_allow_html=True)
    st.markdown(
                    """
                    <style>
                    :root {
                        --bg-color: #777772;
                        --typewriterSpeed: 1s;
                        --typewriterCharacters: 25;
                    }
                    body {
                        margin: 0;
                        font-family: "Source Sans Pro", sans-serif;
                        min-height: 100vh;
                        display: grid;
                        place-content: center;
                        text-align: center;
                        background: var(--bg-color);
                    }
                    .account-screen {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 65vh;
                        margin: 0px -100px;
                        background-color: #ffffff;
                        border: 4px solid #777772;
                        border-radius: 25px;
                        animation: zoomIn 0.5s ease-in-out;
                    }
                    .account-content {
                        display: flex;
                        flex-direction: column;
                        padding: 20px;
                    }
                    .account-content-item{
                        display: flex;
                        flex-direction: row;
                        justify-content: center;
                        align-items: center;
                    }
                    @keyframes zoomIn {
                        0% {
                            transform: scale(0);
                        }
                        100% {
                            transform: scale(1);
                        }
                    }
                    
                    .account-content h1 {
                        font-size: clamp(1rem, 3vw + 1rem, 4rem);
                        position: relative;
                        font-family: "Blinker";
                        position: relative;
                        width: max-content;
                        overflow: hidden;
                        color: var(--bg-color);
                        letter-spacing: 0.1em;
                    }
                    
                    .account-content h1::before,
                    .account-content h1::after {
                        content: "";
                        position: absolute;
                        top: 0;
                        right: 0;
                        bottom: 0;
                        left: 0;
                    }

                    .account-content h1::before {
                        background: #ffffff;
                        z-index: 1;
                        animation: typewriter var(--typewriterSpeed)
                            steps(var(--typewriterCharacters)) 1s forwards;
                    }

                    .account-content h1::after {
                        width: 0.125em;
                        background: var(--bg-color);
                        z-index: 2;
                        animation: typewriter var(--typewriterSpeed)
                            steps(var(--typewriterCharacters)) 1s forwards,
                            blink 750ms steps(var(--typewriterCharacters)) infinite;
                    }

                    .account-content-item form{
                        width: 100%;
                        margin: 20px;
                        color: hsl(0 0% 0% / 0.7);
                        font-size: 2rem;
                        font-weight: 400;
                        opacity: 0;
                        transform: translateY(3rem);
                        animation: fadeInUp 1s ease calc(var(--typewriterSpeed) + 1s) forwards;
                        overflow: hidden;
                    }
                    
                    .custom-button {
                        width: 100%;
                        background-color: #ffffff;
                        border: 4px solid #777772;
                        color: #777772;
                        padding: 5px 50px;
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

                    @keyframes typewriter {
                    to {
                        left: 100%;
                    }
                    }

                    @keyframes blink {
                    to {
                        background: transparent;
                    }
                    }

                    @keyframes fadeInUp {
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                    }
                    </style>
                    <div class="account-screen">
                        <div class="account-content">
                            <h1 style='text-align: center; color: #777772'>Welcome, """f"""{st.session_state['username']}""""""!</h1>
                            <div class="account-content-item">
                                <form method="get" action="/Account?">
                                    <input type="hidden" name="action" value="logout">
                                    <input class="custom-button" type="submit" value="Logout">
                                </form>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

elif st.session_state['logged_in'] and menu_selected == "Home":
    st.switch_page("pages/Home.py")
elif st.session_state['logged_in'] and menu_selected == "Report":
    st.switch_page("pages/Report.py")
else:
    if "action" in st.query_params:
        action = st.query_params["action"]
        if action == "login":
            st.markdown("<h1 style='text-align: center; color: #777772'>Login</h1>", unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                with st.toast("Logging in..."):
                    time.sleep(2)
                    login_status, user_id = login(username, password)
                    status, message = login_status.split(":", 1)
                    if status == "Success":
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['user_id'] = user_id
                        st.toast(message, icon='✅')
                        time.sleep(2)
                        st.rerun()
                    elif status == "Failed":
                        st.toast(message, icon='❌')
                    elif status == "Error":
                        st.toast(message, icon='⚠')

        elif action == "register":
            st.markdown("<h1 style='text-align: center; color: #777772'>Register</h1>", unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!])(?=\S+$).{8,}$"
            
            if st.button("Register", use_container_width=True):
                with st.toast("Registering..."):
                    time.sleep(2)
                    if not re.match(password_pattern, password):
                        st.toast("Password must contain at least 8 characters, including uppercase, lowercase, special character, and number.", icon='❌')
                    elif password != confirm_password:
                        st.toast("Passwords do not match.", icon='❌')
                    else:
                        register_status = register(username, password)
                        status, message = register_status.split(":", 1)
                        if status == "Success":
                            st.toast(message, icon='✅')
                            st.query_params.update({"action": "login"})
                            time.sleep(2)
                            st.rerun()
                        elif status == "Failed":
                            st.toast(message, icon='❌')
                        elif status == "Error":
                            st.toast(message, icon='🚨')
        elif action == "logout":
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.session_state['user_id'] = None
            st.query_params.clear()
            st.rerun()
    else:
        st.markdown(
                    """
                    <style>
                    :root {
                        --bg-color: #777772;
                        --typewriterSpeed: 1s;
                        --typewriterCharacters: 25;
                    }
                    body {
                        margin: 0;
                        font-family: "Source Sans Pro", sans-serif;
                        min-height: 100vh;
                        display: grid;
                        place-content: center;
                        text-align: center;
                        background: var(--bg-color);
                    }
                    .welcome-screen {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 65vh;
                        margin: 0px -100px;
                        background-color: #ffffff;
                        border: 4px solid #777772;
                        border-radius: 25px;
                        animation: zoomIn 0.5s ease-in-out;
                    }
                    .welcome-content {
                        display: flex;
                        flex-direction: column;
                        padding: 20px;
                    }
                    @keyframes zoomIn {
                        0% {
                            transform: scale(0);
                        }
                        100% {
                            transform: scale(1);
                        }
                    }
                    
                    .welcome-content h1 {
                        font-size: clamp(1rem, 3vw + 1rem, 4rem);
                        position: relative;
                        font-family: "Source Code Pro", monospace;
                        position: relative;
                        width: max-content;
                        overflow: hidden;
                        color: var(--bg-color);
                    }
                    
                    .welcome-content h1::before,
                    .welcome-content h1::after {
                        content: "";
                        position: absolute;
                        top: 0;
                        right: 0;
                        bottom: 0;
                        left: 0;
                    }

                    .welcome-content h1::before {
                        background: #ffffff;
                        z-index: 1;
                        animation: typewriter var(--typewriterSpeed)
                            steps(var(--typewriterCharacters)) 1s forwards;
                    }

                    .welcome-content h1::after {
                        width: 0.125em;
                        background: var(--bg-color);
                        z-index: 2;
                        animation: typewriter var(--typewriterSpeed)
                            steps(var(--typewriterCharacters)) 1s forwards,
                            blink 750ms steps(var(--typewriterCharacters)) infinite;
                    }

                    .welcome-content h2{
                        color: hsl(0 0% 0% / 0.7);
                        font-size: 2rem;
                        font-weight: 400;
                        opacity: 0;
                        transform: translateY(3rem);
                        animation: fadeInUp 1s ease calc(var(--typewriterSpeed) + 1s) forwards;
                        overflow: hidden;
                    }

                    @keyframes typewriter {
                    to {
                        left: 100%;
                    }
                    }

                    @keyframes blink {
                    to {
                        background: transparent;
                    }
                    }

                    @keyframes fadeInUp {
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                    }
                    </style>
                    <div class="welcome-screen">
                        <div class="welcome-content">
                            <h1>WELCOME TO EV DATABASE</h1>
                            <h2>You must login first to see the features.</h2>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )