import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set up style for seaborn
sns.set(style='whitegrid')

# Title and sidebar navigation
st.title('E-Commerce Data Dashboard')
st.sidebar.title("Navigation")
dashboard_selection = st.sidebar.selectbox("Choose a dashboard section:", 
                                           ["Top Products", "Monthly Orders", "Geographical Analysis"])

# Load datasets
combined_dat = pd.read_csv('datasets/combined_dat.csv')
customers_df = pd.read_csv('datasets/customers_geo.csv')

# Section 1: Top Products Analysis
if dashboard_selection == "Top Products":
    st.header("Top and Bottom Products by Sales")

    # Calculate top and bottom products
    top_products_df = combined_dat.groupby("product_category_name_english").agg(products=("product_id", "count")).sort_values("products", ascending=False).head(10).reset_index()
    bottom_products_df = combined_dat.groupby("product_category_name_english").agg(products=("product_id", "count")).sort_values("products", ascending=True).head(10).reset_index()

    # Plot
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    sns.barplot(x='product_category_name_english', y='products', data=top_products_df, ax=ax[0], palette="viridis")
    ax[0].set_title("Top 10 Products Sold")
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=90)
    sns.barplot(x='product_category_name_english', y='products', data=bottom_products_df, ax=ax[1], palette="plasma")
    ax[1].set_title("Bottom 10 Products Sold")
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=90)
    st.pyplot(fig)

# Section 2: Monthly Orders Analysis
elif dashboard_selection == "Monthly Orders":
    st.header("Monthly Orders Analysis")
    
    # Convert 'order_approved_at' to datetime
    combined_dat['order_approved_at'] = pd.to_datetime(combined_dat['order_approved_at'])

    # Aggregate orders by month
    monthly_df = combined_dat.resample('M', on='order_approved_at').agg({"order_id": "nunique"})
    monthly_df.index = monthly_df.index.strftime('%B')
    monthly_df = monthly_df.reset_index().rename(columns={"order_id": "order_count", "order_approved_at": "month"})
    monthly_df = monthly_df.sort_values('order_count').drop_duplicates('month', keep='last')

    # Sort by month order
    month_mapping = {month: index for index, month in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], start=1)}
    monthly_df["month_numeric"] = monthly_df["month"].map(month_mapping)
    monthly_df = monthly_df.sort_values("month_numeric").drop("month_numeric", axis=1)

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_df["month"], monthly_df["order_count"], marker='o', linewidth=2, color="#068DA9")
    plt.title("Number of Orders per Month (2018)", fontsize=20)
    plt.xticks(rotation=25)
    plt.yticks(fontsize=10)
    
    for x, y in zip(monthly_df["month"], monthly_df["order_count"]):
        plt.text(x, y, str(y), fontsize=9, ha='center', va='bottom')

    st.pyplot(plt)

# Section 3: Geographical Analysis
elif dashboard_selection == "Geographical Analysis":
    st.header("Customer Distribution by State")

    bystate_df = combined_dat.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    palette = ["#068DA9" if state == most_common_state else "#D3D3D3" for state in bystate_df['customer_state']]

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='customer_state', y='customer_count', data=bystate_df, palette=palette)
    
    plt.title("Customer Count by State", fontsize=20)
    plt.xticks(rotation=90)
    
    st.pyplot(plt)


    # Display geographical distribution map
    st.subheader("Maps Geographical Customer Distribution")
    customers_df.rename(columns={'geolocation_lat': 'lat', 'geolocation_lng': 'lon'}, inplace=True)
    st.map(customers_df[['lat', 'lon']].dropna())
