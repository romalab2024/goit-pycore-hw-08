import pickle
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. Only 10 digits are allowed.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday is None:
            return None
        today = datetime.now().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        self.records[record.name.value] = record

    def find(self, name):
        return self.records.get(name)

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.records.values():
            if record.birthday:
                days_to_bday = record.days_to_birthday()
                if days_to_bday is not None and 0 < days_to_bday <= days:
                    upcoming_birthdays.append((record.name.value, days_to_bday))
        return upcoming_birthdays

# Серіалізація та десеріалізація
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# Декоратор для обробки помилок вводу
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Error: Not enough arguments provided."
        except ValueError as e:
            return f"Error: {e}"
        except KeyError:
            return "Error: Contact not found."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        for i, phone in enumerate(record.phones):
            if phone.value == old_phone:
                record.phones[i] = Phone(new_phone)
                return f"Phone number for {name} updated."
        return f"Phone number {old_phone} not found for {name}."
    return f"Contact {name} not found."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for {name} added."
    return f"Contact {name} not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
    return f"Birthday for {name} not found."

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next week."
    return "\n".join(f"{name} has a birthday in {days} days" for name, days in upcoming_birthdays)

@input_error
def show_all(book: AddressBook):
    contacts = []
    for name, record in book.records.items():
        phones = ', '.join(phone.value for phone in record.phones)
        birthday = record.birthday.value.strftime('%d.%m.%Y') if record.birthday else "No birthday"
        contacts.append(f"{name}: Phones: {phones}; Birthday: {birthday}")
    return "\n".join(contacts) if contacts else "Address book is empty."

def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0], parts[1:]

def main():
    # Завантаження даних адресної книги з файлу
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # Збереження даних перед виходом
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            name = args[0]
            record = book.find(name)
            if record:
                print(f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}")
            else:
                print(f"Contact {name} not found.")

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
