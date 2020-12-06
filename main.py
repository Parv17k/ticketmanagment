import pandas as pd
import streamlit as st
import psycopg2 
import datetime
from configparser import ConfigParser
##import plotly.express as px
import SessionState
session_state = SessionState.get(id=0,data=pd.DataFrame())
head=st.title("")


def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

    
#@st.cache(allow_output_mutation=True)
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
        st.write(error)
        cur.execute("ROLLBACK")
        conn.commit()
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

def submit_feedback(user):
    
    sql_tickets = f"""select distinct * from tickets t where issuer_id ={user['id'][0]} 
                    and t.ticket_id not in (select ticket_id from feedbacks 
                    where feedback_by = {user['id'][0]});"""
    
    tickets=[]
    data = query_db(sql_tickets)
    if len(data) >0:
        st.title("Add a Feedback:")
        for t in data.values.tolist():
            temp = str(t[0])
            tickets.append(temp)
        ticket_id = st.selectbox('Choose a Ticket created by you which are available the table above ', tickets)

        points = st.text_input("Rate out of 10:")
        feedback = st.text_input('feedback:')
        if st.button('Submit Feedback'):
            sql = f"""insert into feedbacks (points, remark, time_stamp, feedback_by,ticket_id)
            values({points}, '{feedback}','{datetime.datetime.now()}',{user['id'][0]} ,{ticket_id} );"""
            result= query_db(sql,True)
            if result=='done':
                st.success('Feedback submitted!!')
            else: st.error('error occured in SQL')
    else: st.write('All tickets feedback have been assigned for the tickets created by you')

def showFeedback(user):
    sql =''
    if user['domain'][0] == 'issue_reporter':
        sql = f'select * from feedbacks where feedback_by={str(user["id"][0])};'
    elif user['domain'][0] == 'employees': 
        sql = f'select * from feedbacks where ticket_id in (select ticket_id from tickets where assigned_to_id = {str(user["id"][0])});'

    else: 
        sql = f"""select * from feedbacks where ticket_id in (select ticket_id from tickets
         where ms_id in (select id from management_system where managerid = {str(user["id"][0])}));"""
    
    data=query_db(sql)
    st.table(data)

@st.cache
def load_tickets(user):
    sql=''

    if user['domain'][0]=='issue_reporter':
        
        sql = f"""select i.name, et.ticket_id,et.status, et.start_time, et.end_time, et.title, et.issuer_id,
         et.assigned_to_id, et.name as emp_name from (select  * from 
         (select * from tickets,ticket_status where tickets.status_id = ticket_status.id) t
         left join employees  e on t.assigned_to_id  = e.id)
         et , issue_reporter i where i.id = et.issuer_id and  i.id={str(user['id'][0])} ;"""

    elif user['domain'][0]=='employees':
        sql =f"""select i.name, et.ticket_id,et.status ,et.start_time, et.end_time, 
        et.title, et.issuer_id, et.assigned_to_id, et.name as emp_name from
         (select  * from (select * from tickets,ticket_status
         where tickets.status_id = ticket_status.id
         ) t, employees e where t.assigned_to_id =e.id and e.id={str(user['id'][0])} )
         et left join issue_reporter i on i.id = et.issuer_id;"""
 
    else:
        sql= f"""select temp.ticket_id,temp.status ,temp.title, m.name as manager_name , temp.name as management_system,
        temp.type as department from ( select  t.title, ms.name,t.ms_id,ms.type,ms.managerid,t.ticket_id,t.status from
        (select * from tickets,ticket_status where tickets.status_id = ticket_status.id) t
        right join management_system ms on t.ms_id=ms.id) temp ,chief_management m
        where m.id = temp.managerid  and  m.id ={str(user['id'][0])};"""
    
    data=query_db(sql)
    return data

def show_tickets(user):
    st.title("Your Tickets:")
    st.table(load_tickets(user))

def createticket(user_id):
    st.title("Create a Ticket:")
    title = st.text_input("title of the ticket:")
    groupid = st.text_input('Group_id:')
    sql_management = 'select id , name , type from management_system;'
    management=[]
    data = query_db(sql_management)
    for t in data.values.tolist():
        temp = str(t[0]) + '  :' + t[1] + '  -'+ t[2]
        management.append(temp)
    ms_id = st.selectbox('Choose a system: ( ID : name  type) ', management).split(':',1)[0]
    #ms_id = st.text_input('Select Management System ID :')
    if st.button('create'):
        
        sql = f"insert into tickets (group_id, ms_id, title, issuer_id,status_id) values({groupid}, {ms_id},'{title}', {user_id},1 );"
        result= query_db(sql,True)
        if result=='done':
            st.success('Ticket is created')
        else: st.error('error occured in SQL')

      
def updatestatus(user):
    st.write("I am in")
    sql = f"""select tickets.ticket_id,ticket_status.status, tickets.title from tickets,ticket_status where tickets.status_id = ticket_status.id and assigned_to_id  = {str(user['id'][0])};"""

    data = query_db(sql)
    tickets=[]
    for t in data.values.tolist():
            temp = f'{str(t[0])} : {t[2] }  : {t[1]}'
            tickets.append(temp)
    
    selT=st.selectbox('select the ticket for which want to update status',tickets)
    sql1= 'select id,status from ticket_status;'
    data1 = query_db(sql1)
    statuss=[]
    for t in data1.values.tolist():
            temp = f'{str(t[0])}  : {t[1]}'
            statuss.append(temp)
    ent= f'select the the new status for the ticket {selT}' 
    selS=st.selectbox(ent,statuss)
    if st.button('update status'):
        selS=selS.split(":")[0]
        selT=selT.split(":")[0]
        sq=f"update tickets set status_id ={selS} where ticket_id ={selT};"
        result= query_db(sq,True)
        if result=='done':
            st.success('Ticket is updated')
        else: st.error('error occured in SQL')
        


def dashboard_reporter(user_data):
    head.title("Issue reporter Dashboard")
    
    st.success("Hello Issue Reporter '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
    createticket(user_data['id'][0])
    submit_feedback(user_data)
    if st.button('show feedback table for the user'):
        showFeedback(user_data)

def dashboard_employee(user_data):
    head.title("Employee Dashboard")
    st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
    updatestatus(user_data)
    st.write("I am down")
    if st.button('show feedback table for the user'):
        showFeedback(user_data)
    
def dashboard_management(user_data):
    head.title("Management Dashboard")
    st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
    if st.button('show feedback table for the user'):
        showFeedback(user_data)

def auth(id,password,domain):

    query="SELECT * from "+domain+" where id="+id+" and password = '"+password+"';"
    try:
        df= query_db(query)

        return df
    except Exception as error:
        st.write("Error Occured",error)
    return 
df=session_state.data 
if df.empty== False:
    df = df.drop(columns='password')
    st.write(df )
if session_state.id == 0:
    head.title("Issue Management System")
    option = st.selectbox('Select your domain/role?',('employees', 'issue_reporter', 'chief_management'))
    st.write('Your selected domian:', option)
    user_id = st.text_input("ID:")
    user_password = st.text_input("Password:")

    if st.button('Login'):
        result = auth(user_id, user_password,option)
        #print("Here is auth data",result)
        if result is not None :
            result['domain']=option
            session_state.id=result['id'][0]
            session_state.data=result
            if "employees" == option:
                dashboard_employee(result)
            elif 'issue_reporter' == option:
                dashboard_reporter(result) 
            elif 'chief_management' == option:
                dashboard_management(result)
        
        else:
            st.write("Please check your Credentials!")
else:
    if "employees" == session_state.data["domain"][0]:
        dashboard_employee(session_state.data)
    elif 'issue_reporter' == session_state.data["domain"][0]:
        dashboard_reporter(session_state.data) 
    elif 'chief_management' == session_state.data["domain"][0]:
        dashboard_management(session_state.data)



'## Read tables'

sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display the table'

    sql_table = f'select * from {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)
