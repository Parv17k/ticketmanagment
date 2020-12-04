import pandas as pd
import streamlit as st
import psycopg2 
from configparser import ConfigParser

##import plotly.express as px
##import SessionState
userInfo={}
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
    return -1


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


'## Read tables'

sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display the table'

    sql_table = f'select * from {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)


'## Query management_system'

sql_customer_names = 'select name from management_system;'
customer_names = query_db(sql_customer_names)['name'].tolist()
customer_name = st.selectbox('Choose a customer', customer_names)
if customer_name:
    sql_customer = f"select * from customers where name = '{customer_name}';"
    customer_info = query_db(sql_customer).loc[0]
    c_age, c_city, c_state = customer_info['age'], customer_info['city'], customer_info['state']
    st.write(f"{customer_name} is {c_age}-year old, and lives in {customer_info['city']}, {customer_info['state']}.")