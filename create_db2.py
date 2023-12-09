import psycopg2
from psycopg2 import extras

conn = psycopg2.connect(database="englishbot", user="postgres", password="postgres")

words = {'Car': 'Машина', 'Peace': 'Мир', 'Green': 'Зелёный', 'Hello': 'Привет'}


def create_tables():
    """Создаём таблицы БД, добавлена проверка
     слов и их переводов на уникальность"""

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS USERS(
        USER_ID SERIAL PRIMARY KEY,
        USER_NUMBER INTEGER UNIQUE NOT NULL);
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS WORDS(
        WORD_ID SERIAL PRIMARY KEY,
        WORD VARCHAR(80) NOT NULL,
        TRANSLATION VARCHAR(80) NOT NULL);
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS USERS_WORDS(
        USER_ID INTEGER NOT NULL REFERENCES USERS(USER_ID),
        WORD_ID INTEGER NOT NULL REFERENCES WORDS(WORD_ID),
        CONSTRAINT PK PRIMARY KEY (USER_ID, WORD_ID)
        );
        """)

        conn.commit()


def check_user(chat_id): # помимо ID почему-то всегда возвращает None
    """Проверяет chat_id на наличие в БД,
     в случае наличия - возвращает True"""
    with conn.cursor() as cur:
        cur.execute("""
        SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s
        """, [chat_id])
        result = cur.fetchone()
        if result:
            #print(result[0])
            return True
        else:
            return False


def add_user_to_db(chat_id):
    """Добавляем chat_id пользователя в БД"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO USERS(USER_NUMBER) VALUES
            (%s)
            """, [chat_id])
            conn.commit()
            print(f'Chat_id {chat_id} added')
        except:
            print(f'[INFO] пользователь {chat_id} уже есть в БД')

        #finally:
        #    if conn:
        #        conn.close()
        #        print(f'[INFO] PostgreSQL connection closed')


def add_word(word, translation, chat_id):
    """Добавляем слова и их перевод в БД, связываем слова и пользователя"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO WORDS(WORD, TRANSLATION) VALUES
            (%s, %s)
            """, (word, translation))
        except:
            print(f'[INFO] Слово {word} уже есть в БД')
        try:
            cur.execute("""
            SELECT WORD_ID FROM WORDS WHERE WORD=%s 
            """, [word])
            word_id = cur.fetchone()  # Получаем id слова из таблицы words
            #print(f'{word} id is {word_id}')

            cur.execute("""
            SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s 
            """, [chat_id])
            user_id = cur.fetchone()[0] # Получаем id пользователя из таблицы words
            #print(f'{chat_id} : {user_id}')

            cur.execute("""
            INSERT INTO USERS_WORDS(USER_ID,WORD_ID) VALUES
            (%s,%s)
            """, (user_id, word_id)) # Связываем добавляемое слово и пользователя

            conn.commit()

        except:
            print(f'[INFO] Слово уже привязано к пользователю')

        #finally:
        #    if conn:
        #        conn.close()
        #        print(f'[INFO] Соединение с БД Postgres закрыто')


def get_words(chat_id):
    """Получаем 4 случайных пары слов и переводов для заданного пользователя"""
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("""
            SELECT WORDS.WORD, WORDS."translation"
            FROM USERS, USERS_WORDS, WORDS
            WHERE 
            USERS_WORDS.USER_ID = USERS.USER_ID
            AND USERS_WORDS.WORD_ID = WORDS.WORD_ID
            AND USERS.USER_NUMBER = %s
            ORDER by random()
            limit 4
            """, [chat_id])
            rows = cur.fetchall()
            dct = [{k: v for k, v in record.items()} for record in rows]  # формируем словарь из 4-х слов
            return dct

        except:
            print(f'[INFO] Ошибка БД Postgres')


def get_words_count(chat_id):
    """Получаем 4 случайных пары слов и переводов для заданного пользователя"""
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("""
                        SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s 
                        """, [chat_id])
            user_id = cur.fetchone()[0]  # Получаем id пользователя из таблицы words
        except:
            print(f'[INFO] Ошибка БД Postgres')

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("""
                        SELECT COUNT(word_id)
                        FROM public.users_words
                        WHERE user_id=%s;
                        """, [user_id])
            words_count = cur.fetchone()[0]
            return words_count
        except:
            print(f'[INFO] Ошибка БД Postgres')


if __name__ == '__main__':
    #create_tables()
    # a = get_words_count(5306142)
    # print(a)
    pass