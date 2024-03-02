import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import urllib

customers = pd.read_csv("./customers_dataset.csv")
orders = pd.read_csv("./orders_dataset.csv")
geolocation = pd.read_csv("./geolocation_dataset.csv")

for column in orders.columns:
    orders[column].fillna(orders[column].mode()[0], inplace=True)
    
def compute_late_analysis():
    late_deliveries = orders[pd.to_datetime(orders['order_delivered_customer_date']) > pd.to_datetime(orders['order_estimated_delivery_date'])]
    late_deliveries = late_deliveries[pd.to_datetime(late_deliveries['order_delivered_customer_date']).dt.day != pd.to_datetime(late_deliveries['order_estimated_delivery_date']).dt.day]
    num_late_deliveries = len(late_deliveries)
    on_time_deliveries = orders[pd.to_datetime(orders['order_delivered_customer_date']) <= pd.to_datetime(orders['order_estimated_delivery_date'])]
    num_on_time_deliveries = len(on_time_deliveries)
    return late_deliveries, num_late_deliveries, num_on_time_deliveries

def show_plot_late_orders(num_late_deliveries, num_on_time_deliveries):
    fig, ax = plt.subplots()
    ax.pie([num_late_deliveries, num_on_time_deliveries], labels=['Late Deliveries', 'On Time Deliveries'], autopct='%1.1f%%')
    ax.set_title('Percentage of Late Deliveries')
    st.pyplot(fig)
    
def dist_late_orders(late_deliveries):
    late_in_days = {}

    for index, row in late_deliveries.iterrows():
        days_late = (pd.to_datetime(row['order_delivered_customer_date']) - pd.to_datetime(row['order_estimated_delivery_date'])).days
        if days_late in late_in_days:
            late_in_days[days_late] += 1
        else:
            late_in_days[days_late] = 1

    late_in_days.pop(0, None)
    
    return late_in_days

def show_plot_late_days(late_in_days):
    fig, ax = plt.subplots()
    sns.barplot(x=list(late_in_days.keys()), y=list(late_in_days.values()), ax=ax)
    ax.set_xlabel('Days Late')
    ax.set_ylabel('Number of Late Deliveries')
    ax.set_title('Number of Late Deliveries by Days Late')
    st.pyplot(fig)
    
def merge_datasets():
    merged_coords = customers.merge(geolocation, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
    merged_coords = merged_coords.drop(columns=['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state'])
    merged_coords.head()
    merged_coords = merged_coords.dropna()
    return merged_coords

def show_brazil(merged_coords):
    brazil_map = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(brazil_map, extent=[-75, -35, -35, 5])

    ax.scatter(merged_coords['geolocation_lng'], merged_coords['geolocation_lat'], color='red', marker='o', label='Locations')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Geolocation Data Over Brazil')
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("Dashboard Menu")
page = st.sidebar.selectbox("Select a page:", ["Overview"])

if page == "Overview":
    st.title("Dashboard")
    st.write("Nicholas Sidharta")

    st.header("Late Orders Analysis")
    st.write("This section analyzes late orders.")
    
    late_deliveries, num_late_deliveries, num_on_time_deliveries = compute_late_analysis()
    
    st.write("Number of late deliveries:", num_late_deliveries)
    st.write("Number of on-time deliveries:", num_on_time_deliveries)
    st.write("Percentage of late deliveries:", (num_late_deliveries / (num_late_deliveries + num_on_time_deliveries))*100)
    
    st.write("Pie chart of late deliveries: ")
    show_plot_late_orders(num_late_deliveries, num_on_time_deliveries)
    
    st.write("Distribution of late deliveries (in-days): ")
    show_plot_late_days(dist_late_orders(late_deliveries))
    
    st.header("Conclusion")
    st.write("Based on the data analysis conducted, it was found that the percentage of delivery delays is 6.6%. From these delivery delays, it can be observed that the most common occurrence on the bar graph is for 1 day, thus it can be concluded that the most common delivery delay is 1 day from the initial delivery estimate.")
    
    st.header("Customer Demographics Analysis")
    st.write("This plot shows the distribution of customer locations in Brazil.")
    
    show_brazil(merge_datasets())

    st.header("Conclusion")
    st.write("Based on the data analysis conducted, it can be seen that orders occur frequently in the eastern region of Brazil. It can be estimated that the cities with the highest number of orders are in the areas of Sao Paulo and Rio de Janeiro.")