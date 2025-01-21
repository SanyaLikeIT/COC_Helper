import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command

API_TOKEN = "7864302137:AAEuxMOLv1wb8GtJKHuNWJyJj_JDZA4s1qk"

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение к базе данных
conn = sqlite3.connect("accounts.db")
cursor = conn.cursor()

# Создание таблиц в базе данных
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS processes (
    process_id INTEGER PRIMARY KEY,
    account_id INTEGER,
    start_time REAL,
    duration REAL,
    description TEXT,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
)
""")
conn.commit()


class AccountStates(StatesGroup):
    waiting_for_decision = State()
    waiting_for_id = State()
    waiting_for_name = State()
    waiting_for_remove = State()


class ProcessStates(StatesGroup):
    waiting_for_choice = State()
    waiting_for_account_id = State()
    waiting_for_description = State()
    waiting_for_duration = State()
    waiting_for_remove_id = State()


def format_time_left(seconds):
    """Форматирует оставшееся время в удобный вид."""
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    time_parts = []
    if days > 0:
        time_parts.append(f"{int(days)} days")
    if hours > 0:
        time_parts.append(f"{int(hours)} hours")
    if minutes > 0:
        time_parts.append(f"{int(minutes)} minutes")
    if seconds > 0:
        time_parts.append(f"{int(seconds)} seconds")

    return " ".join(time_parts)


@dp.message(Command(commands="start"))
async def main(message: Message):
    await message.answer("Hello! Here are my commands:\n"
                         "/process - Add or remove process\n"
                         "/list - Get a list of all accounts and their processes\n"
                         "/id - Get a list of all account IDs\n"
                         "/account - Add or remove account\n"
                         "/cancel - Cancel the current operation")
    await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAENhsZni5Du8ss8dlz9hdb-MVePVm630wACERgAAv564UuysbzruCnEmzYE")


@dp.message(Command(commands="cancel"))
async def cancel_operation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Operation canceled. You can now choose a new action.")


@dp.message(Command(commands="account"))
async def start_account(message: Message, state: FSMContext):
    if (message.from_user.id == 1196215949):
        await message.answer("Choose the option:\n0 - Add account\n1 - Remove account\n/cancel to cancel")
        await state.set_state(AccountStates.waiting_for_decision)
    else:
        await bot.send_message(message.chat.id, "Sorry, you don't have access.")
        await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAENhsFni4zgRorerdq-LKWh--93tPB6MwACsxAAAmxC8UtrAl3OwiBfvzYE")

@dp.message(AccountStates.waiting_for_decision)
async def decision(message: Message, state: FSMContext):
    if message.text == "0":
        await message.answer("Please enter the account ID:")
        await state.set_state(AccountStates.waiting_for_id)
    elif message.text == "1":
        await message.answer("Please enter the account ID to remove:")
        await state.set_state(AccountStates.waiting_for_remove)
    else:
        await message.answer("Invalid input. Please enter 0 or 1.")


# Обработчики
@dp.message(AccountStates.waiting_for_remove)
async def remove_account(message: Message, state: FSMContext):
    account_id = message.text  # ID аккаунта для удаления
    
    # Проверяем, существует ли аккаунт
    cursor.execute("SELECT id FROM accounts WHERE id = ?", (account_id,))
    account = cursor.fetchone()

    if account is None:
        await message.answer("Account with this ID does not exist. Operation canceled.")
    else:
        # Удаляем связанные процессы
        cursor.execute("DELETE FROM processes WHERE account_id = ?", (account_id,))
        # Удаляем сам аккаунт
        cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()

        await message.answer(f"Account with ID {account_id} and all its processes have been removed successfully.")
    
    await state.clear()

@dp.message(AccountStates.waiting_for_id)
async def get_account_id(message: Message, state: FSMContext):
    account_id = message.text  # Теперь не нужно преобразование в число
    await state.update_data(account_id=account_id)
    await message.answer("Please enter the account name:")
    await state.set_state(AccountStates.waiting_for_name)

@dp.message(AccountStates.waiting_for_name)
async def get_account_name(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data.get("account_id")
    account_name = message.text

    try:
        cursor.execute("INSERT INTO accounts (id, name) VALUES (?, ?)", (account_id, account_name))
        conn.commit()
        await state.clear()
        await message.answer(f"Account added successfully:\nID: {account_id}, Name: {account_name}")
    except sqlite3.IntegrityError:
        await message.answer("Account with this ID already exists. Operation canceled.")
        await state.clear()


@dp.message(Command(commands="process"))
async def manage_process(message: Message, state: FSMContext):
    if (message.from_user.id == 1196215949):
        await message.answer("Do you want to add or remove a process?\n0 - Add\n1 - Remove\n/cancel to cancel")
        await state.set_state(ProcessStates.waiting_for_choice)
    else:
        await bot.send_message(message.chat.id, "Sorry, you don't have access.")
        await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAENhsFni4zgRorerdq-LKWh--93tPB6MwACsxAAAmxC8UtrAl3OwiBfvzYE")


@dp.message(ProcessStates.waiting_for_choice)
async def process_choice(message: Message, state: FSMContext):
    if message.text == "0":
        await message.answer("Enter the account ID:")
        await state.set_state(ProcessStates.waiting_for_account_id)
    elif message.text == "1":
        await message.answer("Enter the process ID to remove:")
        await state.set_state(ProcessStates.waiting_for_remove_id)
    else:
        await message.answer("Invalid input. Please enter 0 or 1.")


@dp.message(ProcessStates.waiting_for_account_id)
async def add_process_account_id(message: Message, state: FSMContext):
    account_id = message.text  # Оставляем как текст
    cursor.execute("SELECT id FROM accounts WHERE id = ?", (account_id,))
    if cursor.fetchone() is None:
        await message.answer("Account with this ID does not exist.")
        await state.clear()
    else:
        await state.update_data(account_id=account_id)
        await message.answer("Enter the process description:")
        await state.set_state(ProcessStates.waiting_for_description)


@dp.message(ProcessStates.waiting_for_description)
async def add_process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Enter the process duration (in format: days hours minutes):")
    await state.set_state(ProcessStates.waiting_for_duration)


@dp.message(ProcessStates.waiting_for_duration)
async def add_process_duration(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        account_id = data["account_id"]
        description = data["description"]

        duration_input = message.text.split()
        days, hours, minutes = map(int, duration_input)
        duration_seconds = days * 86400 + hours * 3600 + minutes * 60

        cursor.execute("INSERT INTO processes (account_id, start_time, duration, description) VALUES (?, ?, ?, ?)",
                       (account_id, time.time(), duration_seconds, description))
        conn.commit()

        await state.clear()
        await message.answer("Process added successfully.")
    except (ValueError, IndexError):
        await message.answer("Invalid duration format. Use: days hours minutes.")


@dp.message(ProcessStates.waiting_for_remove_id)
async def remove_process(message: Message, state: FSMContext):
    try:
        process_id = int(message.text)
        cursor.execute("DELETE FROM processes WHERE process_id = ?", (process_id,))
        conn.commit()

        if cursor.rowcount > 0:
            await message.answer("Process removed successfully.")
        else:
            await message.answer("Process with this ID does not exist. Try again")
        #await state.clear()
    except ValueError:
        await message.answer("Invalid input. Please enter a valid numeric ID.")

@dp.message(Command(commands="list"))
async def list_accounts(message: Message):
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()

    if accounts:
        response = []
        for account in accounts:
            account_id, name = account
            cursor.execute("SELECT * FROM processes WHERE account_id = ?", (account_id,))
            processes = cursor.fetchall()

            account_info = f"Account ID: {account_id}, Name: {name}"
            if processes:
                for process in processes:
                    process_id, _, start_time, duration, description = process
                    time_left = max(0, start_time + duration - time.time())
                    formatted_time = format_time_left(time_left)
                    account_info += f"\nProcess ID: {process_id}, Remaining time: {formatted_time}, Description: {description}"
            else:
                account_info += "\nNo active processes"
            account_info += "\n"
            response.append(account_info)

        await message.answer("\n\n".join(response))
        await bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAENjINnjtfgHkovW4ZNG179PVjcOheSJAACVgwAAoBcuVZfeZN3lJAMyjYE")

    else:
        await message.answer("No accounts found.")


@dp.message(Command(commands="id"))
async def list_ids(message: Message):
    cursor.execute("SELECT id, name FROM accounts")
    accounts = cursor.fetchall()

    if accounts:
        response = "\n".join([f"ID: {account[0]}, Name: {account[1]}" for account in accounts])
        await message.answer(response)
        await bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAENhGtnieJCWBGcVcGbFIRxtS8_VCraLwACzAoAAuuVwVYiRNf_jNMtPTYE")
    else:
        await message.answer("No accounts found.")

async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())