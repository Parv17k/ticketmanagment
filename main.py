import pandas as pd
import streamlit as st
import psycopg2 
from configparser import ConfigParser
##import plotly.express as px
import SessionState
session_state = SessionState.get(id=0,domain='')
head=st.title("")

def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

    
@st.cache(allow_output_mutation=True)
def query_db(sql: str,flag= False):
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
        conn.commit()

        # Obtain data
        if flag== False:
            data = cur.fetchall()
        
            column_names = [desc[0] for desc in cur.description]
            df = pd.DataFrame(data=data, columns=column_names)
            return df
        return "done"       
        

    except Exception as error:
        cur.execute("ROLLBACK")
        conn.commit()
        cur.close()
        conn.close()
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

    if user['domain'][0]=='issue_reporter':
        
        sql = f"""select i.name, et.ticket_id,et.status, et.start_time, et.end_time, et.title, et.issuer_id,
         et.assigned_to_id, et.name as emp_name from (select  * from 
         (select * from
         tickets,ticket_status
         where tickets.status_id = ticket_status.id
         ) t
         left join employees  e on t.assigned_to_id  = e.id)
         et , issue_reporter i where i.id = et.issuer_id and  i.id={str(user['id'][0])} ;"""

    elif user['domain'][0]=='employees':
        sql =f"""select i.name, et.ticket_id, et.start_time, et.end_time, 
        et.title, et.issuer_id, et.assigned_to_id, et.name as emp_name from
         (select  * from (select * from
         tickets,ticket_status
         where tickets.status_id = ticket_status.id
         ) t left join employees  e on e.id ={str(user['id'][0])} )
         et left join issue_reporter i on i.id = et.issuer_id;"""
 
    else:
        sql= f"""select temp.title, m.name as manager_name , temp.name as management_system,temp.type as department
        from ( select  t.title, ms.name,t.ms_id,ms.type from (select * from
         tickets,ticket_status
         where tickets.status_id = ticket_status.id
         ) t right join management_system ms on t.ms_id=ms.id) 
        temp ,chief_management m where m.id = temp.ms_id  and  m.id = {str(user['id'][0])} ;"""
    
    data=query_db(sql)
    #print(data)
    return data

def show_tickets(user):
    st.table(load_tickets(user))

def createticket(user_id):
    title = st.text_input("title of the ticket:")
    groupid = st.text_input('Group_id:')
    sql_management = 'select id , name , type from management_system;'
    management=[]
    data = query_db(sql_management)
    st.table(data)
    for t in data.values.tolist():
        temp = str(t[0]) + '  :' + t[1] + '  -'+ t[2]
        management.append(temp)
    ms_id = st.selectbox('Choose a system: ( ID : name  type) ', management).split(':',1)[0]
    #ms_id = st.text_input('Select Management System ID :')
    if st.button('create'):
        
        sql = f"insert into tickets (group_id, ms_id, title, issuer_id,status_id) values({groupid}, {ms_id},'{title}', {user_id},1 );"
        st.write(sql)
        result= query_db(sql,True)
        if result=='done':
            st.success('Ticket is created')
            st.write(result)
        else: st.error('error occured in SQL')
       
        



def dashboard_reporter(user_data):
    head.title("Issue reporter Dashboard")
    
    st.success("Hello Issue Reporter '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
    createticket(user_data['id'][0])
  


def dashboard_employee(user_data):
    head.title("Employee Dashboard")
    st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
def dashboard_management(user_data):
    head.title("Management Dashboard")
    st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
def auth(id,password,domain):

    query="SELECT * from "+domain+" where id="+id+" and password = '"+password+"';"
    try:
        df= query_db(query)

        return df
    except Exception as error:
        st.write("Error Occured",error)
    return 
st.write(session_state.domain)
if session_state.id == 0:
    head.title("Issue Management System")
    option = st.selectbox('Select your domain/role?',('employees', 'issue_reporter', 'chief_management'))
    st.write('Your selected domian:', option)
    user_id = st.text_input("ID:")
    user_password = st.text_input("Password:")

    if st.button('add'):
        result = auth(user_id, user_password,option)
        #print("Here is auth data",result)
        if result is not None :
            result['domain']=option
            session_state.id=result['id'][0]
            session_state.domain=result
            if "employees" == option:
                dashboard_employee(result)
            elif 'issue_reporter' == option:
                dashboard_reporter(result) 
            elif 'chief_management' == option:
                dashboard_management(result)
        
        else:
            st.write("Please check your Credentials!")
else:
    if "employees" == session_state.domain["domain"][0]:
        dashboard_employee(session_state.domain)
    elif 'issue_reporter' == session_state.domain["domain"][0]:
        dashboard_reporter(session_state.domain) 
    elif 'chief_management' == session_state.domain["domain"][0]:
        dashboard_management(resession_state.domain)

'## Read tables'

sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display the table'

    sql_table = f'select * from {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)