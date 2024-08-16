import mysql.connector
from mysql.connector import Error
from templates.db_config import host, database, user, password
import bcrypt
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import random
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt

def connect():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            print("Connected to MySQL Database")
            return conn

    except mysql.connector.Error as e:
        print(f"Error Connecting to MySQL Database: {e}")
        return None

def close(conn):
    conn.close()
    print('Connection to MySQL Database Closed')
    
def login(username, password):
    conn = connect()
    
    if conn:
        try:
            cursor = conn.cursor(prepared=True)
            cursor.execute("SELECT user_id, password FROM users WHERE username=%s", (username,))
            user_data = cursor.fetchone()
            cursor.close()
            close(conn)
            if user_data:
                user_id = user_data[0]
                hashed_password = user_data[1]
                if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                    return "Success:Login successful.", user_id
            return "Failed:Incorrect username or password.", None
        except Error as e:
            print(e)
            close(conn)
            return "Error:Try Again Login Error.", None

def register(username, password):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor(prepared=True)
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result[0] > 0:
                cursor.close()
                close(conn)
                return "Failed:Username already exists, cannot register."

            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cursor.close()
            close(conn)
            return "Success:Registration successful."
        except Error as e:
            print(e)
            close(conn)
            return "Error:Try again registration error."

@st.cache_data(ttl=600)
def display_table_data(table_name, selected_options=None, recommended_cars=None, display_option='Streamlit Data Frame'):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            if display_option == 'Streamlit Markdown':
                if total_rows > 100000:
                    cursor.execute(f"SELECT * FROM {table_name} ORDER BY RAND() LIMIT 100000")
                else:
                    cursor.execute(f"SELECT * FROM {table_name}")
            elif display_option == 'Streamlit Data Frame':
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY RAND() LIMIT 10000")
            else:
                cursor.execute(f"SELECT * FROM {table_name}")
                
            results = cursor.fetchall()
            random.shuffle(results)
            if recommended_cars:
                recommended_car_ids = set([car[0] for car in recommended_cars])
                recommended_rows = [row for row in results if row[0] in recommended_car_ids]
                other_rows = [row for row in results if row[0] not in recommended_car_ids]
                results = recommended_rows + other_rows

            if selected_options:
                for keyword in selected_options:
                    results = [result for result in results if keyword.lower() in ' '.join(map(str, result)).lower()]

            cursor.close()
            close(conn)
            return column_names, results
        except Error as e:
            print(e)
            close(conn)
            return None, None
    return None, None

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
def is_liked(user_id, car_id):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_likes WHERE user_id = %s AND car_id = %s", (user_id, car_id))
            existing_like = cursor.fetchone()
            cursor.close()
            close(conn)
            return existing_like is not None
        except Error as e:
            print(e)
            close(conn)
            return False
    
def save_like(user_id, car_id):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_likes WHERE user_id = %s AND car_id = %s", (user_id, car_id))
            existing_like = cursor.fetchone()

            if existing_like:
                cursor.execute("UPDATE user_likes SET user_id = %s, car_id = %s WHERE id = %s", (user_id, car_id, existing_like[0]))
            else:
                cursor.execute("INSERT INTO user_likes (user_id, car_id) VALUES (%s, %s)", (user_id, car_id))

            conn.commit()
            cursor.close()
            close(conn)
            return True
        except Error as e:
            print(e)
            close(conn)
            return False
    return False

def remove_like(user_id, car_id):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_likes WHERE user_id = %s AND car_id = %s", (user_id, car_id))
            conn.commit()
            cursor.close()
            close(conn)
            return True
        except Error as e:
            print(e)
            close(conn)
            return False
    return False

def preprocess_car_features(car_info):
    features = ' '.join([str(car_info[0]), car_info[2], car_info[3], str(car_info[4]), str(car_info[5]), str(car_info[6]),
                         str(car_info[7]), str(car_info[8]), str(car_info[9]), car_info[10], car_info[11],
                         car_info[12], str(car_info[13])])
    return features

def content_based_recommendation(user_id):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute(f"SELECT car_id FROM user_likes WHERE user_id = {user_id}")
            liked_cars = cursor.fetchall()
            print("Liked cars: ", liked_cars)
            if not liked_cars:
                return []

            liked_car_ids = [car_id for (car_id,) in liked_cars]
            cursor.execute(f"SELECT * FROM electric_car_data WHERE car_id IN ({','.join(map(str, liked_car_ids))})")
            liked_cars_info = cursor.fetchall()
            print("Liked cars info: ", liked_cars_info)
            
            liked_car_features = [preprocess_car_features(car_info) for car_info in liked_cars_info]
            print("Liked car features: ", liked_car_features)

            cursor.execute("SELECT * FROM electric_car_data")
            all_cars_info = cursor.fetchall()
            all_car_features = [preprocess_car_features(car_info) for car_info in all_cars_info]
            print("All car features: ", all_car_features)

            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform(all_car_features)
            print("TF-IDF Matrix: ", tfidf_matrix)

            knn = NearestNeighbors(n_neighbors=10, algorithm='auto', metric='cosine')
            knn.fit(tfidf_matrix)

            liked_tfidf_matrix = tfidf_vectorizer.transform(liked_car_features)

            distances, indices = knn.kneighbors(liked_tfidf_matrix, n_neighbors=10)
            print("Distances: ", distances)
            print("Indices: ", indices)

            recommended_car_ids = set()
            for idx_list in indices:
                for idx in idx_list:
                    car_id = all_cars_info[idx][0]
                    if car_id not in liked_car_ids:
                        recommended_car_ids.add(car_id)

            recommended_car_ids = list(recommended_car_ids)[:10]
            print("Recommended car ids: ", recommended_car_ids)

            recommended_cars = [car_info for car_info in all_cars_info if car_info[0] in recommended_car_ids]
            print("Recommended cars info: ", recommended_cars)

            cursor.close()
            close(conn)
            return recommended_cars
        except Error as e:
            print(e)
            close(conn)
            return None
    return None

@st.cache_data(ttl=600)
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_resource(ttl=600)
def read_data(file_path):
    df = pd.read_csv(file_path)
    return df

@st.cache_data(ttl=600)
def visualize_data(df, selected_columns, chart_type):
    if selected_columns and chart_type:
        for column in selected_columns:
            if chart_type == "Bar Chart":
                data = df[column].value_counts().reset_index()
                data.columns = [column, 'count']
                st.bar_chart(data.set_index(column))
            
            elif chart_type == "Pie Chart" or chart_type == "Donut Chart":
                data = df[column].value_counts().reset_index()
                data.columns = [column, 'count']
                data['percentage'] = data['count'] / data['count'].sum()
                chart = alt.Chart(data).mark_arc(innerRadius=50 if chart_type == "Donut Chart" else 0).encode(
                    theta=alt.Theta(field="percentage", type="quantitative"),
                    color=alt.Color(field=column, type="nominal"),
                    tooltip=[alt.Tooltip(field=column), alt.Tooltip(field="count"), alt.Tooltip(field="percentage", format='.1%')]
                ).properties(title=f"Distribution of {column}")
                st.altair_chart(chart, use_container_width=True)
            
            elif chart_type == "Histogram":
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(df[column], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
                ax.set_title(f"Histogram of {column}")
                ax.set_xlabel(column)
                ax.set_ylabel("Frequency")
                ax.grid(axis='y', alpha=0.75)
                st.pyplot(fig)
            
            elif chart_type == "Area Chart":
                st.area_chart(df[[column]])
            
            elif chart_type == "Line Chart":
                st.line_chart(df[[column]])
                    
            elif chart_type == "Scatter Plot":
                st.plotly_chart(px.scatter(df, x=column, y=df[column].index, title=f"Scatter Plot of {column}"))
            
            elif chart_type == "Box Plot":
                st.plotly_chart(px.box(df, y=column, title=f"Box Plot of {column}"))
            
            elif chart_type == "Violin Plot":
                st.plotly_chart(px.violin(df, y=column, title=f"Violin Plot of {column}"))
    else:
        st.write("Select at least one column and chart type to display.")
        
@st.cache_data(ttl=600)
def get_columns_by_chart_type(df, chart_type):
    numeric_columns = df.select_dtypes(include=['int', 'float']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    columns_list = []

    if chart_type == "Bar Chart" or chart_type == "Pie Chart" or chart_type == "Donut Chart":
        columns_list = categorical_columns
    elif chart_type == "Histogram" or chart_type == "Box Plot" or chart_type == "Violin Plot":
        columns_list = numeric_columns
    elif chart_type == "Area Chart" or chart_type == "Line Chart" or chart_type == "Scatter Plot":
        columns_list = numeric_columns + categorical_columns

    return columns_list