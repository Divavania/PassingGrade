import pickle
import streamlit as st
import pandas as pd
import altair as alt

# Memuat model prediksi passing grade dari file .sav
try:
    model = pickle.load(open('passing_grade_model.sav', 'rb'))
except FileNotFoundError:
    st.error("File model 'passing_grade_model.sav' tidak ditemukan. Pastikan file tersebut ada.")
    model = None  # Inisialisasi model sebagai None jika file tidak ditemukan

# Judul aplikasi
st.title('📈 Prediksi Passing Grade')
st.markdown("""
Aplikasi ini memprediksi nilai **Passing Grade (MIN)** berdasarkan nilai **RATAAN** dan **S.BAKU**.
Gunakan input di *sidebar* untuk memasukkan nilai, lalu klik tombol **Prediksi**.
""")

# Membaca file CSV untuk dataset
try:
    df_passing_grade = pd.read_csv('passing-grade.csv')
    st.header("📊 Dataset Passing Grade")
    df_passing_grade.reset_index(inplace=True)  # Reset index untuk memastikan kolom index tersedia
    df_passing_grade.dropna(subset=['RATAAN', 'S.BAKU'], inplace=True)  # Membersihkan data dari nilai kosong

    # Menampilkan dataset
    st.write("### Data Passing Grade")
    st.dataframe(df_passing_grade)

    # Grafik Nilai RATAAN dengan penyesuaian visual
    st.write("### Grafik Nilai RATAAN")
    chart_rataan = alt.Chart(df_passing_grade).mark_line().encode(
        x=alt.X('index:Q', title='Index'),
        y=alt.Y('RATAAN:Q', title='Nilai RATAAN'),
        tooltip=['index', 'RATAAN']
    ).properties(
        title='Perubahan Nilai RATAAN'
    )
    st.altair_chart(chart_rataan, use_container_width=True)
except FileNotFoundError:
    st.error("File 'passing-grade.csv' tidak ditemukan. Pastikan file tersebut ada.")
    df_passing_grade = None  # Inisialisasi kosong jika file tidak ditemukan

# Sidebar untuk input nilai
st.sidebar.header("Masukkan Nilai")
rataan = st.sidebar.number_input('Masukkan Nilai RATAAN', min_value=0, max_value=1000, value=500)
sbaku = st.sidebar.number_input('Masukkan Nilai S.BAKU', min_value=0, max_value=100, value=50)

# Sidebar untuk input PTN dan prodi
st.sidebar.header("Informasi PTN dan Prodi")
selected_ptn = st.sidebar.text_input("Masukkan PTN (misal: Universitas Indonesia)")
selected_prodi = st.sidebar.text_input("Masukkan Prodi (misal: Teknik Informatika)")

# Tombol prediksi dan hasil
if st.sidebar.button('Prediksi'):
    if model:  # Pastikan model berhasil dimuat
        try:
            passing_grade_prediction = model.predict([[rataan, sbaku]])
            predicted_min = float(passing_grade_prediction[0])
            
            # Menampilkan hasil prediksi dengan penjelasan
            st.header("🔮 Hasil Prediksi")
            st.write(f"**Prediksi Passing Grade (MIN)** untuk PTN **{selected_ptn}** dan Prodi **{selected_prodi}** dengan nilai RATAAN {rataan} dan S.BAKU {sbaku} adalah:")
            
            # Menyajikan hasil dengan penjelasan sederhana
            st.success(f"**{predicted_min:.2f}**")
            st.write("""
            Nilai ini menunjukkan nilai minimum yang diprediksi agar Anda lulus.
            Pastikan untuk mempersiapkan dengan baik dan mempertahankan nilai di atas angka ini untuk mencapai kelulusan.
            """)
            
            # Saran tambahan berdasarkan nilai prediksi
            if predicted_min < 500:
                st.warning("Prediksi ini menunjukkan bahwa nilai minimum lulus cukup rendah. Pastikan untuk belajar lebih giat!")
            elif 500 <= predicted_min < 750:
                st.info("Prediksi ini menunjukkan nilai minimum lulus yang cukup moderat. Teruslah belajar dan jaga performa Anda!")
            else:
                st.success("Prediksi ini menunjukkan nilai minimum lulus yang tinggi. Pertahankan usaha dan tetap fokus!")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat melakukan prediksi: {e}")
    else:
        st.error("Model tidak tersedia. Pastikan file 'passing_grade_model.sav' berhasil dimuat.")