import streamlit as st
from templates.sidebar import initialize_page_config, check_session_state, show_sidebar
from templates.db_connector import display_table_data, convert_df, read_data, visualize_data, get_columns_by_chart_type
import pandas as pd

initialize_page_config("wide")
st.session_state = check_session_state(st.session_state)
menu_selected = show_sidebar(2)

if st.session_state['logged_in'] and menu_selected == "Account":
    st.switch_page("pages/Account.py")
elif st.session_state['logged_in'] and menu_selected == "Home":
    st.switch_page("pages/Home.py")
elif st.session_state['logged_in'] and menu_selected == "Report":
    st.markdown("<h1 style='text-align:center; padding: 3rem 0; font-family: Blinker; font-size:50px;background-color:white; margin-bottom:1rem; border-radius:15px;box-shadow: 0 .2rem .2rem #0005; '>WASHINGTON STATE<br>EV REGISTRATION ACTIVITY</h1>", unsafe_allow_html=True)
    search_keyword = st.text_input(" ", placeholder="Search car by keyword", label_visibility="collapsed")
    if 'search_keywords_2' not in st.session_state:
        st.session_state['search_keywords_2'] = []

    if search_keyword:
        if search_keyword not in st.session_state['search_keywords_2']:
            st.session_state['search_keywords_2'].append(search_keyword)
    
    options = st.session_state.get('search_keywords_2', None)
    selected_options = st.multiselect(" ", options, default=None if not options else st.session_state['search_keywords_2'], placeholder="The keywords you searched for", label_visibility="collapsed")
    
    if selected_options is not None:
        st.session_state['search_keywords_2'] = [keyword for keyword in st.session_state['search_keywords_2'] if keyword in selected_options]
    
    display_option = st.selectbox("Choose display format:", ('Streamlit Data Frame','Streamlit Markdown'))
    
    columns, rows = display_table_data("ev_registration", selected_options, display_option)
    if columns and rows:
        df = pd.DataFrame(rows, columns=columns)
        csv = convert_df(df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='ev_registration.csv',
            mime='text/csv',
            use_container_width=True
        )
        if display_option == 'Streamlit Markdown':
            html_table = f"<table  id='registration_table'><thead><tr>{''.join(['<th><div class=''header'f'><label>{col}</label></div></th>' for col in columns])}</tr></thead><tbody>"
            for row in rows:
                html_table += f"<tr>{''.join([f'<td>{cell}</td>' for cell in row])}</tr>"
            html_table += "</tbody></table>"
            html_code=f"""
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        font-family: "Blinker";
                    }}
                    
                    @media print {{
                        .table, .table__body {{
                            overflow: visible;
                            height: auto !important;
                            width: auto !important;
                        }}
                    }}
                    
                    body {{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    
                    main.table {{
                        height: 50vh;
                        padding: 2rem;
                        background-color: #ffffff;
                        backdrop-filter: blur(7px);
                        box-shadow: 0 .2rem .4rem #0005;
                        border-radius: .8rem;
                        overflow: hidden;
                        line-height: 1;
                    }}
                    
                    
                    .table__body {{
                        width: 100%;
                        max-height: calc(95% - 1rem);
                        background-color: #fffb;

                        margin: .8rem auto;
                        border-radius: .6rem;

                        overflow: auto;
                        overflow: overlay;
                    }}

                    .table__body::-webkit-scrollbar{{
                        width: 0.5rem;
                        height: 0.5rem;
                    }}

                    .table__body::-webkit-scrollbar-thumb{{
                        border-radius: .5rem;
                        background-color: #0004;
                        visibility: hidden;
                    }}

                    .table__body:hover::-webkit-scrollbar-thumb{{
                        visibility: visible;
                    }}

                    table {{
                        width: 100%;
                    }}
                    
                    table, th, td {{
                        border-collapse: collapse;
                        padding: 1rem;
                        text-align: center;
                    }}

                    thead th {{
                        position: sticky;
                        top: 0;
                        left: 0;
                        background-color: #777772;
                        cursor: pointer;
                        text-transform: capitalize;
                        white-space: nowrap;
                        height: 4rem;
                        color: #fff;
                    }}

                    thead tr th .header{{
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }}
                    
                    tbody tr:nth-child(even) {{
                        background-color: #0000000b;
                    }}

                    tbody tr {{
                        --delay: .1s;
                        transition: .5s ease-in-out var(--delay), background-color 0s;
                    }}

                    tbody tr.hide {{
                        opacity: 0;
                        transform: translateX(100%);
                    }}

                    tbody tr:hover {{
                        background-color: #0002 !important;
                    }}
                    
                    tbody tr td {{
                        transition: .2s ease-in-out;
                    }}
                    
                    tbody tr.hide td {{
                        padding: 0;
                        font: 0 / 0 sans-serif;
                        transition: .2s ease-in-out .5s;
                    }}
                </style>
                <body>
                    <main class="table">
                        <section class='table__body' id="tableBody">
                            {html_table}
                        </section>
                    </main>
                </body>
            """
            st.markdown(html_code, unsafe_allow_html=True)
        else:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No data found.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        data_source = st.selectbox("Select data source:", ("Path", "Page"))
        if data_source == "Path":
            file_path = "pages/sources/ev_registration.csv"
            df = read_data(file_path)
        elif data_source == "Page":
            df = df
        if df is not None:
            with st.container(border=True):
                chart_type_1 = st.selectbox("Select chart type:", ["None", "Bar Chart", "Pie Chart", "Histogram", "Area Chart", "Line Chart", "Donut Chart", "Box Plot", "Violin Plot", "Scatter Plot"], key="chart_type_1")
                if chart_type_1 == "None":
                    st.write("Please select a chart type.")
                columns_list_1 = get_columns_by_chart_type(df, chart_type_1)
                if columns_list_1:
                    selected_columns_1 = st.multiselect("Select columns to display:", columns_list_1, key="select_columns_1")
                    visualize_data(df, selected_columns_1, chart_type_1)
                
            with st.container(border=True):
                chart_type_2 = st.selectbox("Select chart type:", ["None", "Bar Chart", "Pie Chart", "Histogram", "Area Chart", "Line Chart", "Donut Chart", "Box Plot", "Violin Plot", "Scatter Plot"], key="chart_type_2")
                if chart_type_2 == "None":
                    st.write("Please select a chart type.")
                columns_list_2 = get_columns_by_chart_type(df, chart_type_2)
                if columns_list_2:
                    selected_columns_2 = st.multiselect("Select columns to display:", columns_list_2, key="select_columns_2")
                    visualize_data(df, selected_columns_2, chart_type_2)

            with st.container(border=True):
                chart_type_3 = st.selectbox("Select chart type:", ["None", "Bar Chart", "Pie Chart", "Histogram", "Area Chart", "Line Chart", "Donut Chart", "Box Plot", "Violin Plot", "Scatter Plot"], key="chart_type_3")
                if chart_type_3 == "None":
                    st.write("Please select a chart type.")
                columns_list_3 = get_columns_by_chart_type(df, chart_type_3)
                if columns_list_3:
                    selected_columns_3 = st.multiselect("Select columns to display:", columns_list_3, key="select_columns_3")
                    visualize_data(df, selected_columns_3, chart_type_3)