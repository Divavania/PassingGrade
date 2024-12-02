import pickle
import streamlit as st
import pandas as pd
import altair as alt

# Memuat model prediksi passing grade dari file .sav
try:
    model = pickle.load(open('passing_grade_model.sav', 'rb'))
except FileNotFoundError:
    st.error("File model 'passing_grade_model.sav' tidak ditemukan. Pastikan file tersebut ada.")
    model = None

st.title('📈 Prediksi Passing Grade')
st.markdown("""
Aplikasi ini memprediksi nilai **Passing Grade (MIN)** berdasarkan nilai **RATAAN** dan **S.BAKU**.
Gunakan menu di *sidebar* untuk memilih antara melihat dataset, grafik, atau melakukan prediksi.
""")

# Membaca file CSV untuk dataset
try:
    df_passing_grade = pd.read_csv('passing-grade.csv')
    df_passing_grade.reset_index(inplace=True)
    df_passing_grade.dropna(subset=['RATAAN', 'S.BAKU'], inplace=True)
except FileNotFoundError:
    st.error("File 'passing-grade.csv' tidak ditemukan. Pastikan file tersebut ada.")
    df_passing_grade = None

# Sidebar untuk navigasi
st.sidebar.header("Navigasi")
menu_option = st.sidebar.selectbox(
    "Pilih menu:",
    ["Lihat Dataset", "Tampilkan Grafik", "Prediksi Passing Grade"]
)

# Fungsi untuk menampilkan dataset
if menu_option == "Lihat Dataset":
    if df_passing_grade is not None:
        st.header("📊 Dataset Passing Grade")
        st.write("### Data Passing Grade")
        st.dataframe(df_passing_grade)
    else:
        st.warning("Dataset tidak tersedia.")

# Fungsi untuk menampilkan grafik
elif menu_option == "Tampilkan Grafik":
    if df_passing_grade is not None:
        # Grafik Nilai RATAAN
        st.write("### Grafik Nilai RATAAN")
        chart_rataan = alt.Chart(df_passing_grade).mark_line().encode(
            x=alt.X('index:Q', title='Index'),
            y=alt.Y('RATAAN:Q', title='Nilai RATAAN'),
            tooltip=['index', 'RATAAN']
        ).properties(
            title='Perubahan Nilai RATAAN'
        )
        st.altair_chart(chart_rataan, use_container_width=True)

        # Grafik hubungan antara RATAAN, MIN, dan MAX
        st.write("### Grafik Hubungan antara RATAAN, MIN, dan MAX")
        line_chart = alt.Chart(df_passing_grade).mark_line().encode(
            x=alt.X('RATAAN:Q', title='Nilai RATAAN'),
            y=alt.Y('MIN:Q', title='Nilai MIN'),
            tooltip=['RATAAN', 'MIN']
        ).properties(
            title='Hubungan antara RATAAN dan Nilai MIN'
        )

        line_chart_max = alt.Chart(df_passing_grade).mark_line(color='red').encode(
            x=alt.X('RATAAN:Q', title='Nilai RATAAN'),
            y=alt.Y('MAX:Q', title='Nilai MAX'),
            tooltip=['RATAAN', 'MAX']
        )

        # Menggabungkan grafik MIN dan MAX
        combined_chart = line_chart + line_chart_max
        st.altair_chart(combined_chart, use_container_width=True)
        
        # Grafik 10 prodi dengan nilai terbaik
        st.write("### Sebaran 10 Prodi dengan Nilai Passing Grade Terbaik")
        if df_passing_grade is not None:
            top_10_best_programs = df_passing_grade.nsmallest(10, 'MIN')
            
            best_programs_chart = alt.Chart(top_10_best_programs).mark_bar().encode(
                x=alt.X('NAMA PRODI:N', title='Nama Prodi', sort='-y'),
                y=alt.Y('MIN:Q', title='Nilai Passing Grade (MIN)'),
                color=alt.Color('PTN:N', title='PTN'),
                tooltip=['NAMA PRODI', 'PTN', 'MIN']
            ).properties(
                title='Sebaran 10 Prodi dengan Nilai Passing Grade Terbaik'
            ).configure_axisX(
                labelAngle=-45
            )
            
            st.altair_chart(best_programs_chart, use_container_width=True)
    else:
        st.warning("Dataset tidak tersedia untuk menampilkan grafik.")

# Fungsi untuk melakukan prediksi
elif menu_option == "Prediksi Passing Grade":
    st.header("🔮 Prediksi Passing Grade")
    
    # Input nilai
    st.write("### Masukkan Data untuk Prediksi")
    rataan = st.number_input('Masukkan Nilai RATAAN', min_value=0, max_value=800, value=0)
    sbaku = st.number_input('Masukkan Nilai S.BAKU', min_value=0, max_value=30, value=0)
    
    # Input PTN dan prodi
    st.write("### Informasi PTN dan Prodi")
    selected_ptn = st.text_input("Masukkan PTN (misal: Universitas Indonesia)")
    selected_prodi = st.text_input("Masukkan Prodi (misal: Teknik Informatika)")
    
    if st.button('Prediksi'):
        if model:
            try:
                # Melakukan prediksi passing grade
                passing_grade_prediction = model.predict([[rataan, sbaku]])
                predicted_min = float(passing_grade_prediction[0])

                # Menampilkan hasil prediksi
                st.write(f"**Prediksi Passing Grade (MIN)** untuk PTN **{selected_ptn.upper()}** dan Prodi **{selected_prodi.upper()}**:")
                st.success(f"**{predicted_min:.2f}**")
                st.write("""
                Nilai ini menunjukkan nilai minimum yang diprediksi agar Anda lulus.
                Pastikan untuk mempersiapkan dengan baik!
                """)

                # Mencari 5 PTN dan Prodi dengan passing grade terdekat
                st.subheader("🎓 Rekomendasi PTN dan Prodi")
                st.write("""
                Berikut merupakan rekomendasi Perguruan Tinggi Negeri dan Program Studi,
                berdasarkan Prediksi Passing Grade (MIN) :
                """)
                if df_passing_grade is not None:
                    df_passing_grade['selisih'] = abs(df_passing_grade['MIN'] - predicted_min)
                    top_recommendations = df_passing_grade.nsmallest(5, 'selisih')
                    top_recommendations_table = top_recommendations[['PTN', 'NAMA PRODI', 'MIN']]
                    top_recommendations_table['Passing Grade (MIN) Terdekat'] = top_recommendations_table['MIN'].apply(lambda x: f"{x:.2f}")
                    st.table(top_recommendations_table[['PTN', 'NAMA PRODI', 'Passing Grade (MIN) Terdekat']])

            except Exception as e:
                st.error(f"Terjadi kesalahan saat melakukan prediksi: {e}")
        else:
            st.error("Model tidak tersedia. Pastikan file 'passing_grade_model.sav' berhasil dimuat.")