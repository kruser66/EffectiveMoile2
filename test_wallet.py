import os
import pytest
from wallet import Wallet, Income, Expense, Transaction


@pytest.fixture
def wallet(request):
    wallet = Wallet('test_transactions.json')
    yield wallet
    if os.path.exists('test_transactions.json'):
        os.remove('test_transactions.json')


def test_add_transaction(wallet):
    income = Income(date='2022-01-01', amount=1000, description='Test income')
    wallet.add_transaction(income)
    assert len(wallet.transactions) == 1
    assert wallet.transactions[0].amount == 1000


def test_edit_transaction(wallet):
    income = Income(date='2022-01-01', amount=1000, description='Test income')
    wallet.add_transaction(income)
    wallet.edit_transaction(0, amount=2000)
    assert wallet.transactions[0].amount == 2000


def test_search_transactions(wallet):
    income = Income(date='2022-01-01', amount=1000, description='Test income')
    expense = Expense(date='2022-01-02', amount=500, description='Test expense')
    wallet.add_transaction(income)
    wallet.add_transaction(expense)
    results = wallet.search_transactions('Test')
    assert len(results) == 2


def test_display_balance(wallet, capsys):
    income = Income(date='2022-01-01', amount=1000, description='Test income')
    expense = Expense(date='2022-01-02', amount=500, description='Test expense')
    wallet.add_transaction(income)
    wallet.add_transaction(expense)
    wallet.display_balance()
    captured = capsys.readouterr()
    assert 'Баланс: 500' in captured.out
    assert 'Доходы: 1000' in captured.out
    assert 'Расходы: 500' in captured.out


def test_save_and_load_transactions(wallet):
    income = Income(date='2022-01-01', amount=1000, description='Test income')
    wallet.add_transaction(income)
    wallet.save_transactions()
    loaded_wallet = Wallet('test_transactions.json')
    assert len(loaded_wallet.transactions) == 1
    assert loaded_wallet.transactions[0].amount == 1000


def test_transaction_validation():
    with pytest.raises(ValueError):
        Transaction(date='2022/01/01', category='Доход', amount=1000, description='Test income')
    with pytest.raises(ValueError):
        Transaction(date='2022-01-01', category='Invalid', amount=1000, description='Test income')
    with pytest.raises(ValueError):
        Transaction(date='2022-01-01', category='Расход', amount='not a number', description='Test income')
