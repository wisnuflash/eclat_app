import pandas as pd
import numpy as np
from collections import defaultdict
import streamlit as st

class DataProcessor:
    """
    Handles data validation, cleaning, and transformation for ECLAT analysis.
    """
    
    def __init__(self):
        self.processed_data = None
        self.transaction_matrix = None
    
    def validate_and_process(self, df, transaction_col, item_col):
        """
        Validate and process the uploaded data.
        
        Args:
            df: Input DataFrame
            transaction_col: Column name for transaction IDs
            item_col: Column name for items/drugs
            
        Returns:
            Processed DataFrame or None if validation fails
        """
        try:
            # Check if required columns exist
            if transaction_col not in df.columns:
                st.error(f"Column '{transaction_col}' not found in data")
                return None
            
            if item_col not in df.columns:
                st.error(f"Column '{item_col}' not found in data")
                return None
            
            # Create a copy for processing
            processed_df = df[[transaction_col, item_col]].copy()
            processed_df.columns = ['transaction_id', 'item']
            
            # Remove null values
            processed_df = processed_df.dropna()
            
            # Convert to string and clean
            processed_df['transaction_id'] = processed_df['transaction_id'].astype(str).str.strip()
            processed_df['item'] = processed_df['item'].astype(str).str.strip()
            
            # Remove empty strings
            processed_df = processed_df[
                (processed_df['transaction_id'] != '') & 
                (processed_df['item'] != '')
            ]
            
            # Validate minimum requirements
            if len(processed_df) < 10:
                st.error("Data terlalu sedikit. Minimal 10 baris data diperlukan.")
                return None
            
            if processed_df['transaction_id'].nunique() < 5:
                st.error("Terlalu sedikit transaksi unik. Minimal 5 transaksi diperlukan.")
                return None
            
            if processed_df['item'].nunique() < 3:
                st.error("Terlalu sedikit item unik. Minimal 3 item berbeda diperlukan.")
                return None
            
            # Remove duplicate transaction-item pairs
            processed_df = processed_df.drop_duplicates()
            
            # Additional cleaning
            processed_df = self._clean_item_names(processed_df)
            
            self.processed_data = processed_df
            return processed_df
            
        except Exception as e:
            st.error(f"Error during data processing: {str(e)}")
            return None
    
    def _clean_item_names(self, df):
        """Clean and standardize item names."""
        # Convert to title case and remove extra spaces
        df['item'] = df['item'].str.title().str.replace(r'\s+', ' ', regex=True)
        
        # Remove common prefixes/suffixes that might cause duplicates
        df['item'] = df['item'].str.replace(r'^(Obat|Drug|Medicine)\s+', '', regex=True, case=False)
        df['item'] = df['item'].str.replace(r'\s+(Tablet|Capsule|Syrup|mg|ml)$', '', regex=True, case=False)
        
        return df
    
    def create_transaction_matrix(self, df):
        """
        Convert processed data to transaction matrix format for ECLAT.
        
        Args:
            df: Processed DataFrame with transaction_id and item columns
            
        Returns:
            List of transactions (each transaction is a set of items)
        """
        if df is None:
            return []
        
        # Group by transaction_id and create sets of items
        transactions = []
        transaction_groups = df.groupby('transaction_id')['item'].apply(set).reset_index()
        
        for _, row in transaction_groups.iterrows():
            transactions.append(row['item'])
        
        self.transaction_matrix = transactions
        return transactions
    
    def get_data_summary(self, df):
        """
        Generate summary statistics for the data.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        if df is None:
            return {}
        
        # Basic statistics
        total_transactions = df['transaction_id'].nunique()
        total_items = df['item'].nunique()
        total_records = len(df)
        
        # Transaction size statistics
        transaction_sizes = df.groupby('transaction_id').size()
        avg_items_per_transaction = transaction_sizes.mean()
        min_items_per_transaction = transaction_sizes.min()
        max_items_per_transaction = transaction_sizes.max()
        
        # Item frequency statistics
        item_frequencies = df['item'].value_counts()
        most_common_item = item_frequencies.index[0] if len(item_frequencies) > 0 else "N/A"
        most_common_item_count = item_frequencies.iloc[0] if len(item_frequencies) > 0 else 0
        
        return {
            'total_transactions': total_transactions,
            'total_items': total_items,
            'total_records': total_records,
            'avg_items_per_transaction': round(avg_items_per_transaction, 2),
            'min_items_per_transaction': min_items_per_transaction,
            'max_items_per_transaction': max_items_per_transaction,
            'most_common_item': most_common_item,
            'most_common_item_count': most_common_item_count,
            'item_frequencies': item_frequencies.to_dict()
        }
    
    def detect_data_quality_issues(self, df):
        """
        Detect potential data quality issues.
        
        Args:
            df: Input DataFrame
            
        Returns:
            List of detected issues
        """
        issues = []
        
        if df is None:
            return ["No data provided"]
        
        # Check for very short item names
        short_items = df[df['item'].str.len() < 3]['item'].unique()
        if len(short_items) > 0:
            issues.append(f"Found {len(short_items)} items with very short names (< 3 characters)")
        
        # Check for transactions with only one item
        single_item_transactions = df.groupby('transaction_id').size()
        single_item_count = (single_item_transactions == 1).sum()
        if single_item_count > 0:
            issues.append(f"Found {single_item_count} transactions with only one item")
        
        # Check for very frequent items (might indicate data quality issues)
        item_freq = df['item'].value_counts()
        total_transactions = df['transaction_id'].nunique()
        very_frequent_items = item_freq[item_freq / total_transactions > 0.8]
        if len(very_frequent_items) > 0:
            issues.append(f"Found {len(very_frequent_items)} items that appear in >80% of transactions")
        
        # Check for duplicate transaction-item pairs in original data
        duplicates = df.duplicated(subset=['transaction_id', 'item']).sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate transaction-item pairs")
        
        return issues
    
    def suggest_parameters(self, df):
        """
        Suggest appropriate parameters for ECLAT based on data characteristics.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary with suggested parameters
        """
        if df is None:
            return {}
        
        total_transactions = df['transaction_id'].nunique()
        total_items = df['item'].nunique()
        
        # Suggest minimum support based on data size
        if total_transactions < 100:
            suggested_min_support = 0.1  # 10%
        elif total_transactions < 1000:
            suggested_min_support = 0.05  # 5%
        else:
            suggested_min_support = 0.02  # 2%
        
        # Suggest minimum confidence
        suggested_min_confidence = 0.5  # 50%
        
        # Suggest maximum itemset length
        avg_transaction_size = df.groupby('transaction_id').size().mean()
        suggested_max_length = min(int(avg_transaction_size * 0.7), 8)
        
        return {
            'min_support': suggested_min_support,
            'min_confidence': suggested_min_confidence,
            'max_length': max(2, suggested_max_length)
        }
