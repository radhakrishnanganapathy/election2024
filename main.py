import streamlit as st
import requests
import datetime
from flask import Flask,Response
import psycopg2
from psycopg2 import IntegrityError
import pandas as pd
import socket
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static



# Function to get user's IP address
conn = psycopg2.connect(
     host='dpg-cmmvudocmk4c73e4qfh0-a.oregon-postgres.render.com',
     database='guvi_yby8',
     user='guvi_yby8_user',
     password='MFyUGk2fbpvmiRZ8FaXIBt56uXD9eMWc'
     )
cur = conn.cursor()

def set_cookie():
    st.experimental_set_query_params(voted='true', expires=datetime.datetime.now() + datetime.timedelta(days=20))
#     st.session_state['voted'] = True
#     response = Response()
#     expires = datetime.datetime.now() + datetime.timedelta(days=20)
#     response.set_cookies('voted','true', expires=expires)
#     return response

def has_voted():
#     return 'voted' in st.experimental_get_query_params()
     return 'voted' in st.query_params
#     return st.session_state.get('voted', False)
#     return 'voted' in st.request.cookies

def main_vote(select_option,sumbit_button):
     ip = get_ip_address()
     party = select_option
     if sumbit_button:
          try:
               insert_query = "insert into election_opinion (ip,party) values (%s,%s)"
               data = ip,party
               cur.execute(insert_query, data)
               conn.commit()
               st.sidebar.success(f'Thanks for voting')
               vote_count()
               
          # set_cookie()
          except IntegrityError as ie:   
               st.sidebar.warning("Sorry, you have already voted. you can vote once." )
          except Exception as e:
               st.warning(e)
def vote_count():
     try:
          select = "select count(ip) from election_opinion"
          cur.execute(select)
          count = cur.fetchone()[0] 
          return count
     except Exception as e:
          st.sidebar.warning(e)
          

def get_user_ip():
    try:
        # Make a request to an external service to get the user's IP address
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return "Unable to fetch IP address"
    except Exception as e:
        st.error(f"Error fetching IP address: {e}")
        return None
    
def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Connect to a remote server (doesn't matter which)
        s.connect(("8.8.8.8", 80))
        
        # Get the local IP address associated with the socket
        ip_address = s.getsockname()[0]
        
        # Close the socket
        s.close()
        
        return ip_address
    except socket.error:
        return "Unable to retrieve IP address"
    
def filter(select_constituencies,select_status,select_party):
     query = "select * from election where "
     filters = []
     if select_constituencies:
          filters.append(f"constituency='{select_constituencies}'")
     if select_status:
          filters.append(f"status='{select_status}'")
     if select_party:
          filters.append(f"party='{select_party}'")
     if filters:
          query += " and ".join(filters)
     if filters:
          cur.execute(query)
          result = cur.fetchall()
          column_names = [desc[0] for desc in cur.description]
          df = pd.DataFrame(result, columns = column_names)
          st.write(df)
     else:
          st.warning("Please select AT least one filter")

def potly():
     count ='''select count(case when status='Withdrawn' then 1 end) as Withdrawn,
     count(case when status='Rejected' then 1 end) as Rejected,
     count(case when status='Applied' then 1 end) as Applied,
     count(case when status='Accepted' then 1 end) as Accepted
      from election
     '''
     cur.execute(count)
     result = cur.fetchall()
     withdrawn, rejected, accepted, applied = result[0]
     categories = ['Withdrawn', 'Rejected', 'Accepted', 'Applied']
     counts = [withdrawn, rejected, accepted, applied]
     color = ['red', 'blue', 'green', 'orange']
     fig = go.Figure([go.Bar(x=categories, y=counts, marker_color=color)])
     st.plotly_chart(fig)
     # st.bar_chart(dict(zip(categories, counts, color=['red', 'blue', 'green', 'orange'])))
     # plt.bar(categories, counts, color=['red', 'blue', 'green', 'orange'])
     # st.plotly_chart(fig)
     # plt.xlabel('Status')
     # plt.ylabel('Count')
     # plt.title('Election Application Status')
     # plt.show()

def candidate_data():
     query = '''select election.*,map.latitude,map.longitude from election
      inner join 
      map on election.constituency = map.constituency 
      where election.status = 'Accepted'
      '''
     cur.execute(query)
     data = cur.fetchall()
     return data

def map_candidate():
     st.title("Election Candidate Map")
     candidateData = candidate_data()
     if candidateData:
          m = folium.Map(location=[candidateData[0][8],candidateData[0][9]],zoom_start=10)

          for candidate in candidateData:
               pop_message = f"name:{candidate[2]}<br>party:{candidate[3]}"
               folium.Marker([candidate[8],candidate[9]],popup=pop_message[2]).add_to(m)
          folium_static(m)
     else:
          st.write("No data ")
    

st.header("General election 2024 - TamilNadu")
st.write('Try to 100% Vote')
st.write("Don't waste your vote on NOTA ")
potly()

st.sidebar.title("Opinion Poll-2024 TN")
option = ['NDA','I.N.D.I.A','Namtamizhar','ADMK','Independent','NOTA','Unable to Vote']
select_option = st.sidebar.selectbox("My vote for", option)
# st.sidebar.button(f'Total Votes : {vote_count()}')
sumbit_button = st.sidebar.button(f'Total Votes : {vote_count()}')



constituencies_query = "select constituency from election group by constituency"
cur.execute(constituencies_query)
constituencies_fetch = cur.fetchall()
constituencies = [status[0] for status in constituencies_fetch]
constituencies.append("")
sort_constituencies = sorted(constituencies)



status_option = ["",'Withdrawn','Rejected','Accepted','Applied']


party_query = "select party from election group by party"
cur.execute(party_query)
party_fetch = cur.fetchall()
parties = [party[0] for party in party_fetch]
parties.append("")
sort_parties = sorted(parties)


col1,col2,col3 = st.columns(3)
with col1:
     select_constituencies = st.selectbox('constituencies',sort_constituencies)
with col2:
     select_status = st.selectbox('status',status_option)
with col3:
     select_party = st.selectbox('party',sort_parties)
submit = st.button("filter")
if submit:
     filter(select_constituencies,select_status,select_party)




# potly()
main_vote(select_option,sumbit_button)
map_candidate()
conn.close()
cur.close()
