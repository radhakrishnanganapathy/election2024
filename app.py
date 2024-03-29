from bs4 import BeautifulSoup
import requests
import pandas as pd
import psycopg2

result = []
for constitutionID in range(1,40):
     print("constitutionID : ",constitutionID)
     for PageNO in range (1,20):
          # print("PageNO : ",PageNO)
          try:
               url = f'https://affidavit.eci.gov.in/CandidateCustomFilter?_token=xWPHZujZV414LDk7xqTzA3XbrH49o1wUwGW1FV50&electionType=24-PC-GENERAL-1-46&election=24-PC-GENERAL-1-46&states=S22&constId={constitutionID}&page={PageNO}'

               response = requests.get(url)

               if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    button = soup.find_all('div', class_='col-md-2')
                    for item in button:
                         button_text = item.find('h4').text.strip() 
                         value = item.find('button')['value']
                         span_text = item.find('span').text.strip() 
                         nomination_count = {
                              'fiter' : button_text,
                              'count' : span_text
                         }
                    profile = soup.find_all('div', class_="details-name")
                    for item in profile:
                         name = item.find('h4', class_='bg-grn')
                         party = item.find('div', class_='col-sm-6 col-xs-12 text-left left-party')
                         state = item.find('div', class_='col-sm-6 col-xs-12 text-left right-party')
                         link = item.find('div',class_='hover-lay').find('a')['href']
                         if name:
                              Candidate_name = name.text.strip()
                         if party:
                              div_text = party.get_text(strip=True)
                              split_text = div_text.split("Status :")
                              party = split_text[0].replace("Party :","").strip()
                              status = split_text[1].strip()
                         if state :
                              div_text = state.get_text(strip=True)
                              split_text = div_text.split("Constituency :")
                              state = split_text[0].replace("State :","").strip()
                              Constituency_view_split = split_text[1].strip()
                              split = Constituency_view_split.split("View more")
                              Constituency = split[0].strip()

                         data = {
                              "stateID": constitutionID,
                              "constitutionID" : constitutionID,
                              "Candidate_name ": Candidate_name,
                              "party":party,
                              "status":status,
                              "state":state,
                              "Constituency":Constituency,
                              'link':link
                         }
                         result.append(data)
               else:
                    print("denied")
               
          except Exception as e:
               print(e)

print(result)
df = pd.DataFrame(result)
df.to_csv('app.csv')

          