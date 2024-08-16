import streamlit as st
from templates.sidebar import initialize_page_config, check_session_state, show_sidebar
from templates.db_connector import display_table_data, get_image_base64, save_like, remove_like, is_liked, content_based_recommendation, convert_df
import pandas as pd

initialize_page_config("wide")
st.session_state = check_session_state(st.session_state)
menu_selected = show_sidebar(1)

if st.session_state['logged_in'] and menu_selected == "Account":
    st.switch_page("pages/Account.py")
elif st.session_state['logged_in'] and menu_selected == "Home":
    search_keyword = st.text_input(" ", placeholder="Search car by keyword", label_visibility="collapsed")
    if 'search_keywords_1' not in st.session_state:
        st.session_state['search_keywords_1'] = []

    if search_keyword:
        if search_keyword not in st.session_state['search_keywords_1']:
            st.session_state['search_keywords_1'].append(search_keyword)
    
    options = st.session_state.get('search_keywords_1', None)
    selected_options = st.multiselect(" ", options, default=None if not options else st.session_state['search_keywords_1'], placeholder="The keywords you searched for", label_visibility="collapsed")

    if selected_options is not None:
        st.session_state['search_keywords_1'] = [keyword for keyword in st.session_state['search_keywords_1'] if keyword in selected_options]

    recommended_cars = content_based_recommendation(st.session_state['user_id'])
    columns, rows = display_table_data("electric_car_data", selected_options, recommended_cars)
    if columns and rows:
        df = pd.DataFrame(rows, columns=columns)
        csv = convert_df(df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='electric_car_data.csv',
            mime='text/csv',
            use_container_width=True
        )
        for row in rows:
            car_id = row[columns.index("car_id")]
            car_image = row[columns.index("car_image")]
            brand = row[columns.index("Brand")]
            model = row[columns.index("Model")]
            acceleration = row[columns.index("AccelSec")]
            top_speed = row[columns.index("TopSpeed_KmH")]
            range_km = row[columns.index("Range_Km")]
            efficiency = row[columns.index("Efficiency_WhKm")]
            fast_charge = row[columns.index("FastCharge_KmH")]
            rapid_charge = row[columns.index("RapidCharge")]
            power_train = row[columns.index("PowerTrain")]
            plug_type = row[columns.index("PlugType")]
            body_style = row[columns.index("BodyStyle")]
            seats = row[columns.index("Seats")]
            
            image_base64 = get_image_base64(car_image)
            if power_train == "FWD":
                icon1 = "&#9899;"
                icon2 = "&#9898;"
            elif power_train == "RWD":
                icon1 = "&#9898;"
                icon2 = "&#9899;"
            elif power_train == "AWD":
                icon1 = "&#9899;"
                icon2 = "&#9899;"
            
            st.markdown(f"""
                <style>
                    * {{
                        font-family: "Blinker";
                    }}
                    .car-card {{
                        display: flex;
                        align-items: center;
                        margin-bottom: 10px;
                        padding: 20px;
                        border: 4px solid #777772;
                        border-radius: 25px;
                        background-color: #f9f9f9;
                    }}
                    .car-card img {{
                        width: 250px;
                        height: auto;
                        border-radius: 15px;
                        box-shadow: 0px 0px 5px 0 rgba(0, 0, 0, 0.25);
                    }}
                    .car-details {{
                        margin-left: 20px;
                        flex: 2;
                    }}
                    .car-details p {{
                        margin: 0;
                    }}
                    .car-details strong {{
                        font-size: 1.2em;
                    }}
                    .car-info strong{{
                        font-weight: 500;
                        opacity: 0.6;
                    }}
                    .car-info p{{
                        font-weight: 300;
                    }}
                </style>
                <div class='car-card'>
                    <img src='data:image/jpg;base64,{image_base64}' alt='Car image'/>
                    <div class='car-details'>
                        <p class='car-title'><strong><strong>{brand} {model}</strong></strong></p>
                        <div style='display: flex; flex-wrap: wrap;'>
                            <div class='car-info' style='flex: 1;'>
                                <p><strong>0 - 100</strong></p>
                                <p> {acceleration} Sec</p>
                                <p><strong>Top Speed:</strong></p>
                                <p> {top_speed} km/h</p>
                            </div>
                            <div class='car-info' style='flex: 1;'>
                                <p><strong>Range:</strong></p>
                                <p> {range_km} km</p>
                                <p><strong>Efficiency:</strong></p>
                                <p> {efficiency} Wh/km</p>
                            </div>
                            <div class='car-info' style='flex: 1;'>
                                <p><strong>Fast Charge:</strong></p>
                                <p> {fast_charge} km/h</p>
                                <p><strong>Rapid Charge:</strong></p>
                                <p> {rapid_charge}</p>
                            </div>
                            <div class='car-info' style='flex: 1;'>
                                <p><strong>Power Train:</strong></p>
                                <p>{icon1}{icon2} {power_train}</p>
                                <p><strong>Plug Type:</strong></p>
                                <p> {plug_type}</p>
                            </div>
                            <div class='car-info' style='flex: 1;'>
                                <p><strong>Body Style:</strong></p>
                                <p> {body_style}</p>
                                <p><strong>Seats:</strong></p>
                                <p>&#128101;{seats}</p>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            like_label = "❤️" if is_liked(st.session_state['user_id'], car_id) else "🤍"
            if st.button(f"{like_label} Like", key=f"like_button_{car_id}", use_container_width=True):
                if like_label == "❤️":
                    remove_like(st.session_state['user_id'], car_id)
                    recommended_cars = content_based_recommendation(st.session_state['user_id'])
                    st.rerun()
                else:
                    save_like(st.session_state['user_id'], car_id)
                    recommended_cars = content_based_recommendation(st.session_state['user_id'])
                    st.rerun()
    else:
            st.write("No data found.")
elif st.session_state['logged_in'] and menu_selected == "Report":
    st.switch_page("pages/Report.py")