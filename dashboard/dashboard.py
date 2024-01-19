import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_order_items_df(df):
    sum_order_items_df = df['df_order_item'].value_counts()
    return sum_order_items_df

def create_review_df(df):
    review_df = df['review_score'].value_counts()
    return review_df

def create_rfm_df(df, now):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'])
    recency=df.groupby('customer_id', as_index=False)['order_purchase_timestamp'].max()
    recency.columns = ['customer_id', 'last_purchase']
    recency['Recency'] = (now - recency['last_purchase']).dt.days
    recency = recency[['customer_id', 'Recency']]
    
    frequency=df.groupby('customer_id', as_index=False)['order_id'].count()
    frequency.columns = ['customer_id', 'Frequency']
    
    monetary = df.groupby('customer_id', as_index=False)['payment_value'].sum()
    monetary.columns = ['customer_id', 'Monetary']
    
    rfm_df = pd.merge(
        left=pd.merge(
            left=recency, 
            right=frequency,
            left_on='customer_id', 
            right_on='customer_id'
        ), 
        right= monetary, 
        left_on='customer_id', 
        right_on='customer_id'
    )
    
    return rfm_df

# Load data
all_df = pd.read_csv("dashboard/all_data.csv")
all_df['order_purchase_timestamp']=pd.to_datetime(all_df['order_purchase_timestamp'])
now = pd.to_datetime('2018-09-1 00:00:00')
order_items_df = create_sum_order_items_df(all_df)
review_df = create_review_df(all_df)
rfm_df = create_rfm_df(all_df, now)

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://img.freepik.com/free-vector/gradient-instagram-shop-logo-template_23-2149704603.jpg?w=1060&t=st=1705675551~exp=1705676151~hmac=e2914c1f9e6aa4193ebb1a527a1630b0ef3fc10043b858dfcd3be9fb7c51d861")
    
st.header('Smile Shop Online Store :sparkles:')

# Visualisasi 1
st.subheader('Review Score')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x=review_df.keys(),
            y=review_df.values,
            order=review_df.keys(),
            )
ax.bar_label(ax.containers[0])
ax.set_xlabel(None)
st.pyplot(fig)

# Visualisasi 2
st.subheader("Products with the Most and Lowest Interest")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24,6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_item_id", y="product_category_name", data=order_items_df.sort_values(by="order_item_id", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("5 Products with High Interest", loc="center", fontsize=15)
ax[0].tick_params(axis = 'y', labelsize=12)

sns.barplot(x="order_item_id", y="product_category_name", data=order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("5 Products with Low Interest", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

st.pyplot(fig)

# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")
st.metric("Time Assumption", str(now))
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(create_rfm_df.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(create_rfm_df.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(create_rfm_df.Monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="Recency", x="customer_id", data=create_rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35,labelbottom=False)
ax[0].set_xlabel(None)

sns.barplot(y="Frequency", x="customer_id", data=create_rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35,labelbottom=False)
ax[1].set_xlabel(None)

sns.barplot(y="Monetary", x="customer_id", data=create_rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35,labelbottom=False)
ax[2].set_xlabel(None)

st.pyplot(fig)

st.caption('Copyright © deviliadc - deviliadcandra@gmail.com')
