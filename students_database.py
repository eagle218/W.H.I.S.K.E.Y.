"""
This Python code interacts with two databases, namely:

1. The Student database:
    It contains data about the students, including their personal information and a Telegram ID to connect with their data.
    It also stores their to-do lists.
    
2. The Schedule Table database:
    It stores data about the schedule of each group.
    Users can retrieve specific schedule information for a particular day, add new schedule entries, and modify existing ones.
    The app also provides notifications about the start of lessons.
    Additionally, the code includes the following class:

3. WordDatabase:
    Represents a database for storing words associated with Telegram users.
    Allows users to add new words, update existing word lists, and retrieve word information based on Telegram user IDs and languages.
    This database is designed to provide a way to store and manage words specific to each user's language preferences in a Telegram context.


4. OpenAiChatHistory:
        The OpenAiChatHistory class represents a database for storing 
        chat history data of Telegram users in a SQLite database. It provides methods 
        to create the necessary table, add new messages to the chat history, retrieve 
        the chat history for a specific user, clear the chat history, and close the database connection.

5. HomeworkBot:
    The HomeworkBot class represents a bot that manages homework data for Telegram users. 
    It interacts with a SQLite database to store and retrieve homework information.
"""


import re
import ast
import json
import locale
import config
import sqlite3
from bot_utils import Encryption




"""                                           """
"""              Students data                """
"""                                           """

class Student:
    def __init__(self) -> None:
        path = config.telegramUsersDatabase
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.encryption = Encryption()
        
    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS telegram_users
                    (id INTEGER PRIMARY KEY, username TEXT NOT NULL, group_text TEXT, aiUsing INTEGER DEFAULT 0, api_key TEXT)''')
    

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS todo_lists (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                task TEXT,
                FOREIGN KEY (user_id) REFERENCES telegram_users (id)
            )
        ''')

        self.conn.commit()


    """                                                 """
    """ Add user to database basing on his telegram ID  """
    """                                                 """

    def add_user(self, tg_id, tg_username):
        """
        This function adds or updates user information in the "telegram_users" table of the database.
       
        Parameters:
            - tg_id: The Telegram ID of the user (integer)
            - tg_username: The Telegram username of the user (string)
        Returns: None
        """
        self.c.execute("SELECT id FROM telegram_users WHERE id = ?", (tg_id,))
        existing_record = self.c.fetchone()

        if existing_record:
            self.c.execute("SELECT username FROM telegram_users WHERE id = ?", (tg_id,))
            existing_username = self.c.fetchone()[0]
            if existing_username != tg_username:
                self.c.execute("UPDATE telegram_users SET username = ? WHERE id = ?", (tg_username, tg_id))
                self.conn.commit()
        else:
            self.c.execute("INSERT INTO telegram_users (id, username) VALUES (?, ?)", (tg_id, tg_username))
            self.conn.commit()

    def add_user_with_group(self, id, group_text):
        """
        This function adds or updates user information along with group text in the "telegram_users" table of the database.
        Parameters:
            - id: The ID of the user (integer)
            - group_text: The group text associated with the user (string)
        Returns: None
        
        """
        self.c.execute("SELECT id FROM telegram_users WHERE id = ?", (id,))
        existing_record = self.c.fetchone()        
        
        if existing_record:
            self.c.execute("UPDATE telegram_users SET group_text = ? WHERE id = ?", (group_text, id))
        else:
            self.c.execute("INSERT INTO telegram_users (id, group_text) VALUES (?, ?)", (id, group_text))
            
        self.conn.commit()  



    """                                    """
    """      User tasks database           """
    """                                    """
    def add_task(self, user_id, task):
        """
        This function adds a task to the user's todo list in the "todo_lists" table of the database.
        Parameters:
            - user_id: The ID of the user (integer)
            - task: The task to be added (string)
        Returns:
            - True if the task was successfully added
            - False if the maximum limit of tasks (10) has been reached
        """
        tasks = self.get_tasks(user_id)
        if len(tasks) >= 10:
            return False

        self.c.execute("SELECT id FROM todo_lists WHERE user_id = ?", (user_id,))
        existing_record = self.c.fetchone()

        if existing_record:
            tasks.append(task)
            tasks_json = json.dumps(tasks)
            self.c.execute("UPDATE todo_lists SET task = ? WHERE user_id = ?", (tasks_json, user_id))
        else:
            self.c.execute("INSERT INTO todo_lists (user_id, task) VALUES (?, ?)", (user_id, json.dumps([task])))

        self.conn.commit()
        return True

    def mark_task_as_completed(self, user_id, index):
        """
        This function marks a task as completed in the user's todo list in the "todo_lists" table of the database.
        Parameters:
            - user_id: The ID of the user (integer)
            - index: The index of the task to be marked as completed (integer)
        Returns:
            - True if the task was successfully marked as completed
            - "Не коректний індекс задачі" if the index is invalid
            - "Задача вже відмічена, як виконана" if the task is already marked as completed
            - "Всі таски виконані" if all tasks in the list are marked as completed

        """
        tasks = self.get_tasks(user_id)
        if index < 0 or index >= len(tasks):
            return "Не коректний індекс задачі"
        
        if "✅" in tasks[index]:
            return "Задача вже відмічена, як виконана"
        
        
        tasks[index] += " ✅"  # Add the " ✅" symbol to mark the task as completed
        tasks_json = json.dumps(tasks)
        self.c.execute("UPDATE todo_lists SET task = ? WHERE user_id = ?", (tasks_json, user_id))
        self.conn.commit()
        task_done = 0
        for task in tasks:
            if "✅" in task:
                task_done += 1
        print(f"len {len(tasks)}, task_done {task_done}")
        if len(tasks) == task_done:
            return "Всі таски виконані"
        
        return True
    
    def get_tasks(self, user_id):
        """
        This function retrieves the tasks from the user's todo list in the "todo_lists" table of the database.
        Parameters:
            - user_id: The ID of the user (integer)
        Returns:
            - A list of tasks (strings) from the user's todo list
        """
        self.c.execute("SELECT task FROM todo_lists WHERE user_id = ?", (user_id,))
        tasks_json = self.c.fetchone()
        if tasks_json:
            tasks = json.loads(tasks_json[0])
            return tasks
        else:
            return []

  
    
    def delete_task_from_list(self, user_id, index):
        """
        This function deletes a task from the user's todo list in the "todo_lists" table of the database.
        Parameters:
            - user_id: The ID of the user (integer)
            - index: The index of the task to be deleted (integer)
        Returns:
            - "Задача успешно удалена" if the task was successfully deleted
            - "Некорректный индекс задачи" if the index is invalid
        
        """

        tasks = self.get_tasks(user_id)
        if index < 0 or index >= len(tasks):
            return "Некорректный индекс задачи"
        del tasks[index]
        tasks_json = json.dumps(tasks)
        self.c.execute("UPDATE todo_lists SET task = ? WHERE user_id = ?", (tasks_json, user_id))
        self.conn.commit()
        return "Задача успешно удалена"

    def delete_task(self, user_id):
        """
        Delete whole user todo-list 
        """
        self.c.execute("DELETE FROM todo_lists WHERE user_id = ?", (user_id,))
        self.conn.commit()



    def use_ai(self, user_id):
        """
        This function deletes the entire todo list of a user from the "todo_lists" table of the database.
        Parameters:
            - user_id: The ID of the user (integer)
        Returns: None
        """
        
        self.c.execute('SELECT aiUsing FROM telegram_users WHERE id = ?', (user_id,))
        result = self.c.fetchone()
        current_value = result[0] if result else 0
    
        new_value = current_value - 1 if current_value > 0 else 0

        self.c.execute('UPDATE telegram_users SET aiUsing = ? WHERE id = ?', (new_value, user_id))
        self.conn.commit()
        return True

    def ai_check(self, user_id):
        """
        checks how many requests users have left to the server OpenAI
        """
        self.c.execute('SELECT aiUsing FROM telegram_users WHERE id = ?', (user_id,))
        result = self.c.fetchone()
        current_value = result[0] if result else 0
       
        if current_value == 0:
            return False
        return True
    
    def insert_api_key(self, tg_id, api_key):
        """
        Insert user api-key in Database, using Encryption
        """
        encrypted_data = self.encryption.encrypt(api_key)

        self.c.execute("UPDATE telegram_users SET api_key = ? WHERE id = ?", (encrypted_data, tg_id))
        self.conn.commit()

    def get_decrypted_api_key(self, tg_id):
        """
        This function retrieves and decrypts the API key for a given Telegram user ID from the "telegram_users" table of the database.
        Parameters:
            - tg_id: The Telegram user ID (integer)
        Returns:
            - The decrypted API key if it exists and can be successfully decrypted
            - False if the API key does not exist, is empty, or cannot be decrypted
        """


        self.c.execute("SELECT api_key FROM telegram_users WHERE id = ?", (tg_id,))
        result = self.c.fetchone()
        if result is not None and result[0] != '':
            data = result[0]
            try:
                decrypted_data = self.encryption.decrypt(data)
                return decrypted_data
            except Exception as e:
                print(e)
                return False
        else:
            return False
        
    def check_api_key(self, tg_id):
        """
        This function checks if an API key exists for a given Telegram user ID in the "telegram_users" table of the database.
        Parameters:
            - tg_id: The Telegram user ID (integer)
        Returns:
            - True if an API key exists for the user
            - False if an API key does not exist for the user or is empty
        """
        self.c.execute("SELECT api_key FROM telegram_users WHERE id = ?", (tg_id,))
        result = self.c.fetchone()
        if result is not None and result[0] is not None and result[0] != '':
            encrypted_data = result[0]
            return True
        else:
            return False

    def select_by_group_id(self, group_id):
        """
        This function selects and prints all the rows from the "telegram_users" table that match the given group ID.
        Parameters:
            - group_id: The group ID (integer)
        Returns: None
        """
        self.c.execute("SELECT * FROM telegram_users WHERE group_id = ?", (group_id,))
        rows = self.c.fetchall()
        for row in rows:
            print(row)
    def update_username(self, id_tg, new_username):
        """
        This function updates the username of a Telegram user with the given ID in the "telegram_users" table.
        Parameters:
            - id_tg: The Telegram user ID (integer)
            - new_username: The new username (string)
        Returns: None
        """
        self.c.execute("UPDATE telegram_users SET username = ? WHERE id = ?", (new_username, id_tg))
        self.conn.commit()



    def select_username_and_group_name(self, id_tg):
        """
        This function selects and returns the username associated with the given Telegram user ID from the "telegram_users" table.
        Parameters:
            - id_tg: The Telegram user ID (integer)
        Returns:
            - The username associated with the user ID if it exists
            - None if the user ID does not exist
        """
        self.c.execute("SELECT username FROM telegram_users WHERE id = ?", (id_tg,))
        rows = self.c.fetchall()
        if rows:
            username = rows[0][0]
            return username
        else:
            return None
    
    def check_group_for_user(self, id):
        """
        This function checks and returns the group text associated with the given user ID from the "telegram_users" table.
        Parameters:
            - id: The user ID (integer)
        Returns:
            - The group text associated with the user ID if it exists
            - None if the user ID does not exist
        """
        self.c.execute("SELECT group_text FROM telegram_users WHERE id = ?", (id,))
        existing_group = self.c.fetchone()

        if existing_group:
            return existing_group[0]
        else:
            return None
    
    def select_all(self):
        """
        This function selects and prints all the rows from the "telegram_users" table.
        Parameters: None
        Returns: None
        """
        self.c.execute("SELECT * FROM telegram_users")
        rows = self.c.fetchall()
        for row in rows:
            print(row)

    def select_users_id(self):
        self.c.execute("SELECT id FROM telegram_users")
        rows = self.c.fetchall()
        return rows
    def close_connection(self):
        self.conn.close()
    def delete_user(self, id):
        self.c.execute("DELETE FROM telegram_users WHERE id = ?", (id,))
        self.conn.commit()

st = Student()
print(st.select_users_id())
"""                                           """
"""              translated Words             """
"""                                           """


class WordDatabase:
    def __init__(self, db_name=config.telegramUsersDatabase):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_word_table(self):
        self.connect()
        c = self.conn.cursor()

        # Create the words table
        c.execute('''CREATE TABLE IF NOT EXISTS words
                     (telegram_id INTEGER, language TEXT, words TEXT)''')

        self.conn.commit()
        self.disconnect()

    def add_word(self, telegram_id, language, word):
        """
        This function adds a word to the word list associated with a Telegram user ID and language in the "words" table.
        Parameters:
            - telegram_id: The Telegram user ID (string)
            - language: The language associated with the word (string)
            - word: The word to be added (string)
        Returns: None
        """

        self.connect()
        c = self.conn.cursor()

        # Check if there is an existing row for Telegram ID and language
        c.execute("SELECT words FROM words WHERE telegram_id=? AND language=?", (telegram_id, language))
        existing_words = c.fetchone()

        if existing_words is None:
            # If the row doesn't exist, create a new one
            words = [word]
            c.execute("INSERT INTO words VALUES (?, ?, ?)", (telegram_id, language, str(words)))
        else:
            # If the row exists, update the word list
            words = eval(existing_words[0]) if isinstance(existing_words[0], str) else existing_words[0]  # Convert the string back to a list if necessary

            if isinstance(words, list):
                words.append(word)
            else:
                words = [words, word]  # Create a new list with existing word and new word

            c.execute("UPDATE words SET words=? WHERE telegram_id=? AND language=?", (str(words), telegram_id, language))

        self.conn.commit()
        self.disconnect()


    
    def get_specific_language_words(self, telegram_id, language):
        """
        This function retrieves the word list associated with a specific Telegram user ID and language from the "words" table.
        Parameters:
            - telegram_id: The Telegram user ID (string)
            - language: The language associated with the word list (string)
        Returns:
            - A list of words associated with the Telegram user ID and language. If no words are found, an empty list is returned.
        """
        self.connect()
        c = self.conn.cursor()

        # Check if there is an existing row for Telegram ID and language
        c.execute("SELECT words FROM words WHERE telegram_id=? AND language=?", (telegram_id, language))
        existing_words = c.fetchone()

        if existing_words is not None:
            words = eval(existing_words[0])  # Convert the string back to a list
            return words

        self.disconnect()
        return []
    
    def display_all_data(self, telegram_id):
        """ Return all user words """
        self.connect()
        c = self.conn.cursor()

        c.execute("SELECT language, words FROM words WHERE telegram_id=?", (telegram_id,))  

        rows = c.fetchall()
    
        return rows
    

        self.disconnect()

    def add_checkmark_to_word(self, telegram_id, language, index):
        """
        This function adds a checkmark symbol ('✅') to a word at a specific index in the word list associated with a Telegram user ID and language.
        Parameters:
            - telegram_id: The Telegram user ID (string)
            - language: The language associated with the word list (string)
            - index: The index of the word to add a checkmark to (integer)
        Returns:
            - If the checkmark is successfully added, it returns None.
            - If the word at the specified index already has a checkmark, it returns the string "It was checked".
            - If the index is out of range, it returns False.
        """
        self.connect()
        c = self.conn.cursor()

        # Check if there is an existing row for Telegram ID and language
        c.execute("SELECT words FROM words WHERE telegram_id=? AND language=?", (telegram_id, language))
        existing_words = c.fetchone()

        if existing_words is not None:
            words = eval(existing_words[0])  # Convert the string back to a list

            if 0 <= index < len(words):
                word = words[index]
                if not word.endswith('✅'):
                    words[index] = word + '✅'
                    c.execute("UPDATE words SET words=? WHERE telegram_id=? AND language=?", (str(words), telegram_id, language))
                else:
                    return "Its was checked"

            else:
                return False
        self.conn.commit()
        self.disconnect()

    def remove_word_by_index(self, telegram_id, language, index):
        """
        This function removes a word from the word list at a specific index associated with a Telegram user ID and language.
        Parameters:
            - telegram_id: The Telegram user ID (string)
            - language: The language associated with the word list (string)
            - index: The index of the word to remove (integer)
        Returns:
            - None
        """
        self.connect()
        c = self.conn.cursor()

        # Check if there is an existing row for Telegram ID and language
        c.execute("SELECT words FROM words WHERE telegram_id=? AND language=?", (telegram_id, language))
        existing_words = c.fetchone()

        if existing_words is not None:
            words = eval(existing_words[0])  # Convert the string back to a list

            if 0 <= index < len(words):
                del words[index]  # Remove the word at the specified index
                c.execute("UPDATE words SET words=? WHERE telegram_id=? AND language=?", (str(words), telegram_id, language))

        self.conn.commit()
        self.disconnect()

    def remove_words_by_language(self, telegram_id, language):
        """"
        This function removes all words for a specified language associated with a Telegram user ID.
        Parameters:
        - telegram_id: The Telegram user ID (string)
        - language: The language to remove words for (string)
        Returns:
        - None
        """

        self.connect()
        c = self.conn.cursor()

        # Remove all words for the specified language
        c.execute("DELETE FROM words WHERE telegram_id=? AND language=?", (telegram_id, language))

        self.conn.commit()
        self.disconnect()


    def delete_all_words(self):
        """ Delete all user word """
        self.connect()
        c = self.conn.cursor()

        # Delete all rows from the words table
        c.execute("DELETE FROM words")

      
        self.conn.commit()
        self.disconnect()



"""                                                  """
"""              Chatgpt history data                """
"""                                                  """

class OpenAiChatHistory:
    """
    This class represents a chat history storage for OpenAI-based chatbot conversations.
    Methods:
        - __init__(): Initializes the OpenAiChatHistory object and establishes a connection to the database.
        - create_table(): Creates the "chat_history" table if it doesn't exist in the database.
        - add_message(tg_id, message): Adds a new message to the chat history for the specified Telegram user ID.
        - get_chat_history(tg_id): Retrieves the chat history for the specified Telegram user ID.
        - clear_chat_history(tg_id): Clears the chat history for the specified Telegram user ID.
        - close_connection(): Closes the database connection.
    """
    def __init__(self):
        self.db_path = config.telegramUsersDatabase
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
    
    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                            (tg_id INTEGER, text TEXT, PRIMARY KEY (tg_id))''')
        self.conn.commit()

    def add_message(self, tg_id, message):
        current_history = self.get_chat_history(tg_id)
        current_history.append(message)
        
        if len(current_history) > 6:
            current_history = current_history[-6:]
            
        history_json = json.dumps(current_history)  # Serialize the history as a JSON string
        self.c.execute("INSERT OR REPLACE INTO chat_history (tg_id, text) VALUES (?, ?)",
                    (tg_id, history_json))
        self.conn.commit()

    def get_chat_history(self, tg_id):
        self.c.execute("SELECT text FROM chat_history WHERE tg_id = ?", (tg_id,))
        result = self.c.fetchone()
        if result:
            history_json = result[0]
           
            try:
                history = json.loads(history_json)[-1]
                
                if isinstance(history, list):
                    return history
                else:
                    print("Invalid chat history format. Returning an empty list.")
                    return []
            except json.decoder.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return []
        else:
            return []


    def clear_chat_history(self, tg_id):
        self.c.execute("DELETE FROM chat_history WHERE tg_id = ?", (tg_id,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()




"""                                           """
"""              ScheduleTable                """
"""                                           """

class ScheduleTable:
    """
    This class represents a schedule table for storing and managing class schedules.
    Methods:
    - __init__(): Initializes the ScheduleTable object and establishes a connection to the database.
                  Creates the "schedule" table if it doesn't exist.
    - execute_query(query, args=None): Executes the given SQL query with optional arguments and returns the result.
    - get_current_schedule_message(group_name, day_of_week, num_week='1'): Retrieves the current schedule message for the specified group, day of the week, and week number.
    - get_schedule_message(group_name, day_of_week, num_week='1'): Retrieves the schedule message for the specified group, day of the week, and week number.
    - select_all_groups(): Retrieves a list of all distinct group names in the schedule table.
    - select_all(): Retrieves all rows from the schedule table and prints them.
    - get_subject_by_day_and_time(group, day_of_week, time, num_week): Retrieves the subject and time for the specified group, day of the week, and week number.
    - get_schedule_data_using_telegramID(tg_id, day_of_week): Retrieves the schedule data for the specified Telegram ID and day of the week.
    - del_group_schedule_of_day(self, group_name, day_of_week): Deletes all schedules for a specific group on a given day of the week.
    """
    def __init__(self):
        db_file = config.scheduleDataBase
        self.conn = sqlite3.connect(db_file)
        
        #self.conn.execute("DROP TABLE IF EXISTS schedule")
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schedule';")
        if not cursor.fetchone():
            cursor.execute('''CREATE TABLE schedule
                (group_name TEXT, day_of_week TEXT, schedule TEXT, num_week INTEGER DEFAULT 0, 
                UNIQUE(group_name, day_of_week, schedule, num_week))''')
            self.conn.commit()
        cursor.close()
        
    def insert_schedule(self, group, day_of_week, schedule, num_week):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO schedule (group_name, day_of_week, schedule, num_week) VALUES (?, ?, ?, ?)',
                        (group, day_of_week, str(schedule), num_week))
            self.conn.commit()
            print(f"Schedule added: {group}, {day_of_week}, {schedule}, {num_week}")
        except sqlite3.IntegrityError:
            cursor.execute('UPDATE schedule SET num_week=? WHERE group_name=? AND day_of_week=? AND schedule=?',
                        (num_week, group, day_of_week, str(schedule)))
            self.conn.commit()
            print(f"Schedule updated: {group}, {day_of_week}, {schedule}, {num_week}")


    def check_booked_time(self, group_name, day_of_week, time):
        result = self.get_current_schedule_message(group_name, day_of_week, num_week=1)
        result_list = [ast.literal_eval(item[0]) for item in result]

        for data in result_list:

            if data[0][0][1] == time:
                
                return False
        return True
    
    """ Main insert, """
    def insert_test(self, group_name, day_of_week, subject, time, num_week):
        # Формуємо розклад для перевірки
        new_schedule = [[(subject, time)]]
        new_schedule = str(new_schedule)
        try:
            cursor = self.conn.cursor()

            if self.check_booked_time(group_name, day_of_week, time) == False:
                print("Цей часовий слот вже зайнятий.")
                return False

            cursor.execute('INSERT INTO schedule (group_name, day_of_week, schedule, num_week) VALUES (?, ?, ?, ?)',
                        (group_name, day_of_week, new_schedule, num_week))
            self.conn.commit()
            print(f"New schedule added: {group_name}, {day_of_week}, {subject}, {time}, {num_week}")
                
        except sqlite3.IntegrityError:
            print("Помилка бази даних.")
            return False

    
    def execute_query(self, query, args=None):
        cursor = self.conn.cursor()
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def get_current_schedule_message(self, group_name, day_of_week, num_week='1'):
        cursor = self.conn.cursor()
        cursor.execute("SELECT schedule FROM schedule WHERE group_name =? AND day_of_week=? AND num_week=?", (group_name, day_of_week, num_week))
        rows = cursor.fetchall()
        return rows
   
    def get_schedule_message(self, group_name, day_of_week, num_week='1'):
        
        cursor = self.conn.cursor()

        cursor.execute("SELECT schedule FROM schedule WHERE group_name=? AND day_of_week=? AND num_week=?", (group_name, day_of_week, num_week))
        results = cursor.fetchall()
        cursor.close()

        
        if len(results) == 0:
            message = "Нет данных о расписании для данной группы и дня недели."
            print(message)
            return False
        else:
            message = [row[0] for row in results]
            result = []
            
            for item in message:
                message = eval(item)
                result.append([message[0][0][0], message[0][0][1]])
            return result
        
        return message
    
    def select_all_groups(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT group_name FROM schedule")
        groups = cursor.fetchall()
        groups_name = []
        for group in groups:
            groups_name.append(group[0])
            # print(group)
            # print(groups_name)
        return groups_name
    def select_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM schedule")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Group: {row[0]}, Day: {row[1]}, Schedule: {row[2]}, Week(0/1): {row[3]}")

    def get_subject_by_day_and_time(self, group, day_of_week, time, num_week):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT schedule FROM schedule WHERE group_name=? AND day_of_week=? AND num_week=?',
                        (group, day_of_week, num_week))
            result = cursor.fetchone()

            if result is not None:
                existing_schedule = eval(result[0])  

                for entry in existing_schedule:
                    if entry[0][1] == time:
                        print(entry[0][0], entry[0][1])
                        return entry[0][0], entry[0][1]

            return None
        except sqlite3.IntegrityError:
            print("Помилка бази даних.")

    def get_schedule_data_using_telegramID(self, tg_id, day_of_week):
        conn1 = sqlite3.connect(config.scheduleDataBase)
        c1 = conn1.cursor()

        conn2 = sqlite3.connect(config.telegramUsersDatabase)
        c2 = conn2.cursor()

        
        c2.execute("SELECT group_text FROM telegram_users WHERE id = ?", (tg_id,))
        result2 = c2.fetchone()
        data = self.get_schedule_message(result2[0], day_of_week)
        return data

    def del_group_schedule_of_day(self, group_name, day_of_week):
        self.conn.execute("DELETE FROM schedule WHERE group_name=? AND day_of_week=?", (group_name, day_of_week))
        self.conn.commit()
        print(f"All schedules for group {group_name} on {day_of_week} have been deleted.")


    def del_qwe(self):
        self.conn.execute("DELETE FROM schedule WHERE group_name=?", ('422',))
        self.conn.commit()

    def __del__(self):
        self.conn.close()



class HomeworkBot:
    """
    This class represents a bot that helps manage homework tasks for different subjects. 
    def __init__(self):
        Initializes the HomeworkBot and establishes a connection to the database.

    def add_homework(self, telegram_id, subject, task):
        Adds a homework task for a specific Telegram user and subject.

    def get_homework(self, telegram_id, subject):
        Retrieves the homework tasks for a specific Telegram user and subject.

    def get_user_subjects(self, telegram_id):
        Retrieves the list of subjects for a specific Telegram user.

    def remove_homework_from_subject(self, telegram_id, subject):
        Removes all homework tasks for a specific Telegram user and subject.

    def remove_all_homework(self, telegram_id):
        Removes all homework tasks for a specific Telegram user.

    def close_connection(self):
        Closes the database connection.
    """
    def __init__(self):
        db_name = config.scheduleDataBase
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS homework
                          (telegram_id TEXT, subject TEXT, tasks TEXT)''')
       

    def add_homework(self, telegram_id, subject, task):
        # Check if there is already an entry for the given Telegram ID and item
        self.c.execute("SELECT tasks FROM homework WHERE telegram_id=? AND subject=?", (telegram_id, subject))
        result = self.c.fetchone()

        if result:
            # If the entry already exists, update the list of jobs
            tasks = ast.literal_eval(result[0])
            tasks.append(task)
            self.c.execute("UPDATE homework SET tasks=? WHERE telegram_id=? AND subject=?", (str(tasks), telegram_id, subject))
        else:
            # If there is no entry, create a new entry
            self.c.execute("INSERT INTO homework (telegram_id, subject, tasks) VALUES (?, ?, ?)", (telegram_id, subject, str([task])))

        self.conn.commit()

    def get_homework(self, telegram_id, subject):
        self.c.execute("SELECT tasks FROM homework WHERE telegram_id=? AND subject=?", (telegram_id, subject))
        result = self.c.fetchone()

        if result:
            tasks = ast.literal_eval(result[0])
            return tasks
        else:
            return []
    
    def get_user_subjects(self, telegram_id):
        self.c.execute("SELECT DISTINCT subject FROM homework WHERE telegram_id=?", (telegram_id,))
        results = self.c.fetchall()
        subjects = [result[0] for result in results]
        return subjects

    def remove_homework_from_subject(self, telegram_id, subject):
        self.c.execute("DELETE FROM homework WHERE telegram_id=? and subject=?", (telegram_id, subject))
        self.conn.commit()
        

    def remove_all_homework(self, telegram_id):
        self.c.execute("DELETE FROM homework WHERE telegram_id=?", (telegram_id,))
        self.conn.commit()
        
    def close_connection(self):
        self.conn.close()



