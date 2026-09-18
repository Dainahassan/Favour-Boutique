import streamlit as st
import pandas as pd
from datetime import datetime
import os

sales_file = "sales.csv"
inventory_file = "inventory.csv"

st.set_page_config(page_title="Boutique POS v5", layout="wide")

# Theme
st.markdown("""
<style>
.stApp {
    background-color: black;
    color: silver;
}
</style>
""", unsafe_allow_html=True)

st.title("Boutique POS System (Version 5)")

# Create files if missing
if not os.path.exists(sales_file):
    pd.DataFrame(columns=["Date","Item","Buy","Sell","Qty","Revenue","Profit"]).to_csv(sales_file,index=False)

if not os.path.exists(inventory_file):
    pd.DataFrame(columns=["Item","Stock","Buy Price","Sell Price","Supplier","Last Restock"]).to_csv(inventory_file,index=False)

sales = pd.read_csv(sales_file)
inventory = pd.read_csv(inventory_file)

tab1, tab2, tab3 = st.tabs(["Sales","Inventory","Analytics"])

# ---------------- SALES ----------------
with tab1:

    st.header("Record Sale")

    if inventory.empty:
        st.warning("Add inventory first.")
    else:
        item = st.selectbox("Select Item", inventory["Item"].unique(), key="sale_item")

        selected = inventory[inventory["Item"] == item].iloc[0]

        buy_price = selected["Buy Price"]
        sell_price = st.number_input("Selling price", 0.0, key="sale_sell")
        stock = selected["Stock"]

        sale_date = st.date_input("Sale Date", datetime.today(), key="sale_date")
        qty = st.number_input("Quantity sold", 1, key="sale_qty")

        st.write(f"Stock Available: {stock}")

        if st.button("Save Sale"):

            if qty > stock:
                st.error("Not enough stock!")
            else:
                revenue = sell_price * qty
                profit = (sell_price - buy_price) * qty

                new = pd.DataFrame({
                    "Date":[sale_date.strftime("%Y-%m-%d")],
                    "Item":[item],
                    "Buy":[buy_price],
                    "Sell":[sell_price],
                    "Qty":[qty],
                    "Revenue":[revenue],
                    "Profit":[profit]
                })

                sales = pd.concat([sales, new])
                sales.to_csv(sales_file, index=False)

                inventory.loc[inventory["Item"] == item, "Stock"] -= qty
                inventory.to_csv(inventory_file, index=False)

                st.success(f"Sale saved. Profit: {profit}")

                # CLEAR INPUTS
                if "sale_qty" not in st.session_state:
                    st.session_state["sale_qty"] = 1
# ---------------- INVENTORY ----------------
with tab2:

    st.header("Inventory Management")

    item_name = st.text_input("Item name", key="inv_item")
    stock = st.number_input("Stock quantity",1, key="inv_stock")
    buy_price = st.number_input("Buying price",0.0, key="inv_buy")
    supplier = st.text_input("Supplier", key="inv_supplier")
    restock_date = st.date_input("Restock Date", datetime.today(), key="inv_date")

    if st.button("Add / Update Item"):

        if item_name in inventory["Item"].values:
            # UPDATE EXISTING ITEM
            inventory.loc[inventory["Item"]==item_name,"Stock"] += stoc
            inventory.loc[inventory["Item"]==item_name,"Last Restock"] = restock_date
        else:
            # NEW ITEM
            new_item = pd.DataFrame({
                "Item":[item_name],
                "Stock":[stock],
                "Buy Price":[buy_price],
                "Supplier":[supplier],
                "Last Restock":[restock_date]
            })

            inventory = pd.concat([inventory,new_item])

        inventory.to_csv(inventory_file,index=False)

        st.success("Inventory updated")
        st.rerun()

        st.session_state["inv_item"] = ""
        st.session_state["inv_stock"] = 1
        st.session_state["inv_buy"] = 0.0
        st.session_state["inv_sell"] = 0.0
        st.session_state["inv_supplier"] = ""

    st.subheader("Current Inventory")
    st.dataframe(inventory)

    # DELETE INVENTORY ITEM
    st.subheader("Delete Item")

    if not inventory.empty:
        del_item = st.selectbox("Select item to delete", inventory["Item"], key="del_inv")

        if st.button("Delete Item"):
            inventory = inventory[inventory["Item"] != del_item]
            inventory.to_csv(inventory_file,index=False)
            st.success("Item deleted")
            st.rerun()

# ---------------- ANALYTICS ----------------
with tab3:

    st.header("Analytics")

    if not sales.empty:

        total_revenue = sales["Revenue"].sum()
        total_profit = sales["Profit"].sum()
        total_items = sales["Qty"].sum()

        col1,col2,col3 = st.columns(3)

        col1.metric("Revenue", total_revenue)
        col2.metric("Profit", total_profit)
        col3.metric("Items Sold", total_items)

        st.subheader("Sales Data")
        st.dataframe(sales)

        # DELETE SALES ENTRY
        st.subheader("Delete Sale Entry")

        sales["ID"] = sales.index

        del_sale = st.selectbox(
            "Select sale to delete",
            sales["ID"],
            format_func=lambda x: f"{sales.loc[x,'Item']} - {sales.loc[x,'Date']} - Qty {sales.loc[x,'Qty']}"
        )

        if st.button("Delete Sale"):
            sales = sales.drop(del_sale)
            sales.to_csv(sales_file,index=False)
            st.success("Sale deleted")
            st.rerun()

    else:
        st.info("No sales yet.")
