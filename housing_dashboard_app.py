
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Statistical Housing Dashboard", layout="wide")

st.title(" Statistical Analysis of Housing Data")

# Load data
df = pd.read_csv("cleaned_housing_data.csv")

st.markdown("###  Dataset Overview")
st.dataframe(df.head())

# Show key statistics
st.markdown("###  Summary Statistics")
st.dataframe(df.describe())

# Additional statistics
st.markdown("###  Additional Statistics")
st.write("**Median**")
st.dataframe(df.median(numeric_only=True))
st.write("**Mode**")
st.dataframe(df.mode(numeric_only=True).iloc[0])
st.write("**Range**")
st.dataframe(df.max(numeric_only=True) - df.min(numeric_only=True))
st.write("**Variance**")
st.dataframe(df.var(numeric_only=True))
st.write("**Standard Deviation**")
st.dataframe(df.std(numeric_only=True))

# Correlation matrix
st.markdown("###  Correlation Matrix")
fig_corr, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig_corr)

# Pairplot of top correlated features
st.markdown("###  Scatter Relationships (Top Correlated Features with Price)")
top_features = df[['price', 'sqft_living', 'bathrooms', 'sqft_above', 'view']]
fig_pair = px.scatter_matrix(top_features, dimensions=top_features.columns, color="price")
st.plotly_chart(fig_pair, use_container_width=True)

# Z-score distribution
st.markdown("###  Z-Score Distribution (Normalized)")
z_scores = (df.select_dtypes(include='number') - df.select_dtypes(include='number').mean()) / df.select_dtypes(include='number').std()
st.line_chart(z_scores.head(50))
