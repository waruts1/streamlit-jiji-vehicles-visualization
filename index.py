from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import requests
import re
import datetime

def load_data():
    cookies = {
        'first_visit': '1675672536',
        'rid': 'jiji.co.ke',
        'app': 'dea054f6a1164db783b5137485f470df',
        'uid': '34343db60e2af4e30a5ca55b1347573633f887e9',
        '_js2': 'FHxe_JjOIHNVr3PIjCaYk2dmeGpKOZn5mFs-QF17Kv4=',
        'app_sid': '1675672537113',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://jiji.co.ke/cars',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Window-ID': '1675672536616',
        'Connection': 'keep-alive',
        # 'Cookie': 'first_visit=1675672536; rid=jiji.co.ke; app=dea054f6a1164db783b5137485f470df; uid=34343db60e2af4e30a5ca55b1347573633f887e9; _js2=FHxe_JjOIHNVr3PIjCaYk2dmeGpKOZn5mFs-QF17Kv4=; app_sid=1675672537113',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    params = {
        'slug': 'cars',
        'webp': 'true',
    }

    getData = requests.get('https://jiji.co.ke/api_web/v1/listing', params=params, cookies=cookies, headers=headers).json()['adverts_list']

    pageNo = 1

    # totalItems = getData['total_pages']
    totalItems = 35
    perPageResults = []

    for a in range(1, totalItems):

        url = 'https://jiji.co.ke/api_web/v1/listing?page=%s' % pageNo
        getDataFromLoop = requests.get(url, params=params, cookies=cookies, headers=headers).json()['adverts_list']['adverts']
        totalPageSize = len(getDataFromLoop)
        for i in range(1,totalPageSize):
            if i > totalPageSize:
                break
            perPageResults.append(getDataFromLoop[i])
        pageNo += 1   
    
    car_name = []
    price = []
    color = []
    year = []
    make = []
    model = []
    mileage = []
    for i in range(len(perPageResults)):
        price.append(perPageResults[i]['price_obj']['value'])
        if(len(perPageResults[i]['attrs']) > 2):
            mileage.append(perPageResults[i]['attrs'][2]['value'])
        else:
            mileage.append(0)
        car_name.append(perPageResults[i]['title'])
        car_title = perPageResults[i]['title']
        split_str =car_title.split(" ") 
        year_str = split_str[-2] if re.search('[a-zA-Z]', str(split_str[-2])) == None else split_str[-1]
        year.append(year_str)
        color.append(split_str[-1] if re.search('[0-9]', str(split_str[-1])) == None else split_str[-2]) 
        make.append(split_str[0])
        model.append(split_str[1])
    
    data = {
        'car_name':car_name,
        'price':price,
        'color':color,
        'year':year,
        'make':make,
        'model':model,
        'mileage':mileage
        }
    df = pd.DataFrame(data, columns=['car_name', 'price', 'color', 'year', 'make','model','mileage'])
    df['year'] = df['year'].apply(remove_non_numberics)
    return df;

def remove_non_numberics(s):
    if re.search('[a-zA-Z]', str(s)) != None or int(len(s)) > 4 or int(len(s)) < 4:
        return int(0)
    else :
        return int(s)


df = load_data()
st.title("Web Scraped Jiji Vehicle DataSet")

clist = ["ALL"] + sorted(df['make'].unique())

vehicle_make = st.sidebar.selectbox("Select a make:",clist)
st.write('Vehicle Make Selected Is :', vehicle_make)
df_filter_make = df[df['make'] == vehicle_make]

df2=df_filter_make.groupby(['model']).size().reset_index().rename(columns={0:'count'}).sort_values(['count'], ascending=False)

col1, col2, col3 = st.columns(3)

with col1:
   vehicle_model = st.selectbox("Select a model:",["ALL"] + sorted(df2['model']))

with col2:
    year_from = st.selectbox('Year From', range(1990, datetime.date.today().year + 1))

with col3:
    year_to = st.selectbox('Year To', range(1990, datetime.date.today().year + 1))


df_filter_make = df[df["make"] == vehicle_make]
if vehicle_model == 'ALL':
    df_filter_model = df[df["make"] == vehicle_make]
else :
    df_filter_model = df_filter_make[df_filter_make['model'] == vehicle_model ]

st.write('Vehicle Model Selected Is :', vehicle_model , 'Total Rows ', df_filter_model.shape[0])

st.dataframe(df_filter_model[df_filter_model['year'].between(year_from,year_to)])

fig = px.line(df2, 
    x = "model", y = "count", title = vehicle_make)

st.plotly_chart(fig)

@st.cache_data
def convert_df():
   return df_filter_model[df_filter_model['year'].between(year_from,year_to)].to_csv(index=False).encode('utf-8')


csv = convert_df(df)

st.sidebar.download_button(
   "Press to Download",
   csv,
   "file.csv",
   "text/csv",
   key='download-csv'
)
st.cache_data