import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import os
from pathlib import Path

# Import custom utilities
from utils.eclat_algorithm import ECLATAlgorithm
from utils.data_processing import DataProcessor
from utils.visualization import VisualizationManager
from utils.report_generator import ReportGenerator
from utils.activity_logger import ActivityLogger
from utils.database import fetch_stock_data, add_stock_obat, update_stock_obat, delete_stock_obat, execute_sql_file
from halaman.data_obat import show_manajemen_obat
from utils.database_setup import SQLAlchemySetup

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'eclat_results' not in st.session_state:
    st.session_state.eclat_results = None
if 'association_rules' not in st.session_state:
    st.session_state.association_rules = None

# Initialize components
activity_logger = ActivityLogger()
data_processor = DataProcessor()
eclat_algorithm = ECLATAlgorithm()
viz_manager = VisualizationManager()
report_generator = ReportGenerator()
# Initialize database setup
# db_setup = SQLAlchemySetup()
# Initialize database connection
# if not db_setup.init_database():
#     st.error("❌ Gagal menginisialisasi database. Periksa konfigurasi dan coba lagi.")
# Check if database setup is successful
# if not execute_sql_file(sql_file_path_relative='database_schema.sql'):
#     st.error("❌ Gagal menjalankan file SQL untuk setup database. Periksa file dan coba lagi.")
# else:
#     st.success("✅ Database sudah siap!")
# print("📁 Current working directory:", os.getcwd())
# Main function to run the Streamlit app

# Sidebar navigation dengan design yang lebih baik
def create_sidebar():
    st.sidebar.title("🏥 Pharmacy Management System")
    st.sidebar.markdown("---")
    
    # Initialize session state untuk menyimpan pilihan aktif
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "Manajemen Data Obat"
    
    selected_page = None
    
    # Sidebar dengan navigation menggunakan expander dan button
    with st.sidebar:
        
        # Expander untuk Manajemen Obat
        with st.expander("📊 Manajemen Obat", expanded=True):
            # col1, col2 = st.columns(2)

            if st.button("📋 Data Obat", use_container_width=True):
                selected_page = "Manajemen Data Obat"
                st.session_state.active_page = selected_page

            if st.button("📥 Unduh Laporan", use_container_width=True):
                selected_page = "Unduh Laporan"
                st.session_state.active_page = selected_page
            
            if st.button("📝 Log Aktivitas", use_container_width=True):
                selected_page = "Log Aktivitas"
                st.session_state.active_page = selected_page
        
        # Expander untuk Eclat Analysis
        with st.expander("🔍 Eclat Analysis", expanded=False):
            # col1, col2 = st.columns(2)

            if st.button("📊 Input Data", use_container_width=True):
                selected_page = "Input Data Resep Obat"
                st.session_state.active_page = selected_page

            if st.button("⚙️ Proses Analisis", use_container_width=True):
                selected_page = "Proses Analisis ECLAT"
                st.session_state.active_page = selected_page

            if st.button("📈 Lihat Hasil", use_container_width=True):
                selected_page = "Lihat Hasil Analisis"
                st.session_state.active_page = selected_page
            
            if st.button("💡 Rekomendasi", use_container_width=True):
                selected_page = "Lihat Rekomendasi Obat"
                st.session_state.active_page = selected_page
            
            if st.button("📋 Unduh Laporan Eclat", use_container_width=True):
                selected_page = "Unduh Laporan Eclat"
                st.session_state.active_page = selected_page
        
        # Expander untuk Pengaturan
        with st.expander("⚙️ Pengaturan"):
            st.markdown("**Konfigurasi Analisis:**")
            
            min_support = st.slider("Minimum Support", 0.1, 1.0, 0.3, key="min_support")
            confidence = st.slider("Minimum Confidence", 0.1, 1.0, 0.5, key="confidence")
            max_items = st.number_input("Max Items per Set", 2, 10, 5, key="max_items")
            
            st.markdown("**Database:**")
            if st.button("🔄 Refresh Database", use_container_width=True):
                st.success("Database refreshed!")
            
            if st.button("🗑️ Clear Cache", use_container_width=True):
                st.success("Cache cleared!")
        
        # Expander untuk Info Aplikasi
        with st.expander("ℹ️ Tentang Aplikasi"):
            st.markdown("""
            **Pharmacy Management System v1.0**
            
            **Fitur Utama:**
            - 📊 Manajemen data obat
            - 🔍 Analisis pola dengan algoritma ECLAT
            - 💡 Rekomendasi obat otomatis
            - 📋 Laporan komprehensif
            
            **Teknologi:**
            - Python + Streamlit
            - ECLAT Algorithm
            - Data Analytics
            
            📧 **Support:** admin@pharmacy.com
            📞 **Helpdesk:** 0800-1234-5678
            """)
        
        # Status halaman aktif
        st.markdown("---")
        st.markdown(f"**📍 Halaman Aktif:** {st.session_state.active_page}")
        
        # Footer
        st.markdown("---")
        st.caption("*© 2024 Pharmacy System*")
    
    # Return halaman yang dipilih atau halaman aktif dari session state
    return selected_page if selected_page else st.session_state.active_page

# Alternative: Menggunakan selectbox di dalam expander
def create_sidebar_with_selectbox():
    st.sidebar.title("🏥 Pharmacy Management System")
    st.sidebar.markdown("---")
    
    # Initialize session state
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "Manajemen Data Obat"
    
    selected_page = None
    
    with st.sidebar:
        
        # Expander untuk Manajemen Obat
        with st.expander("📊 Manajemen Obat", expanded=True):
            manajemen_choice = st.selectbox(
                "Pilih Menu:",
                ["-- Pilih Menu --", "Manajemen Data Obat", "Unduh Laporan", "Log Aktivitas"],
                key="manajemen_select"
            )
            
            if manajemen_choice != "-- Pilih Menu --":
                selected_page = manajemen_choice
                st.session_state.active_page = selected_page
        
        # Expander untuk Eclat Analysis
        with st.expander("🔍 Eclat Analysis", expanded=True):
            eclat_choice = st.selectbox(
                "Pilih Analisis:",
                ["-- Pilih Analisis --", "Input Data Resep Obat", "Proses Analisis ECLAT", 
                 "Lihat Hasil Analisis", "Lihat Rekomendasi Obat", "Unduh Laporan Eclat"],
                key="eclat_select"
            )
            
            if eclat_choice != "-- Pilih Analisis --":
                selected_page = eclat_choice
                st.session_state.active_page = selected_page
        
        # Quick Actions
        with st.expander("⚡ Quick Actions"):
            col1, col2 = st.columns(2)
            
            if col1.button("🚀 Quick Start", use_container_width=True):
                selected_page = "Input Data Resep Obat"
                st.session_state.active_page = selected_page
            
            if col2.button("📊 Dashboard", use_container_width=True):
                selected_page = "Lihat Hasil Analisis"
                st.session_state.active_page = selected_page
        
        # Pengaturan
        with st.expander("⚙️ Pengaturan"):
            st.markdown("**Konfigurasi:**")
            min_support = st.slider("Minimum Support", 0.1, 1.0, 0.3)
            max_items = st.number_input("Max Items", 2, 10, 5)
            
            # Save settings button
            if st.button("💾 Simpan Pengaturan", use_container_width=True):
                st.success("✅ Pengaturan disimpan!")
        
        # Info
        with st.expander("ℹ️ Info & Help"):
            st.markdown("""
            **🆘 Butuh Bantuan?**
            
            1. **Getting Started**: Mulai dengan Input Data
            2. **Analisis**: Gunakan menu Eclat Analysis
            3. **Laporan**: Download hasil di menu Unduh Laporan
            
            **📞 Kontak Support:**
            - Email: support@pharmacy.com
            - Tel: 0800-1234-5678
            """)
        
        # Status
        st.markdown("---")
        st.info(f"🎯 **Halaman Aktif:** {st.session_state.active_page}")
    
    return selected_page if selected_page else st.session_state.active_page


def main():
    st.set_page_config(
        page_title="ECLAT Drug Pattern Analysis",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # st.title("💊 ECLAT Drug Management")
    # st.markdown("---")
    
    # Sidebar navigation
    active_page = create_sidebar()  # Atau gunakan create_sidebar_with_selectbox()
    
    # Log activity
    activity_logger.log_activity(f"Navigated to: {active_page}")
    
    # Page routing
    page_functions = {
        "Manajemen Data Obat": show_manajemen_obat,
        "Unduh Laporan": download_reports_page,
        "Log Aktivitas": activity_logs_page,
        "Input Data Resep Obat": input_data_page,
        "Proses Analisis ECLAT": process_analysis_page,
        "Lihat Hasil Analisis": view_results_page,
        "Lihat Rekomendasi Obat": recommendations_page,
        "Unduh Laporan Eclat": download_reports_page,
    }
    
    # Show current page in main area
    st.title(f"📋 {active_page}")
    st.markdown("---")
    
    # Execute the selected page function
    if active_page in page_functions:
        try:
            page_functions[active_page]()
        except Exception as e:
            st.error(f"❌ Error loading page: {str(e)}")
            st.info("💡 Please try refreshing the page or contact support.")
    else:
        st.error("❌ Halaman tidak ditemukan.")
        st.info("🔍 Silakan pilih menu yang tersedia di sidebar.")

# CSS untuk styling yang lebih baik
def add_custom_css():
    st.markdown("""
    <style>
    /* Custom button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #ddd;
        background-color: #f8f9fa;
        color: #333;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,123,255,0.3);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f1f3f4;
        border-radius: 8px;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        background-color: #fafafa;
        border-radius: 0 0 8px 8px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 8px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

def input_data_page():
    st.header("📊 Input Data Resep Obat")
    st.markdown("Upload file CSV atau Excel yang berisi data resep obat untuk dianalisis.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Pilih file data resep obat:",
        type=['csv', 'xlsx', 'xls'],
        help="File harus berisi kolom untuk ID transaksi dan nama obat"
    )
    
    if uploaded_file is not None:
        try:
            # Process uploaded file
            with st.spinner("Memproses file..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.data = df
                activity_logger.log_activity(f"File uploaded: {uploaded_file.name}")
            
            st.success(f"✅ File berhasil diupload: {uploaded_file.name}")
            
            # Display data preview
            st.subheader("Preview Data")
            st.dataframe(df.head(10))
            
            # Data statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Baris", len(df))
            with col2:
                st.metric("Total Kolom", len(df.columns))
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            
            # Column mapping
            st.subheader("Mapping Kolom")
            st.markdown("Pilih kolom yang sesuai untuk analisis:")
            
            col1, col2 = st.columns(2)
            with col1:
                transaction_col = st.selectbox(
                    "Kolom ID Transaksi:",
                    df.columns.tolist(),
                    help="Kolom yang berisi ID unik untuk setiap transaksi"
                )
            with col2:
                item_col = st.selectbox(
                    "Kolom Nama Obat:",
                    df.columns.tolist(),
                    help="Kolom yang berisi nama obat"
                )
            
            if st.button("Validasi dan Simpan Data"):
                processed_df = data_processor.validate_and_process(df, transaction_col, item_col)
                if processed_df is not None:
                    st.session_state.processed_data = processed_df
                    st.success("✅ Data berhasil divalidasi dan diproses!")
                    activity_logger.log_activity("Data validated and processed successfully")
                    
                    # Show processed data summary
                    st.subheader("Ringkasan Data Terproses")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Unique Transactions", processed_df['transaction_id'].nunique())
                    with col2:
                        st.metric("Unique Items", processed_df['item'].nunique())
                else:
                    st.error("❌ Gagal memproses data. Periksa format dan kolom yang dipilih.")
        
        except Exception as e:
            st.error(f"❌ Error saat memproses file: {str(e)}")
            activity_logger.log_activity(f"Error processing file: {str(e)}")

def process_analysis_page():
    st.header("🔍 Proses Analisis ECLAT")
    
    if st.session_state.processed_data is None:
        st.warning("⚠️ Silakan upload dan proses data terlebih dahulu di halaman 'Input Data Resep Obat'")
        return
    
    st.markdown("Konfigurasi parameter untuk analisis ECLAT:")
    
    # ECLAT parameters
    col1, col2 = st.columns(2)
    with col1:
        min_support = st.slider(
            "Minimum Support (%):",
            min_value=1,
            max_value=50,
            value=5,
            help="Minimum percentage of transactions that must contain an itemset"
        )
    
    with col2:
        min_confidence = st.slider(
            "Minimum Confidence (%):",
            min_value=10,
            max_value=100,
            value=50,
            help="Minimum confidence level for association rules"
        )
    
    max_length = st.slider(
        "Maximum Itemset Length:",
        min_value=2,
        max_value=10,
        value=5,
        help="Maximum number of items in frequent itemsets"
    )
    
    if st.button("🚀 Mulai Analisis ECLAT", type="primary"):
        with st.spinner("Menjalankan algoritma ECLAT... Mohon tunggu..."):
            try:
                # Convert processed data to transaction format
                transactions = data_processor.create_transaction_matrix(st.session_state.processed_data)
                
                # Run ECLAT algorithm
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update progress
                status_text.text("Mencari frequent itemsets...")
                progress_bar.progress(25)
                
                frequent_itemsets = eclat_algorithm.find_frequent_itemsets(
                    transactions, 
                    min_support=min_support/100,
                    max_length=max_length
                )
                
                progress_bar.progress(50)
                status_text.text("Generating association rules...")
                
                # Generate association rules
                association_rules = eclat_algorithm.generate_association_rules(
                    frequent_itemsets,
                    transactions,
                    min_confidence=min_confidence/100
                )
                
                progress_bar.progress(75)
                status_text.text("Menyelesaikan analisis...")
                
                # Store results
                st.session_state.eclat_results = frequent_itemsets
                st.session_state.association_rules = association_rules
                
                progress_bar.progress(100)
                status_text.text("Analisis selesai!")
                
                st.success("✅ Analisis ECLAT berhasil diselesaikan!")
                activity_logger.log_activity(f"ECLAT analysis completed with {len(frequent_itemsets)} frequent itemsets and {len(association_rules)} rules")
                
                # Display quick summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Frequent Itemsets", len(frequent_itemsets))
                with col2:
                    st.metric("Association Rules", len(association_rules))
                with col3:
                    st.metric("Avg Confidence", f"{np.mean([rule['confidence'] for rule in association_rules]):.2%}" if association_rules else "N/A")
                
            except Exception as e:
                st.error(f"❌ Error selama analisis: {str(e)}")
                activity_logger.log_activity(f"ECLAT analysis error: {str(e)}")

def view_results_page():
    st.header("📈 Hasil Analisis")
    
    if st.session_state.eclat_results is None or st.session_state.association_rules is None:
        st.warning("⚠️ Silakan jalankan analisis ECLAT terlebih dahulu.")
        return
    
    tab1, tab2, tab3 = st.tabs(["Frequent Itemsets", "Association Rules", "Visualizations"])
    
    with tab1:
        st.subheader("Frequent Itemsets")
        if st.session_state.eclat_results:
            # Convert to DataFrame for display
            itemsets_data = []
            for itemset, support in st.session_state.eclat_results.items():
                itemsets_data.append({
                    'Itemset': ', '.join(sorted(itemset)),
                    'Size': len(itemset),
                    'Support': f"{support:.3f}",
                    'Support (%)': f"{support*100:.1f}%"
                })
            
            df_itemsets = pd.DataFrame(itemsets_data)
            df_itemsets = df_itemsets.sort_values('Support (%)', ascending=False)
            
            st.dataframe(df_itemsets, use_container_width=True)
            
            # Top itemsets chart
            fig = viz_manager.create_itemsets_chart(df_itemsets.head(10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada frequent itemsets ditemukan.")
    
    with tab2:
        st.subheader("Association Rules")
        if st.session_state.association_rules:
            # Convert to DataFrame
            rules_data = []
            for rule in st.session_state.association_rules:
                rules_data.append({
                    'Antecedent': ', '.join(sorted(rule['antecedent'])),
                    'Consequent': ', '.join(sorted(rule['consequent'])),
                    'Support': f"{rule['support']:.3f}",
                    'Confidence': f"{rule['confidence']:.3f}",
                    'Lift': f"{rule['lift']:.3f}",
                    'Confidence (%)': f"{rule['confidence']*100:.1f}%"
                })
            
            df_rules = pd.DataFrame(rules_data)
            df_rules = df_rules.sort_values('Confidence (%)', ascending=False)
            
            st.dataframe(df_rules, use_container_width=True)
            
            # Rules visualization
            fig = viz_manager.create_rules_scatter(df_rules)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada association rules ditemukan.")
    
    with tab3:
        st.subheader("Visualizations")
        if st.session_state.eclat_results and st.session_state.association_rules:
            
            # Network visualization
            st.subheader("Network Graph")
            network_fig = viz_manager.create_network_graph(st.session_state.association_rules)
            st.plotly_chart(network_fig, use_container_width=True)
            
            # Heatmap
            st.subheader("Association Rules Heatmap")
            heatmap_fig = viz_manager.create_rules_heatmap(st.session_state.association_rules)
            st.plotly_chart(heatmap_fig, use_container_width=True)

def recommendations_page():
    st.header("💡 Rekomendasi Obat")
    
    if st.session_state.association_rules is None:
        st.warning("⚠️ Silakan jalankan analisis ECLAT terlebih dahulu.")
        return
    
    st.markdown("Masukkan obat yang sudah diresepkan untuk mendapatkan rekomendasi:")
    
    # Get all unique items from processed data
    if st.session_state.processed_data is not None:
        all_items = sorted(st.session_state.processed_data['item'].unique().tolist())
        
        selected_items = st.multiselect(
            "Pilih obat yang sudah diresepkan:",
            all_items,
            help="Pilih satu atau lebih obat untuk mendapatkan rekomendasi"
        )
        
        if selected_items:
            recommendations = eclat_algorithm.get_recommendations(
                selected_items,
                st.session_state.association_rules,
                top_n=10
            )
            
            if recommendations:
                st.subheader("🎯 Rekomendasi Obat")
                
                rec_data = []
                for rec in recommendations:
                    rec_data.append({
                        'Recommended Drug': ', '.join(rec['recommended_items']),
                        'Confidence': f"{rec['confidence']:.3f}",
                        'Lift': f"{rec['lift']:.3f}",
                        'Support': f"{rec['support']:.3f}",
                        'Confidence (%)': f"{rec['confidence']*100:.1f}%"
                    })
                
                df_recommendations = pd.DataFrame(rec_data)
                st.dataframe(df_recommendations, use_container_width=True)
                
                # Visualization
                fig = viz_manager.create_recommendations_chart(df_recommendations)
                st.plotly_chart(fig, use_container_width=True)
                
                activity_logger.log_activity(f"Generated recommendations for: {', '.join(selected_items)}")
            else:
                st.info("Tidak ada rekomendasi ditemukan untuk kombinasi obat yang dipilih.")

def download_reports_page():
    st.header("📄 Unduh Laporan")
    
    if st.session_state.eclat_results is None:
        st.warning("⚠️ Silakan jalankan analisis ECLAT terlebih dahulu.")
        return
    
    st.markdown("Pilih jenis laporan yang ingin diunduh:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Unduh Laporan Lengkap (Excel)", type="primary"):
            try:
                excel_buffer = report_generator.generate_excel_report(
                    st.session_state.eclat_results,
                    st.session_state.association_rules,
                    st.session_state.processed_data
                )
                
                st.download_button(
                    label="💾 Download Excel Report",
                    data=excel_buffer,
                    file_name=f"eclat_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                activity_logger.log_activity("Excel report downloaded")
            except Exception as e:
                st.error(f"Error generating Excel report: {str(e)}")
    
    with col2:
        if st.button("📋 Unduh Laporan Ringkas (CSV)"):
            try:
                csv_buffer = report_generator.generate_csv_report(
                    st.session_state.association_rules
                )
                
                st.download_button(
                    label="💾 Download CSV Report",
                    data=csv_buffer,
                    file_name=f"association_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                activity_logger.log_activity("CSV report downloaded")
            except Exception as e:
                st.error(f"Error generating CSV report: {str(e)}")

def activity_logs_page():
    st.header("📋 Log Aktivitas")
    
    logs = activity_logger.get_recent_logs()
    
    if logs:
        st.subheader("Recent Activities")
        
        # Display logs in a nice format
        for log in logs:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            st.text(f"[{timestamp}] {log['activity']}")
        
        # Option to clear logs
        if st.button("🗑️ Clear Logs"):
            activity_logger.clear_logs()
            st.success("Logs cleared successfully!")
            st.rerun()
    else:
        st.info("No activity logs found.")

if __name__ == "__main__":
    main()
