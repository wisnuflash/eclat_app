from datetime import time
import streamlit as st
import pandas as pd
from utils.database import fetch_stock_data, add_stock_obat, update_stock_obat, delete_stock_obat
import time

def show_manajemen_obat():
    """
    Function utama untuk menampilkan halaman manajemen obat
    """
    st.title("Manajemen Data Obat")

    # Initialize session state untuk tracking perubahan
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # Function untuk load data fresh dari database
    def load_fresh_data():
        try:
            original_data = fetch_stock_data()
            if original_data:
                df = pd.DataFrame(original_data)
                # Pastikan kolom sesuai dengan database
                if not df.empty:
                    # Konversi tipe data yang sesuai
                    df['id_obat'] = df['id_obat'].astype('Int64')  # Nullable integer
                    df['stok'] = df['stok'].astype('Int64')
                    df['nama_obat'] = df['nama_obat'].astype(str)
            else:
                # Jika tidak ada data, buat DataFrame kosong dengan struktur yang benar
                df = pd.DataFrame(columns=["id_obat", "nama_obat", "stok"])
                df['id_obat'] = df['id_obat'].astype('Int64')
                df['stok'] = df['stok'].astype('Int64')
            
            return df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame(columns=["id_obat", "nama_obat", "stok"])

    # Load data awal atau refresh
    if not st.session_state.data_loaded or st.button("🔄 Refresh Data"):
        st.session_state.df_original = load_fresh_data()
        st.session_state.data_loaded = True

    # Tampilkan info jumlah data
    if not st.session_state.df_original.empty:
        st.info(f"📊 Total data: {len(st.session_state.df_original)} obat")
    else:
        st.warning("📝 Belum ada data. Tambahkan data baru dengan mengklik tombol '+' di bawah tabel.")

    # Data Editor dengan konfigurasi yang lebih baik
    edited_df = st.data_editor(
        st.session_state.df_original,
        column_config={
            "id_obat": st.column_config.NumberColumn(
                "ID Obat",
                help="ID akan otomatis terisi untuk data baru",
                disabled=False,  # Allow input untuk baris baru, tapi akan diabaikan
                width="small"
            ),
            "nama_obat": st.column_config.TextColumn(
                "Nama Obat",
                help="Masukkan nama obat",
                max_chars=100,
                width="medium"
            ),
            "stok": st.column_config.NumberColumn(
                "Stok",
                help="Jumlah stok obat",
                min_value=0,
                step=1,
                width="small"
            )
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_obat"  # Unique key untuk menghindari konflik
    )

    # Tombol Simpan dengan pengecekan perubahan
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Simpan Perubahan", type="primary", use_container_width=True):
            try:
                success_messages = []
                error_messages = []
                
                # Bersihkan data yang invalid (nama_obat kosong atau NaN)
                valid_edited_df = edited_df.dropna(subset=['nama_obat'])
                valid_edited_df = valid_edited_df[valid_edited_df['nama_obat'].str.strip() != '']
                
                # Reset index untuk operasi yang lebih mudah
                valid_edited_df = valid_edited_df.reset_index(drop=True)
                original_df = st.session_state.df_original.reset_index(drop=True)
                
                # Konversi ID ke set untuk perbandingan (hanya yang tidak NaN)
                original_ids = set()
                if not original_df.empty:
                    original_ids = set(original_df['id_obat'].dropna().astype(int))
                
                edited_ids = set()
                if not valid_edited_df.empty:
                    edited_ids = set(valid_edited_df['id_obat'].dropna().astype(int))
                
                # --- 1. PROSES BARIS BARU (ID kosong/NaN) ---
                new_rows = valid_edited_df[valid_edited_df['id_obat'].isna()]
                print(f"New rows to add: {len(new_rows)}")
                if not new_rows.empty:
                    st.info(f"🔄 Menambahkan {len(new_rows)} data baru...")
                    for _, row in new_rows.iterrows():
                        try:
                            # Untuk baris baru, jangan kirim id_obat (biarkan AUTO_INCREMENT)
                            add_stock_obat(
                                nama_obat=str(row["nama_obat"]).strip(),
                                stok=int(row["stok"]) if pd.notna(row["stok"]) else 0 # Pastikan stok tidak NaN, default ke 0
                            )   
                            success_messages.append(f"✅ Berhasil menambah: {row['nama_obat']}")
                            time.sleep(1)  # Delay untuk menghindari masalah dengan banyak request
                        except Exception as e:
                            error_messages.append(f"❌ Gagal menambah {row['nama_obat']}: {str(e)}")
                
                # --- 2. PROSES BARIS YANG DIUBAH ---
                existing_rows = valid_edited_df[valid_edited_df['id_obat'].notna()]
                if not existing_rows.empty and not original_df.empty:
                    for _, row in existing_rows.iterrows():
                        try:
                            id_obat = int(row["id_obat"])
                            # Cari data asli berdasarkan ID
                            original_row = original_df[original_df["id_obat"] == id_obat]
                            
                            if not original_row.empty:
                                ori = original_row.iloc[0]
                                # Cek apakah ada perubahan
                                nama_changed = str(row["nama_obat"]).strip() != str(ori["nama_obat"]).strip()
                                stok_changed = int(row["stok"]) != int(ori["stok"])
                                
                                if nama_changed or stok_changed:
                                    update_stock_obat(
                                        id_obat=id_obat,
                                        nama_obat=str(row["nama_obat"]).strip(),
                                        stok=int(row["stok"]) if pd.notna(row["stok"]) else 0
                                    )
                                    success_messages.append(f"✅ Berhasil update: {row['nama_obat']}")
                        except Exception as e:
                            error_messages.append(f"❌ Gagal update {row['nama_obat']}: {str(e)}")
                
                # --- 3. PROSES BARIS YANG DIHAPUS ---
                deleted_ids = original_ids - edited_ids
                if deleted_ids:
                    st.info(f"🗑️ Menghapus {len(deleted_ids)} data...")
                    for id_obat in deleted_ids:
                        try:
                            # Cari nama obat untuk pesan
                            deleted_row = original_df[original_df["id_obat"] == id_obat]
                            nama_obat = deleted_row.iloc[0]["nama_obat"] if not deleted_row.empty else f"ID {id_obat}"
                            
                            delete_stock_obat(int(id_obat))
                            success_messages.append(f"✅ Berhasil hapus: {nama_obat}")
                        except Exception as e:
                            error_messages.append(f"❌ Gagal hapus ID {id_obat}: {str(e)}")
                
                # Tampilkan hasil operasi
                if success_messages:
                    for msg in success_messages:
                        st.success(msg)
                
                if error_messages:
                    for msg in error_messages:
                        st.error(msg)
                
                if not success_messages and not error_messages:
                    st.info("ℹ️ Tidak ada perubahan yang perlu disimpan.")
                
                # Refresh data setelah operasi berhasil
                if success_messages:
                    st.session_state.df_original = load_fresh_data()
                    st.success("🎉 Data berhasil disinkronkan dengan database!")
                    time.sleep(1)  # Delay untuk memastikan UI update
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error dalam proses penyimpanan: {str(e)}")

    # Tampilkan informasi perubahan
    if not edited_df.equals(st.session_state.df_original):
        st.warning("⚠️ **Ada perubahan yang belum disimpan!**")
        
        # Show preview perubahan
        with st.expander("👁️ Preview Perubahan"):
            col_preview1, col_preview2 = st.columns(2)
            
            with col_preview1:
                st.write("**Data Asli:**")
                st.dataframe(st.session_state.df_original, use_container_width=True, height=200)
            
            with col_preview2:
                st.write("**Data Setelah Edit:**")
                st.dataframe(edited_df, use_container_width=True, height=200)

    # Instruksi penggunaan
    st.markdown("---")
    with st.expander("📖 Petunjuk Penggunaan"):
        st.markdown("""
        ### 🔧 **Cara Menggunakan Editor:**
        
        1. **➕ Tambah Data Baru:**
           - Klik tombol **"+"** di bawah tabel
           - Isi nama obat dan stok (biarkan ID kosong, akan otomatis terisi)
        
        2. **✏️ Edit Data:**
           - Klik langsung pada sel yang ingin diubah
           - Edit nama obat atau stok sesuai kebutuhan
        
        3. **🗑️ Hapus Data:**
           - Klik tombol **"🗑️"** di sebelah kiri baris yang ingin dihapus
           - Atau hapus semua isi nama obat (kosongkan)
        
        4. **💾 Simpan:**
           - Klik **"Simpan Perubahan ke Database"** untuk menyimpan semua perubahan
           - Sistem akan otomatis mendeteksi data baru, yang diubah, dan yang dihapus
        
        ### ⚠️ **Penting:**
        - ID Obat untuk data baru akan otomatis terisi oleh sistem
        - Nama obat tidak boleh kosong
        - Stok harus berupa angka (minimal 0)
        - Perubahan baru tersimpan setelah klik tombol "Simpan"
        """)

    # Footer dengan statistik
    if not st.session_state.df_original.empty:
        total_stok = st.session_state.df_original['stok'].sum()
        rata_stok = st.session_state.df_original['stok'].mean()
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Total Obat", len(st.session_state.df_original))
        with col_stat2:
            st.metric("Total Stok", total_stok)
        with col_stat3:
            st.metric("Rata-rata Stok", f"{rata_stok:.1f}")

# Untuk testing langsung file ini
if __name__ == "__main__":
    show_manajemen_obat()