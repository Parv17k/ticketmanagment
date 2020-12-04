import pandas as pd
import streamlit as st
import psycopg2 
from configparser import ConfigParser
##import plotly.express as px
import SessionState
session_state = SessionState.get(id=0,name='Parv')
head=st.title("")

def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

@st.cache
def query_db(sql: str):
    # print(f'Running query_db(): {sql}')
    try:
        db_info = get_config()

    # Connect to an existing database
        conn = psycopg2.connect(**db_info)
    except: 
        conn = createConnection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
   # cur.close()
    #conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

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

@st.cache
def load_tickets(user):
    sql=''
    if user['domain'][0]=='issue_reporter':
        sql = 'select  * from tickets where issuer_id = '+str(user['id'][0])
    elif user['domain'][0]=='employees':
        sql = 'select  * from tickets where assigned_to_id = '+str(user['id'][0])
    data=query_db(sql)
    return data
def show_tickets(user):
    st.table(load_tickets(user))


def dashboard_reporter(user_data):
    head.title("Issue reporter Dashboard")
    st.success("Hello Issue Reporter"+", Please scroll down and access your dashboard")
    show_tickets(user_data)
def dashboard_employee(user_data):
     st.success("Hello"+", Please scroll down and access your dashboard")
     show_tickets(user_data)
def dashboard_management(user_data):
     st.success("Hello Issue Reporter"+", Please scroll down and access your dashboard")
def auth(id,password,domain):

    query="SELECT * from "+domain+" where id="+id+" and password = '"+password+"';"
    try:
        df= query_db(query)
        print(df)
        return df
    except Exception as error:
        cursor.execute("ROLLBACK")
        con.commit()
        st.write("Error Occured",error)
    return 



head.title("Issue Management System")
option = st.selectbox('Select your domain/role?',('employees', 'issue_reporter', 'chief_management'))
st.write('Your selected domian:', option)
user_id = st.text_input("ID:")
user_password = st.text_input("Password:")

if st.button('add'):
    result = auth(user_id, user_password,option)
    print("Here is auth data",result)
    if result is not None :
        result['domain']=option
        if "employees" == option:
            dashboard_employee(result)
        elif 'issue_reporter' == option:
            dashboard_reporter(result)
            
        else:
            dashboard_management(result)
    
    else:
        st.write("Please check your Credentials!")

"""
'## Read tables'

sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display the table'
    sql_table = f'select * from {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)

st.write(session_state.name)
st.write("We are here")
"""