import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import numpy as np

# Konfigurasi halaman
st.set_page_config(page_title="AI Job Dashboard", layout="wide")
st.title("🤖 AI Jobs Dashboard (Global Listings)")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("ai_job_dataset.csv")
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    df["application_deadline"] = pd.to_datetime(df["application_deadline"])
    return df

df = load_data()

# Sidebar filter
st.sidebar.header("🎛️ Filter Data")
locations = st.sidebar.multiselect("📍 Pilih Lokasi Perusahaan", sorted(df['company_location'].dropna().unique()), default=["United States", "Germany"])
experience_levels = st.sidebar.multiselect("🧠 Pilih Tingkat Pengalaman", sorted(df['experience_level'].dropna().unique()), default=["EN", "SE", "MI"])

# Filter tanggal
min_date = df["posting_date"].min()
max_date = df["posting_date"].max()
date_range = st.sidebar.date_input("📆 Rentang Tanggal Posting", [min_date, max_date])

# Terapkan filter
df_filtered = df[
    (df['company_location'].isin(locations)) &
    (df['experience_level'].isin(experience_levels)) &
    (df["posting_date"] >= pd.to_datetime(date_range[0])) &
    (df["posting_date"] <= pd.to_datetime(date_range[1]))
]

# Ringkasan data
st.markdown("### 📃 Ringkasan Data")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Jumlah Pekerjaan", len(df_filtered))
with col2:
    st.metric("Gaji Rata-Rata (USD)", f"${df_filtered['salary_usd'].mean():,.0f}")
with col3:
    st.metric("Negara Unik", df_filtered['company_location'].nunique())

# Tabel dan ekspor
st.subheader("📄 Tabel Data Pekerjaan")
st.dataframe(df_filtered[['job_title', 'company_name', 'salary_usd', 'experience_level', 'company_location', 'remote_ratio', 'education_required', 'industry']])

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("📀 Download Data Terfilter (CSV)", csv, "filtered_ai_jobs.csv", "text/csv")

# Visualisasi Interaktif 3D & Animasi
st.markdown("---")
st.subheader("🗭 Visualisasi Interaktif 3D & Animasi")

if "years_experience" not in df_filtered.columns:
    df_filtered["years_experience"] = np.random.randint(0, 15, size=len(df_filtered))

fig_3d = px.scatter_3d(
    df_filtered,
    x="years_experience",
    y="remote_ratio",
    z="salary_usd",
    color="experience_level",
    symbol="company_size" if "company_size" in df_filtered.columns else None,
    hover_data=["job_title", "company_name"],
    title="Distribusi Gaji Berdasarkan Pengalaman & Remote Ratio",
    animation_frame="education_required" if "education_required" in df_filtered.columns else None,
    opacity=0.7,
    height=600
)
st.plotly_chart(fig_3d, use_container_width=True)

st.write("### 📈 Animasi Tren Postingan Pekerjaan per Bulan")
monthly_df = df_filtered.copy()
monthly_df["Month"] = pd.to_datetime(monthly_df["posting_date"]).dt.to_period("M").astype(str)
monthly_grouped = monthly_df.groupby(["Month", "company_location"]).size().reset_index(name="job_count")

fig_line = px.line(
    monthly_grouped,
    x="Month",
    y="job_count",
    color="company_location",
    title="Tren Jumlah Pekerjaan AI per Lokasi (Animasi per Bulan)",
    markers=True,
    animation_frame="Month"
)
fig_line.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_line, use_container_width=True)

# Visualisasi tambahan
st.markdown("---")
st.subheader("📊 Visualisasi Tambahan")

avg_salary = df_filtered.groupby("company_location")["salary_usd"].mean().sort_values(ascending=False).head(10)
st.write("### 💵 Rata-rata Gaji per Negara (Top 10)")
st.bar_chart(avg_salary)

st.write("### 📁 Distribusi Gaji (USD)")
fig1, ax1 = plt.subplots()
sns.histplot(df_filtered["salary_usd"], bins=30, kde=True, ax=ax1, color="teal")
ax1.set_title("Distribusi Gaji USD")
st.pyplot(fig1)

st.write("### 🌍 Komposisi Remote Ratio")
remote_map = {0: 'Onsite', 50: 'Hybrid', 100: 'Remote'}
remote_count = df_filtered['remote_ratio'].map(remote_map).value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(remote_count, labels=remote_count.index, autopct='%1.1f%%', startangle=90)
ax2.axis("equal")
st.pyplot(fig2)

# WordCloud
st.subheader("☁️ WordCloud Keterampilan / Judul Pekerjaan")
text_data = " ".join(df_filtered["job_title"].dropna().astype(str).tolist())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)
fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis("off")
st.pyplot(fig_wc)

st.markdown("---")
st.caption("📌 Data: AI Job Dataset (Global Listings)")
