import pandas as pd
import streamlit as st
import psycopg2 
##import plotly.express as px
##import SessionState
userInfo={}
def auth(id,password,domain):
    con=createConnection()
    cursor= con.cursor()
    query="SELECT * from "+domain+" where id="+id+" and password = '"+password+"';"
    try:
        cursor.execute(query);
        record = cursor.fetchone();
        return record;
    except Exception as error:
        cursor.execute("ROLLBACK")
        con.commit()
        st.write("Error Occured",error);
    return -1;


@st.cache(allow_output_mutation=True)
def createConnection():
    try:
        conn = psycopg2.connect(host='suleiman.db.elephantsql.com',
                        port='5432',
                        database='ncteubln',
                        user= 'ncteubln',
                        password= '2GVWH57HylcCfWVlSE2Z1NqQ0-FklkM7')
        return conn;
    except(Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database", error)
    return None


st.title("Issue Management System")
option = st.selectbox('Select your domain/role?',('employees', 'issue_reporter', 'chief_management'))
st.write('Your selected domian:', option)
user_id = st.text_input("ID:")
user_password = st.text_input("Password:")
if st.button('add'):
    result = auth(user_id, user_password,option);
    if result != -1 and result != None:
        st.write("Welcome user")
    else:
        st.write("Please check your Credentials!")


def dashboard_reporter():
    st.write("Hello Issue Reporter");
def dashboard_employee():
    st.write("Hello employee !");
def dashboard_management():
    st.write("Hello Chief management"); 