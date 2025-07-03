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
from utils.database import fetch_stock_data, add_stock_obat, update_stock_obat, delete_stock_obat
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
db_setup = SQLAlchemySetup()
# Initialize database connection
if not db_setup.init_database():
    st.error("❌ Gagal menginisialisasi database. Periksa konfigurasi dan coba lagi.")
# Check if database setup is successful
if not db_setup.execute_sql_file():
    st.error("❌ Gagal menjalankan file SQL untuk setup database. Periksa file dan coba lagi.")

# Main function to run the Streamlit app
def main():
    st.set_page_config(
        page_title="ECLAT Drug Pattern Analysis",
        page_icon="💊",
        layout="wide",
        # initial_sidebar_state="expanded"
    )
    
    st.title("💊 ECLAT Drug")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "List Halaman Eclat Analysis:",
        ["Manajemen Data Obat", "Input Data Resep Obat", "Proses Analisis ECLAT", "Lihat Hasil Analisis", 
         "Lihat Rekomendasi Obat", "Unduh Laporan", "Log Aktivitas"]
    )
    
    # Log page navigation
    activity_logger.log_activity(f"Navigated to: {page}")
    
    pages = {
        "Manajemen Data Obat": show_manajemen_obat,
        "Input Data Resep Obat": input_data_page,
        "Proses Analisis ECLAT": process_analysis_page,
        "Lihat Hasil Analisis": view_results_page,
        "Lihat Rekomendasi Obat": recommendations_page,
        "Unduh Laporan": download_reports_page,
        "Log Aktivitas": activity_logs_page,
    }

    # Eksekusi fungsi berdasarkan pilihan user
    if page in pages:
        pages[page]()
    else:
        st.error("Halaman tidak ditemukan.")



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
