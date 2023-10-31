![image](https://github.com/eagle218/W.H.I.S.K.E.Y./assets/113504886/7fe14841-0fb8-46c8-bd75-0dbd802e8c18)# W.H.I.S.K.E.Y.
Telegram bot to help students

![Uploading image.png…]()

Telegram Messenger Helper App
This app provides various functionalities to help students using Telegram Messenger. It uses an SQLite database for data storage and retrieval.

main.py:

    Functionality provided by this app includes:

    Schedule Operations;

    Document Operations;

    Foreign words operation;

    Task Operations;

    Homework Operations;

    AI Operations;

    Miscellaneous Operations;


    Note: Some commands require additional user input or file uploads for proper functionality.


bot_utils.py:

    Telegram Bot Helper Functions

    This repository contains various helper functions for a Telegram bot. These functions provide different functionalities such as encryption, data parsing, learning resources retrieval, weather classification, AI response generation, translation, image generation, image classification, background removal, document creation, and weekday finding.

    Table of Contents
    Encryption

    encrypt(message, key): Encrypts a message using a specified key.
    decrypt(ciphertext, key): Decrypts a ciphertext using a specified key.
    Data Parser

    data_parser(url): Parses news data from the specified URL and returns a list of news articles.
    Learning Resources Links

    learning_resources_links(query): Retrieves a list of learning resource links related to the given query.
    Weather Classification

    weather_classified(text): Classifies weather-related text and extracts the mentioned city name.
    AI Response Generation

    AI_response(conversation_history): Generates an AI response based on the user's conversation history using the OpenAI GPT-3.5 Turbo model.
    Translation

    translate_text(text, source_lang, target_lang): Translates text from one language to another using a translation service.
    Image Generation

    generate_image(query): Generates an image based on the specified query.
    Image Classification

    imageClassification(image_path): Performs image classification using a pre-trained model.
    Background Removal

    background_remove(image_path, output_path): Removes the background from an input image and saves the result.
    Document Creation for Special Topic

    document_creating_for_special_topic(topic, group, your_name, instructor_name): Creates a document with the specified topic, group, your name, and instructor name.
    Weekday Finding

    find_weekday(date): Finds the weekday for the given date.
    For detailed information about each function, please refer to the respective function's documentation in the code.

    This bot is developed using the aiogram library.




students_database.py:
This Python code interacts with two databases and includes several classes to provide various functionalities in the Telegram Messenger Helper App.

Student Database:

    Represents a database for storing student data, including personal information and Telegram IDs.
    Provides methods for retrieving student data and managing to-do lists.
    Schedule Table Database:

    Represents a database for storing schedule information for different groups.
    Allows users to retrieve specific schedule information for a particular day, add new schedule entries, and modify existing ones.
    Provides notifications about the start of lessons.
    WordDatabase:

    Represents a database for storing words associated with Telegram users.
    Allows users to add new words, update existing word lists, and retrieve word information based on Telegram user IDs and languages.
    OpenAiChatHistory:

    Represents a database for storing chat history data of Telegram users in a SQLite database.
    Provides methods to create the necessary table, add new messages to the chat history, retrieve the chat history for a specific user, clear the chat history, and close the database connection.
    HomeworkBot:

    Represents a bot that manages homework data for Telegram users.
    Interacts with a SQLite database to store and retrieve homework information.
    The code is designed to provide functionality for various operations such as schedule management, group operations, document creation, foreign words translation, task management, homework operations, AI operations, and miscellaneous operations.
