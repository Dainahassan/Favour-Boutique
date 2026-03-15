import streamlit as st
import pandas as pd
from datetime import datetime
import os

file = "sales.csv"

st.set_page_config(page_title="Boutique Dashboard", layout="wide")

# Theme styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: silver;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Boutique Sales Dashboard")

# Create file if not exists
if not os.path.exists(file):
    df = pd.DataFrame(columns=["Date","Item","Buying Price","Selling Price","Quantity","Revenue","Profit"])
    df.to_csv(file,index=False)

df = pd.read_csv(file)

# SALES ENTRY
st.header("Add New Sale")

item = st.text_input("Item name")
buy = st.number_input("Buying price",0.0)
sell = st.number_input("Selling price",0.0)
qty = st.number_input("Quantity sold",1)

if st.button("Save Sale"):

    revenue = sell * qty
    profit = (sell - buy) * qty

    new = pd.DataFrame({
        "Date":[datetime.today().strftime("%Y-%m-%d")],
        "Item":[item],
        "Buying Price":[buy],
        "Selling Price":[sell],
        "Quantity":[qty],
        "Revenue":[revenue],
        "Profit":[profit]
    })

    df = pd.concat([df,new],ignore_index=True)
    df.to_csv(file,index=False)

    st.success(f"Sale saved. Profit: {profit}")

# DASHBOARD
st.header("Business Overview")

total_revenue = df["Revenue"].sum()
total_profit = df["Profit"].sum()
total_items = df["Quantity"].sum()

col1,col2,col3 = st.columns(3)

col1.metric("Total Revenue", total_revenue)
col2.metric("Total Profit", total_profit)
col3.metric("Items Sold", total_items)

# SALES TABLE
st.header("Sales History")
st.dataframe(df)

# BEST SELLING ITEMS
st.header("Top Selling Products")

top_items = df.groupby("Item")["Quantity"].sum().sort_values(ascending=False)

st.bar_chart(top_items)
