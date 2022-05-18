import pytest
from tami import *
from datetime import datetime
from dateutil.relativedelta import *

now = datetime.now()
yesterday = now + relativedelta(days=-1)
twoDaysAgo = now + relativedelta(days=-2)
threeDaysAgo = now + relativedelta(days=-3)
oneMonthAgo = now + relativedelta(months=-1)
sixWeeksAgo = now + relativedelta(weeks=-6)
twoYearsAgo = now + relativedelta(years=-2)

mockTransactionHistory = [
  # Lavender should be excluded since she did not have two transactions in the past year
  Transaction(price=500, item_id='Lavender', timestamp=threeDaysAgo),
  Transaction(price=700, item_id='Hyacinth', timestamp=oneMonthAgo),
  Transaction(price=1200, item_id='Mars', timestamp=twoDaysAgo),
  # Nyx should be excluded since she did not have two transactions in the past year
  Transaction(price=612, item_id='Nyx', timestamp=twoYearsAgo),
  Transaction(price=400, item_id='Hyacinth', timestamp=threeDaysAgo),
  Transaction(price=1200, item_id='Nyx', timestamp=yesterday),
  Transaction(price=612, item_id='Mars', timestamp=sixWeeksAgo),
];

expected_values = {
  'sorted_transactions': [
    Transaction(price=612, item_id='Nyx', timestamp=twoYearsAgo),
    Transaction(price=612, item_id='Mars', timestamp=sixWeeksAgo),
    Transaction(price=700, item_id='Hyacinth', timestamp=oneMonthAgo),
    Transaction(price=500, item_id='Lavender', timestamp=threeDaysAgo),
    Transaction(price=400, item_id='Hyacinth', timestamp=threeDaysAgo),
    Transaction(price=1200, item_id='Mars', timestamp=twoDaysAgo),
    Transaction(price=1200, item_id='Nyx', timestamp=yesterday),
  ],
  'valid_transactions': [
    Transaction(price=612, item_id='Mars', timestamp=sixWeeksAgo),
    Transaction(price=700, item_id='Hyacinth', timestamp=oneMonthAgo),
    Transaction(price=400, item_id='Hyacinth', timestamp=threeDaysAgo),
    Transaction(price=1200, item_id='Mars', timestamp=twoDaysAgo),
  ],
  'index_value_history': [
    {
      'item_id': 'Mars',
      'price': 612,
      'index_value': 612,
      'transaction': Transaction(price=612, item_id='Mars', timestamp=sixWeeksAgo),
    },
    {
      'item_id': 'Hyacinth',
      'price': 700,
      'index_value': 612,
      'transaction': Transaction(price=700, item_id='Hyacinth', timestamp=oneMonthAgo),
    },
    {
      'item_id': 'Hyacinth',
      'price': 400,
      'index_value': 472.0609756097561,
      'transaction': Transaction(price=400, item_id='Hyacinth', timestamp=threeDaysAgo),
    },
    {
      'item_id': 'Mars',
      'price': 1200,
      'index_value': 746.3414634146342,
      'transaction': Transaction(price=1200, item_id='Mars', timestamp=twoDaysAgo),
    },
  ],
  'index_value': 746.3414634146342,
  'index_ratios': [
    {
      'item_id': 'Mars',
      'price': 1200,
      'index_value': 746.3414634146342,
      'transaction': Transaction(price=1200, item_id='Mars', timestamp=twoDaysAgo),
      'index_ratio': 1.6078431372549018,
    },
    {
      'item_id': 'Hyacinth',
      'price': 400,
      'index_value': 472.0609756097561,
      'transaction': Transaction(price=400, item_id='Hyacinth', timestamp=threeDaysAgo),
      'index_ratio': 0.847348161926167,
    },
  ],
  'time_adjusted_values': [1200, 632.4110671936759],
  'time_adjusted_market_index': 1832.411067193676,
}

sorted_transactions = sort_transactions(mockTransactionHistory)
valid_transactions = filter_valid_transactions(sorted_transactions)

def test_create_index_value_history():
    index_value_history = create_index_value_history(valid_transactions)
    assert index_value_history == expected_values['index_value_history']

def test_get_index_ratios():
    index_value_history = create_index_value_history(valid_transactions)
    index_ratios = get_index_ratios(index_value_history)
    assert index_ratios == expected_values['index_ratios']
    
def test_get_index_value():
    index_value_history = create_index_value_history(valid_transactions)
    index_value = get_index_value(index_value_history)
    assert index_value == expected_values['index_value']
    
def test_tami():
    value = tami(valid_transactions)
    assert value == expected_values['time_adjusted_market_index']
