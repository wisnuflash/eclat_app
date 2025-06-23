import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import networkx as nx

class VisualizationManager:
    """
    Handles all visualization tasks for ECLAT analysis results.
    """
    
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_itemsets_chart(self, df_itemsets):
        """
        Create bar chart for frequent itemsets.
        
        Args:
            df_itemsets: DataFrame with itemsets and their support values
            
        Returns:
            Plotly figure object
        """
        # Convert support percentage to numeric for sorting
        df_itemsets['Support_Numeric'] = df_itemsets['Support (%)'].str.rstrip('%').astype(float)
        df_itemsets = df_itemsets.sort_values('Support_Numeric', ascending=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_itemsets['Itemset'],
            x=df_itemsets['Support_Numeric'],
            orientation='h',
            marker_color=self.color_palette[0],
            text=df_itemsets['Support (%)'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Support: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Top Frequent Itemsets by Support',
            xaxis_title='Support (%)',
            yaxis_title='Itemsets',
            height=max(400, len(df_itemsets) * 30),
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_rules_scatter(self, df_rules):
        """
        Create scatter plot for association rules (Support vs Confidence).
        
        Args:
            df_rules: DataFrame with association rules
            
        Returns:
            Plotly figure object
        """
        # Convert string percentages to numeric
        df_rules['Support_Numeric'] = pd.to_numeric(df_rules['Support'])
        df_rules['Confidence_Numeric'] = pd.to_numeric(df_rules['Confidence'])
        df_rules['Lift_Numeric'] = pd.to_numeric(df_rules['Lift'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_rules['Support_Numeric'],
            y=df_rules['Confidence_Numeric'],
            mode='markers',
            marker=dict(
                size=df_rules['Lift_Numeric'] * 5,  # Size based on lift
                color=df_rules['Lift_Numeric'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Lift"),
                line=dict(width=1, color='black')
            ),
            text=df_rules['Antecedent'] + ' → ' + df_rules['Consequent'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Support: %{x:.3f}<br>' +
                         'Confidence: %{y:.3f}<br>' +
                         'Lift: %{marker.color:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Association Rules: Support vs Confidence (Bubble size = Lift)',
            xaxis_title='Support',
            yaxis_title='Confidence',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_network_graph(self, association_rules):
        """
        Create network graph visualization of association rules.
        
        Args:
            association_rules: List of association rules
            
        Returns:
            Plotly figure object
        """
        if not association_rules:
            fig = go.Figure()
            fig.add_annotation(
                text="No association rules to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes and edges
        for rule in association_rules[:20]:  # Limit to top 20 rules for clarity
            antecedent_str = ', '.join(sorted(rule['antecedent']))
            consequent_str = ', '.join(sorted(rule['consequent']))
            
            G.add_node(antecedent_str, node_type='antecedent')
            G.add_node(consequent_str, node_type='consequent')
            G.add_edge(antecedent_str, consequent_str, 
                      weight=rule['confidence'], 
                      lift=rule['lift'])
        
        # Calculate positions
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Extract edges
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Find the corresponding rule for edge info
            for rule in association_rules:
                ant_str = ', '.join(sorted(rule['antecedent']))
                con_str = ', '.join(sorted(rule['consequent']))
                if (edge[0] == ant_str and edge[1] == con_str) or \
                   (edge[1] == ant_str and edge[0] == con_str):
                    edge_info.append(f"Confidence: {rule['confidence']:.3f}")
                    break
        
        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Extract nodes
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            # Color coding: antecedent vs consequent
            if len(node.split(', ')) == 1:
                node_color.append(self.color_palette[0])
            else:
                node_color.append(self.color_palette[1])
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=20,
                color=node_color,
                line=dict(width=2, color='black')
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                        #    title='Association Rules Network Graph',
                        #    titlefont_size=16,
                           title=dict(
                                text='Association Rules Network Graph',
                                font=dict(size=16)
                            ),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="black", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=600
                       ))
        
        return fig
    
    def create_rules_heatmap(self, association_rules):
        """
        Create heatmap visualization for association rules.
        
        Args:
            association_rules: List of association rules
            
        Returns:
            Plotly figure object
        """
        if not association_rules:
            fig = go.Figure()
            fig.add_annotation(
                text="No association rules to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Prepare data for heatmap
        antecedents = []
        consequents = []
        confidences = []
        lifts = []
        
        for rule in association_rules[:15]:  # Limit for readability
            ant_str = ', '.join(sorted(rule['antecedent']))
            con_str = ', '.join(sorted(rule['consequent']))
            antecedents.append(ant_str)
            consequents.append(con_str)
            confidences.append(rule['confidence'])
            lifts.append(rule['lift'])
        
        # Create matrix
        unique_antecedents = list(set(antecedents))
        unique_consequents = list(set(consequents))
        
        confidence_matrix = np.zeros((len(unique_consequents), len(unique_antecedents)))
        lift_matrix = np.zeros((len(unique_consequents), len(unique_antecedents)))
        
        for i, (ant, con, conf, lift) in enumerate(zip(antecedents, consequents, confidences, lifts)):
            ant_idx = unique_antecedents.index(ant)
            con_idx = unique_consequents.index(con)
            confidence_matrix[con_idx, ant_idx] = conf
            lift_matrix[con_idx, ant_idx] = lift
        
        # Create subplot with two heatmaps
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Confidence Heatmap', 'Lift Heatmap'),
            horizontal_spacing=0.15
        )
        
        # Confidence heatmap
        fig.add_trace(
            go.Heatmap(
                z=confidence_matrix,
                x=unique_antecedents,
                y=unique_consequents,
                colorscale='Blues',
                name='Confidence',
                showscale=True,
                colorbar=dict(x=0.45, title="Confidence")
            ),
            row=1, col=1
        )
        
        # Lift heatmap
        fig.add_trace(
            go.Heatmap(
                z=lift_matrix,
                x=unique_antecedents,
                y=unique_consequents,
                colorscale='Reds',
                name='Lift',
                showscale=True,
                colorbar=dict(x=1.02, title="Lift")
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Association Rules Heatmaps',
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Antecedent", row=1, col=1)
        fig.update_xaxes(title_text="Antecedent", row=1, col=2)
        fig.update_yaxes(title_text="Consequent", row=1, col=1)
        fig.update_yaxes(title_text="Consequent", row=1, col=2)
        
        return fig
    
    def create_recommendations_chart(self, df_recommendations):
        """
        Create chart for drug recommendations.
        
        Args:
            df_recommendations: DataFrame with recommendations
            
        Returns:
            Plotly figure object
        """
        # Convert confidence percentage to numeric
        df_recommendations['Confidence_Numeric'] = df_recommendations['Confidence (%)'].str.rstrip('%').astype(float)
        df_recommendations = df_recommendations.sort_values('Confidence_Numeric', ascending=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_recommendations['Recommended Drug'],
            x=df_recommendations['Confidence_Numeric'],
            orientation='h',
            marker_color=self.color_palette[2],
            text=df_recommendations['Confidence (%)'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Confidence: %{text}<br>Lift: %{customdata}<extra></extra>',
            customdata=df_recommendations['Lift']
        ))
        
        fig.update_layout(
            title='Drug Recommendations by Confidence',
            xaxis_title='Confidence (%)',
            yaxis_title='Recommended Drugs',
            height=max(400, len(df_recommendations) * 40),
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_data_overview_charts(self, df):
        """
        Create overview charts for the input data.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Tuple of Plotly figure objects
        """
        # Item frequency chart
        item_counts = df['item'].value_counts().head(15)
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=item_counts.values,
            y=item_counts.index,
            orientation='h',
            marker_color=self.color_palette[0]
        ))
        fig1.update_layout(
            title='Top 15 Most Frequent Items',
            xaxis_title='Frequency',
            yaxis_title='Items',
            height=500
        )
        
        # Transaction size distribution
        transaction_sizes = df.groupby('transaction_id').size()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=transaction_sizes,
            nbinsx=20,
            marker_color=self.color_palette[1]
        ))
        fig2.update_layout(
            title='Distribution of Transaction Sizes',
            xaxis_title='Number of Items per Transaction',
            yaxis_title='Frequency',
            height=400
        )
        
        return fig1, fig2
