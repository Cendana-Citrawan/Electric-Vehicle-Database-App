import streamlit as st
from templates.sidebar import initialize_page_config

initialize_page_config(sidebar="collapsed")

st.image("sources/Logo.png")
st.markdown("""
            <style>
                div[data-testid="collapsedControl"] {
                    display: none;
                }
            
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                    }
                    to {
                        opacity: 1;
                    }
                }

                .button-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    animation: fadeIn 0.5s;
                }

                .custom-button {
                    background-color: #ffffff;
                    border: 8px solid #777772;
                    color: #777772;
                    padding: 20px 100px;
                    text-align: center;
                    font-size: 25px;
                    margin-top: 20px;
                    cursor: pointer;
                    border-radius: 35px;
                    transition: background-color 0.3s, transform 0.3s, color 0.3s ease-in-out;
                    font-weight: bold;
                    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
                }

                .custom-button:hover {
                    background-color: #777772;
                    transform: scale(1.05);
                    color: #ffffff;
                }
                
                .custom-button:active {
                    transform: scale(0.9);
                }
                
            </style>
            <div class="button-container">
                <form action="/Account">
                    <input class="custom-button" type="submit" value="Get Started">
                </form>
            </div>
            """, unsafe_allow_html=True)