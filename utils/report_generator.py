import pandas as pd
import io
from datetime import datetime
import xlsxwriter

class ReportGenerator:
    """
    Generates various types of reports from ECLAT analysis results.
    """
    
    def __init__(self):
        pass
    
    def generate_excel_report(self, frequent_itemsets, association_rules, processed_data):
        """
        Generate comprehensive Excel report with multiple sheets.
        
        Args:
            frequent_itemsets: Dictionary of frequent itemsets
            association_rules: List of association rules
            processed_data: Original processed DataFrame
            
        Returns:
            BytesIO buffer containing Excel file
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Summary sheet
            self._create_summary_sheet(writer, frequent_itemsets, association_rules, processed_data)
            
            # Frequent itemsets sheet
            self._create_itemsets_sheet(writer, frequent_itemsets)
            
            # Association rules sheet
            self._create_rules_sheet(writer, association_rules)
            
            # Data overview sheet
            self._create_data_overview_sheet(writer, processed_data)
        
        output.seek(0)
        return output.getvalue()
    
    def _create_summary_sheet(self, writer, frequent_itemsets, association_rules, processed_data):
        """Create summary sheet with key metrics."""
        workbook = writer.book
        worksheet = workbook.add_worksheet('Summary')
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        
        # Metric format
        metric_format = workbook.add_format({
            'bold': True,
            'font_size': 12
        })
        
        # Title
        worksheet.write('A1', 'ECLAT Analysis Summary Report', header_format)
        worksheet.write('A2', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Data metrics
        row = 4
        worksheet.write(f'A{row}', 'Data Metrics:', metric_format)
        row += 1
        
        if processed_data is not None:
            worksheet.write(f'A{row}', 'Total Transactions:')
            worksheet.write(f'B{row}', processed_data['transaction_id'].nunique())
            row += 1
            
            worksheet.write(f'A{row}', 'Total Unique Items:')
            worksheet.write(f'B{row}', processed_data['item'].nunique())
            row += 1
            
            worksheet.write(f'A{row}', 'Total Records:')
            worksheet.write(f'B{row}', len(processed_data))
            row += 1
            
            avg_items = processed_data.groupby('transaction_id').size().mean()
            worksheet.write(f'A{row}', 'Average Items per Transaction:')
            worksheet.write(f'B{row}', round(avg_items, 2))
            row += 2
        
        # Analysis results
        worksheet.write(f'A{row}', 'Analysis Results:', metric_format)
        row += 1
        
        worksheet.write(f'A{row}', 'Frequent Itemsets Found:')
        worksheet.write(f'B{row}', len(frequent_itemsets) if frequent_itemsets else 0)
        row += 1
        
        worksheet.write(f'A{row}', 'Association Rules Generated:')
        worksheet.write(f'B{row}', len(association_rules) if association_rules else 0)
        row += 1
        
        if association_rules:
            avg_confidence = sum(rule['confidence'] for rule in association_rules) / len(association_rules)
            worksheet.write(f'A{row}', 'Average Confidence:')
            worksheet.write(f'B{row}', f'{avg_confidence:.3f}')
            row += 1
            
            avg_lift = sum(rule['lift'] for rule in association_rules) / len(association_rules)
            worksheet.write(f'A{row}', 'Average Lift:')
            worksheet.write(f'B{row}', f'{avg_lift:.3f}')
        
        # Auto-adjust column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
    
    def _create_itemsets_sheet(self, writer, frequent_itemsets):
        """Create frequent itemsets sheet."""
        if not frequent_itemsets:
            return
        
        # Convert to DataFrame
        itemsets_data = []
        for itemset, support in frequent_itemsets.items():
            itemsets_data.append({
                'Itemset': ', '.join(sorted(itemset)),
                'Size': len(itemset),
                'Support': support,
                'Support (%)': f'{support*100:.2f}%'
            })
        
        df_itemsets = pd.DataFrame(itemsets_data)
        df_itemsets = df_itemsets.sort_values('Support', ascending=False)
        
        # Write to Excel
        df_itemsets.to_excel(writer, sheet_name='Frequent Itemsets', index=False)
        
        # Format the sheet
        workbook = writer.book
        worksheet = writer.sheets['Frequent Itemsets']
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        
        # Apply header format
        for col_num, value in enumerate(df_itemsets.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
    
    def _create_rules_sheet(self, writer, association_rules):
        """Create association rules sheet."""
        if not association_rules:
            return
        
        # Convert to DataFrame
        rules_data = []
        for rule in association_rules:
            rules_data.append({
                'Antecedent': ', '.join(sorted(rule['antecedent'])),
                'Consequent': ', '.join(sorted(rule['consequent'])),
                'Support': f'{rule["support"]:.4f}',
                'Confidence': f'{rule["confidence"]:.4f}',
                'Lift': f'{rule["lift"]:.4f}',
                'Support (%)': f'{rule["support"]*100:.2f}%',
                'Confidence (%)': f'{rule["confidence"]*100:.2f}%'
            })
        
        df_rules = pd.DataFrame(rules_data)
        
        # Write to Excel
        df_rules.to_excel(writer, sheet_name='Association Rules', index=False)
        
        # Format the sheet
        workbook = writer.book
        worksheet = writer.sheets['Association Rules']
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        
        # Apply header format
        for col_num, value in enumerate(df_rules.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df_rules.columns):
            max_length = max(df_rules[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_length + 2, 50))
    
    def _create_data_overview_sheet(self, writer, processed_data):
        """Create data overview sheet."""
        if processed_data is None:
            return
        
        workbook = writer.book
        worksheet = workbook.add_worksheet('Data Overview')
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        
        # Item frequency analysis
        worksheet.write('A1', 'Top 20 Most Frequent Items', header_format)
        
        item_freq = processed_data['item'].value_counts().head(20)
        
        worksheet.write('A3', 'Item', header_format)
        worksheet.write('B3', 'Frequency', header_format)
        
        for i, (item, freq) in enumerate(item_freq.items(), start=4):
            worksheet.write(f'A{i}', item)
            worksheet.write(f'B{i}', freq)
        
        # Transaction size analysis
        worksheet.write('D1', 'Transaction Size Distribution', header_format)
        
        transaction_sizes = processed_data.groupby('transaction_id').size()
        size_dist = transaction_sizes.value_counts().sort_index()
        
        worksheet.write('D3', 'Transaction Size', header_format)
        worksheet.write('E3', 'Count', header_format)
        
        for i, (size, count) in enumerate(size_dist.items(), start=4):
            worksheet.write(f'D{i}', size)
            worksheet.write(f'E{i}', count)
        
        # Auto-adjust column widths
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 12)
    
    def generate_csv_report(self, association_rules):
        """
        Generate CSV report for association rules.
        
        Args:
            association_rules: List of association rules
            
        Returns:
            CSV string
        """
        if not association_rules:
            return "No association rules found."
        
        # Convert to DataFrame
        rules_data = []
        for rule in association_rules:
            rules_data.append({
                'Antecedent': ', '.join(sorted(rule['antecedent'])),
                'Consequent': ', '.join(sorted(rule['consequent'])),
                'Support': rule['support'],
                'Confidence': rule['confidence'],
                'Lift': rule['lift']
            })
        
        df_rules = pd.DataFrame(rules_data)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df_rules.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()
    
    def generate_text_summary(self, frequent_itemsets, association_rules, processed_data):
        """
        Generate plain text summary report.
        
        Args:
            frequent_itemsets: Dictionary of frequent itemsets
            association_rules: List of association rules
            processed_data: Original processed DataFrame
            
        Returns:
            String containing text report
        """
        report = []
        report.append("ECLAT ANALYSIS SUMMARY REPORT")
        report.append("=" * 40)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Data overview
        if processed_data is not None:
            report.append("DATA OVERVIEW:")
            report.append(f"- Total Transactions: {processed_data['transaction_id'].nunique()}")
            report.append(f"- Total Unique Items: {processed_data['item'].nunique()}")
            report.append(f"- Total Records: {len(processed_data)}")
            
            avg_items = processed_data.groupby('transaction_id').size().mean()
            report.append(f"- Average Items per Transaction: {avg_items:.2f}")
            report.append("")
        
        # Analysis results
        report.append("ANALYSIS RESULTS:")
        report.append(f"- Frequent Itemsets Found: {len(frequent_itemsets) if frequent_itemsets else 0}")
        report.append(f"- Association Rules Generated: {len(association_rules) if association_rules else 0}")
        
        if association_rules:
            avg_confidence = sum(rule['confidence'] for rule in association_rules) / len(association_rules)
            avg_lift = sum(rule['lift'] for rule in association_rules) / len(association_rules)
            report.append(f"- Average Confidence: {avg_confidence:.3f}")
            report.append(f"- Average Lift: {avg_lift:.3f}")
        
        report.append("")
        
        # Top association rules
        if association_rules:
            report.append("TOP 10 ASSOCIATION RULES:")
            report.append("-" * 30)
            
            for i, rule in enumerate(association_rules[:10], 1):
                antecedent = ', '.join(sorted(rule['antecedent']))
                consequent = ', '.join(sorted(rule['consequent']))
                report.append(f"{i}. {antecedent} → {consequent}")
                report.append(f"   Support: {rule['support']:.3f}, "
                            f"Confidence: {rule['confidence']:.3f}, "
                            f"Lift: {rule['lift']:.3f}")
                report.append("")
        
        return '\n'.join(report)
