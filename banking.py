from random import randint, sample
import sqlite3
import os.path

cards = []
IIN_BANKING = 400000
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute(
"""
SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='card'
"""
)
if cur.fetchone()[0] == 1:
    print('Table exists')
else:
    cur.execute('CREATE TABLE card('
            '   id INTEGER,'
            '   number TEXT,'
            '   pin TEXT,'
            '   balance INTEGER DEFAULT 0'
            ');')
    conn.commit()
# cur.execute('DROP TABLE card;')
# conn.commit()
# cur.execute('CREATE TABLE card('
#             '   id INTEGER,'
#             '   number TEXT,'
#             '   pin TEXT,'
#             '   balance INTEGER DEFAULT 0'
#             ');')
# conn.commit()


class Banking:

    def __init__(self):
        self.card_number = Banking.generate_card_number()
        self.pin = "".join(str(n) for n in sample(range(10), 4))

    @staticmethod
    def generate_card_number():
        while True:
            s = str(IIN_BANKING) + "".join(str(n) for n in sample(range(10), 10))
            if Banking.LuhnAlgorithm(s):
                return s

    @staticmethod
    def LuhnAlgorithm(card_number):
        total_sum = 0
        for i, c in enumerate(reversed(str(card_number))):
            e = int(c) * (2 if i % 2 else 1)
            total_sum += sum(divmod(e, 10))
        return total_sum % 10 == 0

    @staticmethod
    def StoreCard(card_number, pin):
        cards.append(str(card_number))
        cards.append(str(pin))


def ClientMenu():
    print("1. Balance\n"
          "2. Add income\n"
          "3. Do transfer\n"
          "4. Close account\n"
          "5. Log Out\n"
          "0. Exit")


def ProcessClient():
    print("Your card has been created\n"
          "Your card number:")
    my_bank = Banking()
    user_id = randint(100, 999)
    cur.execute(f'INSERT INTO card (id, number, pin) VALUES ("{user_id}", "{my_bank.card_number}", "{my_bank.pin}");')
    conn.commit()
    print(my_bank.card_number)
    print("Your card PIN:")
    print(my_bank.pin)
    my_bank.StoreCard(my_bank.card_number, my_bank.pin)


def LogIn():
    banker = Banking()
    print("Enter your card number:")
    number = input()
    print("Enter your PIN:")
    number_pin = input()
    cur.execute("""SELECT number FROM card WHERE number=?""", (number,))
    given_result_for_number = cur.fetchone()
    cur.execute("""SELECT pin FROM card WHERE pin=?""", (number_pin,))
    given_result_for_pin = cur.fetchone()
    if given_result_for_number and given_result_for_pin:
        print("You have successfully logged in!")
        while True:
            client_choice = input("1. Balance\n"
                                  "2. Add income\n"
                                  "3. Do transfer\n"
                                  "4. Close account\n"
                                  "5. Log Out\n"
                                  "0. Exit\n")
            if client_choice == "1":
                cur.execute(f'SELECT balance FROM card WHERE number = {number};')
                conn.commit()
                bal = cur.fetchone()
                print("Balance: " + str(bal[0]))
            elif client_choice == "2":
                added_income = int(input("Enter income: "))
                cur.execute(f'UPDATE card SET balance = balance + {added_income} WHERE number = {number}')
                conn.commit()
                print("Income was added!")
            elif client_choice == "3":
                print("Transfer")
                while True:
                    print("Enter card number:")
                    entered_number = input()
                    cur.execute('SELECT number, COUNT(*) FROM card WHERE number = ? GROUP BY number', (entered_number,))
                    get_query = cur.fetchone()
                    if not get_query:
                        if not banker.LuhnAlgorithm(entered_number):
                            print("Probably you made a mistake in the card number. Please try again!")
                            break
                        else:
                            print("Such a card does not exist")
                            break
                    else:
                        if number == entered_number:
                            print("You can't transfer money to the same account!")
                        else:
                            print("Enter how much money you want to transfer:")
                            transfer_money = int(input())
                            cur.execute(f'SELECT balance FROM card WHERE number = {number};')
                            conn.commit()
                            money_safe = cur.fetchone()
                            if transfer_money > money_safe[0]:
                                print("Not enough money!")
                                break
                            else:
                                print("Success!")
                                cur.execute(f'UPDATE card SET balance = balance - {transfer_money} '
                                            f'WHERE number = {number}')
                                conn.commit()
                                cur.execute(f'UPDATE card SET balance = balance + {transfer_money} '
                                            f'WHERE number = {entered_number}')
                                conn.commit()
                                break
            elif client_choice == "4":
                cur.execute(f'DELETE FROM card WHERE number = {number}')
                conn.commit()
                print("The account has been closed!")
            elif client_choice == "5":
                print("Logged out successfully!")
                break
            elif client_choice == "0":
                print("Bye!")
                exit()
    else:
        print("Wrong card number or PIN!")


while True:
    given_choice = input("""1. Create an account\n2. Log into account\n0. Exit\n""")
    if given_choice == "1":
        ProcessClient()
    elif given_choice == "2":
        LogIn()
    elif given_choice == "0":
        print("Bye!")
        break
