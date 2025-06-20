from collections import defaultdict, Counter
from itertools import combinations
import pandas as pd
import numpy as np

class ECLATAlgorithm:
    """
    Implementation of ECLAT (Equivalence Class Transformation) algorithm
    for frequent itemset mining and association rule generation.
    """
    
    def __init__(self):
        self.frequent_itemsets = {}
        self.item_support = {}
    
    def find_frequent_itemsets(self, transactions, min_support=0.05, max_length=5):
        """
        Find frequent itemsets using ECLAT algorithm.
        
        Args:
            transactions: List of transactions (each transaction is a set of items)
            min_support: Minimum support threshold
            max_length: Maximum length of itemsets to generate
            
        Returns:
            Dictionary of frequent itemsets with their support values
        """
        # Convert transactions to tid-list format
        tid_lists = self._create_tid_lists(transactions)
        
        # Calculate minimum support count
        min_support_count = len(transactions) * min_support
        
        # Find frequent 1-itemsets
        frequent_1_itemsets = {}
        for item, tid_list in tid_lists.items():
            support = len(tid_list) / len(transactions)
            if len(tid_list) >= min_support_count:
                frequent_1_itemsets[frozenset([item])] = support
                self.item_support[item] = support
        
        # Initialize result with frequent 1-itemsets
        self.frequent_itemsets = frequent_1_itemsets.copy()
        
        # Generate frequent k-itemsets iteratively
        current_itemsets = list(frequent_1_itemsets.keys())
        
        for k in range(2, max_length + 1):
            next_itemsets = self._generate_candidates(current_itemsets, k)
            
            if not next_itemsets:
                break
            
            frequent_k_itemsets = {}
            
            for itemset in next_itemsets:
                # Calculate support by intersecting tid-lists
                itemset_list = list(itemset)
                tid_intersection = set(tid_lists[itemset_list[0]])
                
                for item in itemset_list[1:]:
                    tid_intersection = tid_intersection.intersection(set(tid_lists[item]))
                
                support = len(tid_intersection) / len(transactions)
                
                if len(tid_intersection) >= min_support_count:
                    frequent_k_itemsets[itemset] = support
            
            if not frequent_k_itemsets:
                break
            
            self.frequent_itemsets.update(frequent_k_itemsets)
            current_itemsets = list(frequent_k_itemsets.keys())
        
        return self.frequent_itemsets
    
    def _create_tid_lists(self, transactions):
        """Create transaction ID lists for each item."""
        tid_lists = defaultdict(list)
        
        for tid, transaction in enumerate(transactions):
            for item in transaction:
                tid_lists[item].append(tid)
        
        return dict(tid_lists)
    
    def _generate_candidates(self, frequent_itemsets, k):
        """Generate candidate itemsets of length k."""
        candidates = set()
        itemsets_list = list(frequent_itemsets)
        
        for i in range(len(itemsets_list)):
            for j in range(i + 1, len(itemsets_list)):
                # Join two (k-1)-itemsets if they differ by only one item
                itemset1 = set(itemsets_list[i])
                itemset2 = set(itemsets_list[j])
                
                union = itemset1.union(itemset2)
                if len(union) == k:
                    candidates.add(frozenset(union))
        
        return list(candidates)
    
    def generate_association_rules(self, frequent_itemsets, transactions, min_confidence=0.5):
        """
        Generate association rules from frequent itemsets.
        
        Args:
            frequent_itemsets: Dictionary of frequent itemsets
            transactions: List of transactions
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of association rules with metrics
        """
        rules = []
        
        # Only consider itemsets with length >= 2
        for itemset, support in frequent_itemsets.items():
            if len(itemset) < 2:
                continue
            
            itemset_list = list(itemset)
            
            # Generate all possible antecedent-consequent pairs
            for r in range(1, len(itemset_list)):
                for antecedent in combinations(itemset_list, r):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
                    
                    if len(consequent) == 0:
                        continue
                    
                    # Calculate confidence
                    antecedent_support = frequent_itemsets.get(antecedent, 0)
                    if antecedent_support == 0:
                        continue
                    
                    confidence = support / antecedent_support
                    
                    if confidence >= min_confidence:
                        # Calculate lift
                        consequent_support = frequent_itemsets.get(consequent, 0)
                        if consequent_support == 0:
                            # Calculate consequent support from individual items
                            consequent_support = self._calculate_consequent_support(
                                consequent, transactions
                            )
                        
                        lift = confidence / consequent_support if consequent_support > 0 else 0
                        
                        rules.append({
                            'antecedent': set(antecedent),
                            'consequent': set(consequent),
                            'support': support,
                            'confidence': confidence,
                            'lift': lift
                        })
        
        # Sort rules by confidence descending
        rules.sort(key=lambda x: x['confidence'], reverse=True)
        
        return rules
    
    def _calculate_consequent_support(self, consequent, transactions):
        """Calculate support for consequent itemset."""
        count = 0
        for transaction in transactions:
            if consequent.issubset(set(transaction)):
                count += 1
        return count / len(transactions)
    
    def get_recommendations(self, input_items, association_rules, top_n=5):
        """
        Get drug recommendations based on input items and association rules.
        
        Args:
            input_items: List of items already prescribed
            association_rules: List of association rules
            top_n: Number of top recommendations to return
            
        Returns:
            List of recommendations with confidence and lift scores
        """
        recommendations = []
        input_set = set(input_items)
        
        for rule in association_rules:
            antecedent = set(rule['antecedent'])
            consequent = set(rule['consequent'])
            
            # Check if input items match or are subset of antecedent
            if antecedent.issubset(input_set) or input_set.issubset(antecedent):
                # Exclude items already in input
                recommended_items = consequent - input_set
                
                if recommended_items:
                    recommendations.append({
                        'recommended_items': list(recommended_items),
                        'confidence': rule['confidence'],
                        'lift': rule['lift'],
                        'support': rule['support'],
                        'antecedent': list(antecedent)
                    })
        
        # Remove duplicates and sort by confidence
        unique_recommendations = {}
        for rec in recommendations:
            key = frozenset(rec['recommended_items'])
            if key not in unique_recommendations or rec['confidence'] > unique_recommendations[key]['confidence']:
                unique_recommendations[key] = rec
        
        # Sort by confidence and return top N
        sorted_recommendations = sorted(
            unique_recommendations.values(),
            key=lambda x: (x['confidence'], x['lift']),
            reverse=True
        )
        
        return sorted_recommendations[:top_n]
