from datetime import datetime
from typing import List, Literal, Union, Optional
from pydantic import BaseModel, Field, field_validator
import json


class Transaction(BaseModel):
    date: str = Field(..., description="Дата транзакции в формате YYYY-MM-DD")
    category: Literal['Доход', 'Расход'] = Field(..., description="Категория транзакции: 'Доход' или 'Расход'")
    amount: int = Field(..., description="Сумма транзакции")
    description: str = Field(..., description="Описание транзакции")

    @field_validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Неверный формат даты. Используйте формат YYYY-MM-DD.')


class Income(Transaction):
    category: Literal['Доход'] = Field('Доход')


class Expense(Transaction):
    category: Literal['Расход'] = Field('Расход')


class Wallet:
    def __init__(self, filename: str):
        self.filename = filename
        self.transactions: List[Union[Income, Expense]] = self.load_transactions()

    def load_transactions(self) -> List[Union[Income, Expense]]:
        try:
            with open(self.filename, 'r') as file:
                transactions_data = json.load(file)
                return [
                    Income(**data) if data['category'] == 'Доход' else Expense(**data) for data in transactions_data
                ]
        except FileNotFoundError:
            return []

    def save_transactions(self):
        with open(self.filename, 'w') as file:
            json.dump([t.model_dump() for t in self.transactions], file, indent=4, default=str)

    def add_transaction(self, transaction: Union[Income, Expense]):
        self.transactions.append(transaction)
        self.save_transactions()

    def edit_transaction(self, index: int, **kwargs):
        transaction = self.transactions[index]
        for key, value in kwargs.items():
            if value is not None:
                setattr(transaction, key, value)
        self.save_transactions()

    def search_transactions(self, query: str) -> List[Union[Income, Expense]]:
        return [(index, t) for index, t in enumerate(self.transactions) if query in str(t.model_dump().values())]

    def display_transactions(self):
        for index, transaction in enumerate(self.transactions):
            print(f"Индекс: {index}, Транзакция: {transaction.model_dump()}")

    def display_balance(self):
        incomes = sum(t.amount for t in self.transactions if isinstance(t, Income))
        expenses = sum(t.amount for t in self.transactions if isinstance(t, Expense))
        balance = incomes - expenses
        print(f"Баланс: {balance}")
        print(f"Доходы: {incomes}")
        print(f"Расходы: {expenses}")


def input_transaction_data(transaction: Optional[Transaction] = None) -> dict:
    data = {}
    if transaction:
        for field in transaction.model_fields:
            if field != 'category':  # Пропускаем поле категории
                value = input(
                    f"Введите новое значение для {field} \
                        или оставьте пустым, чтобы не менять ({getattr(transaction, field)}): "
                )
                if value:
                    data[field] = value
        data['category'] = transaction.category
    else:
        data['date'] = input_date("Введите дату (YYYY-MM-DD): ")
        data['amount'] = input_amount("Введите сумму: ")
        data['description'] = input("Введите описание: ")
    return data


def input_date(prompt: str) -> str:
    while True:
        date_input = input(prompt)
        try:
            datetime.strptime(date_input, '%Y-%m-%d')
            return date_input
        except ValueError:
            print('Неверный формат даты. Используйте формат YYYY-MM-DD.')


def input_amount(prompt: str) -> int:
    while True:
        amount_input = input(prompt)
        try:
            return int(amount_input)
        except ValueError:
            print('Неверный формат суммы. Введите число.')


def main():
    wallet = Wallet('transactions.json')

    while True:
        print("\n1. Вывод транзакций")
        print("2. Добавление дохода")
        print("3. Добавление расхода")
        print("4. Редактирование записи")
        print("5. Поиск по записям")
        print("6. Вывод баланса")
        print("7. Выход")

        choice = input("Выберите действие: ")

        try:
            match choice:
                case '1':
                    wallet.display_transactions()
                case '2':
                    data = input_transaction_data()
                    income = Income(**data)
                    wallet.add_transaction(income)
                case '3':
                    data = input_transaction_data()
                    expense = Expense(**data)
                    wallet.add_transaction(expense)
                case '4':
                    index = int(input("Введите индекс записи для редактирования: "))
                    transaction = wallet.transactions[index]
                    data = input_transaction_data(transaction)
                    wallet.edit_transaction(index, **data)
                case '5':
                    query = input("Введите поисковый запрос: ")
                    transactions = wallet.search_transactions(query)
                    for index, record in transactions:
                        print(f"Индекс: {index}, Транзакция: {record.model_dump()}")
                case '6':
                    wallet.display_balance()
                case '7':
                    break
                case _:
                    print("Некорректный ввод, попробуйте еще раз.")
        except ValueError as e:
            print(e)
        except IndexError:
            print("Транзакция с таким индексом не найдена.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
