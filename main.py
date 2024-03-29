import streamlit as st
import requests
import datetime
from flask import Flask,Response
import psycopg2
from psycopg2 import IntegrityError

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

def main(select_option,sumbit_button):
     ip = get_user_ip()
     party = select_option
     if sumbit_button:
          try:
               insert_query = "insert into election_opinion (ip,party) values (%s,%s)"
               data = ip,party
               cur.execute(insert_query, data)
               conn.commit()
               st.success(f'Thanks for voting')
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
    
st.sidebar.title("Opinion Poll-2024 TN")
option = ['NDA','I.N.D.I.A','Namtamizhar','ADMK','Independent','NOTA','Unable to Vote']
select_option = st.sidebar.selectbox("My vote for", option)
st.sidebar.button(f'Total Votes : {vote_count()}')
sumbit_button = st.sidebar.button('submit yor Vote')

st.header("General election 2024 - TamilNadu")
st.write('Try to 100% Vote')
st.write("Don't waste your vote on NOTA ")

constituencies_query = "select constituency from election group by constituency"
cur.execute(constituencies_query)
constituencies_fetch = cur.fetchall()
constituencies = [status[0] for status in constituencies_fetch]
select_status = st.selectbox('constituencies',constituencies)

status_option = ['Withdrawn','Rejected','Accepted','Applied']
select_status = st.selectbox('status',status_option)

if __name__ == "__main__":
    main(select_option,sumbit_button)
    conn.close()
    cur.close()
