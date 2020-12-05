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
    conn=None
    try:
        db_info = get_config()

    # Connect to an existing database
        conn = psycopg2.connect(**db_info)
    except: 
        conn = createConnection()
    # Open a cursor to perform database operations
    cur = conn.cursor()
    try:
        
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

    except Exception as error:
        cur.execute("ROLLBACK")
        conn.commit()
        st.write("Error Occured",error)
    return None

    

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
    print("You are ",user)
    if user['domain'][0]=='issue_reporter':
        
        sql = """select i.name, et.ticket_id, et.start_time, et.end_time, et.title, et.issuer_id, et.assigned_to_id, et.name as emp_name from
         (select  *
        from tickets t left join employees  e on issuer_id = """+str(user['id'][0])+""")
         et left join issue_reporter i on i.id = et.issuer_id;"""
    elif user['domain'][0]=='employees':
        sql = """select i.name, et.ticket_id, et.start_time, et.end_time, et.title, et.issuer_id, et.assigned_to_id, et.name as emp_name from
         (select  *
        from tickets t left join employees  e on e.id ="""+str(user['id'][0])+""" )
         et left join issue_reporter i on i.id = et.issuer_id;"""
 
    else:
        sql= """
        select temp.title, m.name as manager_name , temp.name as management_system,temp.type as department
        from ( select  t.title, ms.name,t.ms_id,ms.type from tickets t right join management_system ms on t.ms_id=ms.id) temp ,chief_management m
        where m.id = temp.ms_id  and  m.id = """+str(user['id'][0])+""" ;"""
        print(sql)
    data=query_db(sql)
    print(data)
    return data

def show_tickets(user):
    st.table(load_tickets(user))


def dashboard_reporter(user_data):
    head.title("Issue reporter Dashboard")
    st.success("Hello Issue Reporter '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
def dashboard_employee(user_data):
     st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
     show_tickets(user_data)
def dashboard_management(user_data):
     st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
     show_tickets(user_data)
def auth(id,password,domain):

    query="SELECT * from "+domain+" where id="+id+" and password = '"+password+"';"
    try:
        df= query_db(query)
        print(df)
        return df
    except Exception as error:
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
        elif 'chief_management' == option:
            dashboard_management(result)
    
    else:
        st.write("Please check your Credentials!")
