import pandas as pd
import streamlit as st
import psycopg2 
##import plotly.express as px
##import SessionState
userInfo={}
head=st.title("")

@st.cache
def load_tickets(user):
    ##todo: read data for a given user.

    return data
def show_tickets(user):
    
    df = pd.DataFrame([[1, 2], [3, 4]], columns=["col1", "col2"])
    df.index = [""] * len(df)
    
    st.table(df)


def dashboard_reporter(user_data):
    head.title("Issue reporter Dashboard")
    st.success("Hello Issue Reporter"+", Please scroll down and access your dashboard")
    show_tickets(user_data)
def dashboard_employee(user_data):
    st.write("Hello employee !")
def dashboard_management(user_data):
    st.write("Hello Chief management") 
def auth(id,password,domain):
    con=createConnection()
    cursor= con.cursor()
    query="SELECT * from "+domain+" where id="+id+" and password = '"+password+"';"
    try:
        cursor.execute(query)
        record = cursor.fetchone()
        if type(record) == tuple:
            result = list(record)
            result.append(domain)
            return   result
        else:
            return None

    except Exception as error:
        cursor.execute("ROLLBACK")
        con.commit()
        st.write("Error Occured",error)
    return -1;


@st.cache(allow_output_mutation=True)
def createConnection():
    try:
        conn = psycopg2.connect(host='suleiman.db.elephantsql.com',
                        port='5432',
                        database='ncteubln',
                        user= 'ncteubln',
                        password= '2GVWH57HylcCfWVlSE2Z1NqQ0-FklkM7')
        return conn
    except(Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database", error)
    return None

head.title("Issue Management System")
option = st.selectbox('Select your domain/role?',('employees', 'issue_reporter', 'chief_management'))
st.write('Your selected domian:', option)
user_id = st.text_input("ID:")
user_password = st.text_input("Password:")

if st.button('add'):
    result = auth(user_id, user_password,option)
    if result != -1 and result != None:
        if "employees" in result:
            dashboard_employee(result)
            
        elif 'issue_reporter' in result:
            dashboard_reporter(result)
        else:
            dashboard_management(result)
    
    else:
        st.write("Please check your Credentials!")
