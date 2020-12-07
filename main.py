import pandas as pd
import streamlit as st
import psycopg2 
import datetime
import numpy as np
#import graphviz as graphviz
from configparser import ConfigParser
import SessionState
#import matplotlib.pyplot as plt

session_state = SessionState.get(id=0,data=pd.DataFrame())
head=st.title("")

def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

def query_db(sql: str,flag= False):
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
            df = df.replace({pd.np.nan: None})
            return df
        return "done"       
        

    except Exception as error:
        st.write(error)
        cur.execute("ROLLBACK")
        conn.commit()
    return None

def show_ms_profit():
    st.title("Profit/Loss Overview : All Departement with tickets")
    sql="""
    select sum(amount - penalty) as profit_dept, int.name from costs,(select t.ticket_id,m.name as name from tickets t,management_system m where m.id=t.ms_id ) int where int.ticket_id=costs.ticket_id group by int.name;
    """
    data=query_db(sql)
    st.dataframe(data)

def show_cost(user):
    st.title("Cost Overview : for your Management Systems")
    sql = f"""
    select tickets.ticket_id,costs.amount,costs.penalty,(amount - penalty) as profit 
    from costs,tickets where tickets.ticket_id=costs.ticket_id and tickets.ticket_id in
    (select ticket_id from 
    tickets where ms_id in (select id from management_system where managerid={user['id'][0]}));
    """
    data=query_db(sql)
    data=data.set_index('ticket_id')
    st.dataframe(data)
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

def show_ms_profit():
    st.title("Profit/Loss Overview : All Department")
    sql=f"""select sum(amount - penalty) as profit_dept, int.name from costs,
    (select t.ticket_id,m.name as name from tickets t,management_system m where m.id=t.ms_id )
     int where int.ticket_id=costs.ticket_id group by int.name;
    """
    data=query_db(sql)
    st.dataframe(data)

def show_cost(user):
    st.title("Cost Overview : for your Management Systems")
    sql = f"""
    select tickets.ticket_id,costs.amount,costs.penalty,(amount - penalty) as profit 
    from costs,tickets where tickets.ticket_id=costs.ticket_id and tickets.ticket_id in
    (select ticket_id from 
    tickets where ms_id in (select id from management_system where managerid={user['id'][0]}));
    """
    data=query_db(sql)
    data=data.set_index('ticket_id')
    st.dataframe(data)
   # X = np.arange(4)
    #fig = plt.figure()
    #ax = fig.add_axes(data)
    #ax.bar(X + 0.00, data['amount'], color = 'b', width = 0.25)
    #ax.bar(X + 0.25, data['profit'], color = 'g', width = 0.25)
    #ax.bar(X + 0.50, data['penalty'], color = 'r', width = 0.25)
    #plt.plot(data['penalty'], 'r--', data['amount'], 'bs', data['profit'], 'g^')
    
    #st.pyplot(fig)
    
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
    st.dataframe(data)


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
    if st.button('create'):
        
        sql = f"insert into tickets (group_id, ms_id, title, issuer_id,status_id) values({groupid}, {ms_id},'{title}', {user_id},1 );"
        result= query_db(sql,True)
        if result=='done':
            st.success('Ticket is created')
        else: st.error('error occured in SQL')

      
def updatestatus(user):
    sql = f"""select tickets.ticket_id,ticket_status.status, tickets.title 
    from tickets,ticket_status where tickets.status_id = ticket_status.id and assigned_to_id  = {str(user['id'][0])};"""

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
        temp = int(selS)
        selT=selT.split(":")[0]
        sq=f"update tickets set status_id ={selS} where ticket_id ={selT};"
        if temp == 6:
            sq=f"""update tickets set end_time ='{datetime.datetime.now()}',resolution_sla='{datetime.datetime.now()}',status_id ={selS} where ticket_id ={selT};"""
        result= query_db(sq,True)
        print(sq)
        if result=='done':
            st.success('Ticket is updated')
        else: st.error('error occured in SQL')


def visualize_tickets(user):
    sql1 = f"""select ticket_id ,title  from tickets where 
            ms_id in (select id from management_system where managerid = {str(user['id'][0])});"""
    data = query_db(sql1)
    if data.empty== False :
        st.subheader('Graph a ticket')
        tickets=[]
        for t in data.values.tolist():
                temp = f'{str(t[0])} : {t[1]}'
                tickets.append(temp)
        
        selT=st.selectbox('Select Ticket for a graph:',tickets)
        selT=selT.split(":")[0]
    sql= f"""select issue_reporter.name as reporter,temp.title,temp.issuer_id as 
    issuer_id,temp.emp_id,temp.emp_name from (select t.issuer_id,t.title,t.assigned_to_id as 
    emp_id,e.name as emp_name from tickets t,employees e where e.id = t.assigned_to_id and t.ticket_id={selT}) 
    temp, issue_reporter where issue_reporter.id=temp.issuer_id;"""
    data = query_db(sql)
    if data.empty == False:
        st.dataframe(data)
      #  graph = graphviz.Digraph()
      #  graph.edge("reporter - "+str(data['reporter'][0]),"ticket - "+ str(data['title'][0]))
      #  graph.edge("worker - "+str(data['emp_name'][0]), "ticket - "+str(data['title'][0]))
      #  st.graphviz_chart(graph)
    else:
         st.error("Can not create a graph with this ticket,Please assign a worker or check the ticket")
    

def update_employee(user):
    sql = f"""select ticket_id ,title  from tickets where assigned_to_id is null and 
            ms_id in (select id from management_system where managerid = {str(user['id'][0])});"""
    data = query_db(sql)
    if data.empty== False :
        st.subheader('Ticket that dont have any employee assigned')
        tickets=[]
        for t in data.values.tolist():
                temp = f'{str(t[0])} : {t[1]}'
                tickets.append(temp)
        
        selT=st.selectbox('select the ticket for which want to update Employess',tickets)
        sql1= f'select id,name from employees where ms_id in (select id from management_system where managerid= {str(user["id"][0])}  );'
        data1 = query_db(sql1)
        statuss=[]
        for t in data1.values.tolist():
                temp = f'{str(t[0])}  : {t[1]}'
                statuss.append(temp)
        ent= f'select the the user for the ticket {selT}' 
        selE=st.selectbox(ent,statuss)
        if st.button('update status'):
            selE=selE.split(":")[0]
            selT=selT.split(":")[0]
            sq=f""" update tickets set assigned_to_id = {selE},start_time ='{datetime.datetime.now()}',response_sla ='true' where ticket_id ={selT};"""
            print(sq)
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
    if st.button('show feedback table for the user'):
        showFeedback(user_data)
    
def dashboard_management(user_data):
    head.title("Management Dashboard")
    st.success("Hello '"+user_data['name'][0]+"', Please scroll down and access your dashboard")
    show_tickets(user_data)
    update_employee(user_data)
    if st.button('show feedback table for the user'):
        showFeedback(user_data)
    show_cost(user_data)
    show_ms_profit()
    visualize_tickets(user_data)

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
        print(result)
        #print("Here is auth data",result)
        if result.empty == False :
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
            st.error("Please check your Credentials!")
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