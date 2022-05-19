
from time import time
from typing import List
from datetime import datetime
from dateutil.relativedelta import *
from functools import reduce


class Transaction():
    price: float
    item_id: int
    timestamp: datetime

    def __init__(self, price:float, item_id:int, timestamp: datetime):
        self.price = price
        self.item_id = item_id
        self.timestamp = timestamp
        
    def __repr__(self):
        return str({'price':self.price, 'item_id': self.item_id, 'timestamp': str(self.timestamp)})

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return self.price == other.price and self.item_id == other.item_id and str(self.timestamp) == str(other.timestamp)
        return False

class IndexValueHistoryItem:
    item_id: int
    price: float
    index_value: float
    Transaction: Transaction

    def __init__(self, price:float, item_id:int, index_value: float, Transaction: Transaction):
        self.price = price
        self.item_id = item_id
        self.index_value = index_value
        self.Transaction = Transaction

    def __repr__(self):
        return str({'price':self.price, 'item_id': self.item_id, 'index_value': self.index_value, 'Transaction': self.Transaction})

    def __eq__(self, other):
        if isinstance(other, IndexValueHistoryItem):
            return self.price == other.price and self.item_id == other.item_id and self.index_value == other.index_value and self.Transaction == other.Transaction
        return False
    

def sort_timestamp(element):
    return element.timestamp.timestamp()

'''
    Given a list of transactions, this returns those transactions sorted in chronological order.
'''
def sort_transactions(transaction_history: List[Transaction]) -> List[Transaction]:
    return sorted(transaction_history, key=sort_timestamp)

'''
    Given a list of transactions, this returns only transactions that have at least
    2 sales in the last year, and at least one sale in the last 6 months.
'''
def filter_valid_transactions(transaction_history: List[Transaction]) -> List[Transaction]:
    now = datetime.now()
    one_year_ago = now + relativedelta(years=-1)
    six_months_ago = now + relativedelta(months=-6)

    inclusion_map: dict() = {}
    for transaction in transaction_history:
        item_id, timestamp = transaction.item_id, transaction.timestamp
        if item_id not in inclusion_map.keys():
            inclusion_map[item_id] = {
                'past_year_sale_count': 0,
                'has_sale_in_last_six_months': False,
                'is_valid': False,
            }
        
        current_map_item = inclusion_map[item_id]
        if current_map_item['is_valid']:
            continue

        # If the transaction did not occur within the last year, it does not affect
        # whether the item is valid or not, so we skip it
        if not timestamp > one_year_ago:
            continue

        past_year_sale_count = current_map_item['past_year_sale_count'] if current_map_item['past_year_sale_count'] else 0
        current_map_item['past_year_sale_count'] = past_year_sale_count + 1

        # If the transaction did not occur within the last six months, since we already
        # incremented the `past_year_sale_count`, we keep going
        if not timestamp > six_months_ago:
            continue

        current_map_item['has_sale_in_last_six_months'] = True

        # If the item has 2 or more sales in the last year, it's valid :-)
        if current_map_item['past_year_sale_count'] >= 2:
            current_map_item['is_valid'] = True

    return [ transaction for transaction in transaction_history if inclusion_map[transaction.item_id]['is_valid'] ]

'''
   Given a list of transactions, this crates a list that contains the index value at the
   time of each transaction, and includes the transaction as well.
   @see {@link https://github.com/Mimicry-Protocol/TAMI/blob/main/reference/card-ladder-white-paper.pdf}
'''
def create_index_value_history(transaction_history: List[Transaction]) -> List[IndexValueHistoryItem]:
    transaction_map = {}

    last_index_value:int = 0
    last_divisor: int = 1

    result = []

    for i in range(0,len(transaction_history)):
        transaction = transaction_history[i]

        is_first_sale = False if transaction.item_id in transaction_map.keys() else True
        
        transaction_map[transaction.item_id] = transaction
        
        item_count = len(transaction_map.keys())

        all_last_sold_value = reduce(lambda x, value: x + value.price, transaction_map.values(),0)
        
        index_value = all_last_sold_value / (item_count * last_divisor)

        if i == 0:
            last_index_value = index_value

            result.append({
                'item_id': transaction.item_id,
                'price': float(transaction.price),
                'index_value': float(index_value),
                'transaction': transaction
            })

            continue

        next_divisor = last_divisor * (index_value / last_index_value)  if is_first_sale else last_divisor

        weighted_index_value = all_last_sold_value / (item_count * next_divisor)

        last_index_value = weighted_index_value
        last_divisor = next_divisor

        result.append({
                'item_id': transaction.item_id,
                'price': float(transaction.price),
                'index_value': float(weighted_index_value),
                'transaction': transaction
            })

    return result


def get_index_value(index_value_history: List[IndexValueHistoryItem]):
    return index_value_history[len(index_value_history)-1]['index_value']


def assign_map(x:dict, y:IndexValueHistoryItem):
    x[y['item_id']] = y
    return x

def get_index_ratios(index_value_history: List[IndexValueHistoryItem]):
    last_sale_map = reduce(assign_map ,index_value_history,{})
    result = []
    for value in last_sale_map.values():
        result.append({
            **value,
            'index_ratio': value['price'] / value['index_value']
        })
    return result

def tami(transaction_history: List[Transaction]):
    sorted_transactions = sort_transactions(transaction_history)
    valid_transactions = filter_valid_transactions(sorted_transactions)
    index_value_history = create_index_value_history(valid_transactions)
    index_value = get_index_value(index_value_history)
    index_ratios = get_index_ratios(index_value_history)
    time_adjusted_values = [element['index_ratio'] * index_value for element in index_ratios]
    time_adjusted_market_index = reduce(lambda acc,value: acc + value, time_adjusted_values, 0)
    return time_adjusted_market_index



