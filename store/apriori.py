from collections import defaultdict
from itertools import combinations

def apriori(transactions, min_support=0.5):
    """
    Apriori algorithm to find frequent itemsets.
    transactions: list of lists, each inner list is a transaction of product IDs
    min_support: minimum support threshold (0 to 1)
    Returns: dict of frequent itemsets with their support counts
    """
    itemset_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            itemset_counts[frozenset([item])] += 1

    num_transactions = len(transactions)
    frequent_itemsets = {k: v for k, v in itemset_counts.items() if v / num_transactions >= min_support}

    k = 2
    current_frequent_itemsets = set(frequent_itemsets.keys())

    while current_frequent_itemsets:
        candidate_itemsets = set()
        current_frequent_list = list(current_frequent_itemsets)
        for i in range(len(current_frequent_list)):
            for j in range(i + 1, len(current_frequent_list)):
                union_set = current_frequent_list[i] | current_frequent_list[j]
                if len(union_set) == k:
                    candidate_itemsets.add(union_set)

        itemset_counts = defaultdict(int)
        for transaction in transactions:
            transaction_set = set(transaction)
            for candidate in candidate_itemsets:
                if candidate.issubset(transaction_set):
                    itemset_counts[candidate] += 1

        current_frequent_itemsets = set()
        for itemset, count in itemset_counts.items():
            if count / num_transactions >= min_support:
                frequent_itemsets[itemset] = count
                current_frequent_itemsets.add(itemset)

        k += 1

    return frequent_itemsets

def generate_association_rules(frequent_itemsets, min_confidence=0.7):
    """
    Generate association rules from frequent itemsets.
    frequent_itemsets: dict of itemsets with support counts
    min_confidence: minimum confidence threshold (0 to 1)
    Returns: list of tuples (antecedent, consequent, confidence)
    """
    rules = []
    num_transactions = None
    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue
        for i in range(1, len(itemset)):
            for antecedent in combinations(itemset, i):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent
                if antecedent in frequent_itemsets and itemset in frequent_itemsets:
                    support_itemset = frequent_itemsets[itemset]
                    support_antecedent = frequent_itemsets[antecedent]
                    confidence = support_itemset / support_antecedent
                    if confidence >= min_confidence:
                        rules.append((antecedent, consequent, confidence))
    return rules
