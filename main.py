import pandas as pd
import streamlit as st
import psycopg2 
##import plotly.express as px
##import SessionState
def auth(email,password):
    if email == password:
        return True
    else:
        return -1
@st.cache(allow_output_mutation=True)
def connection():


    conn = psycopg2.connect(host='suleiman.db.elephantsql.com',
                      port='5432',
                      database='ncteubln',
                      user= 'ncteubln',
                      password= '2GVWH57HylcCfWVlSE2Z1NqQ0-FklkM7')
    #st.write('jvndbnmvcb',conn)
    return conn
@st.cache
def get_data():
    url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
    return pd.read_csv(url)
df = get_data()
st.title("Issue Management System")
option = st.selectbox('Select your domain/role?',('Reporter', 'Management', 'Employee'))
st.write('Your selected domian:', option)
conn = insert_record2(option)
st.write('jvndbnmvcb',conn)
user_email = st.text_input("Email:")
user_password = st.text_input("Password:")
if st.button('add'):
    result = auth(user_email, user_password)
    if result != -1:
        st.write("Welcome user")
    else:
        st.write("Please check mentioned credentials!")

