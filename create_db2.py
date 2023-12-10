import psycopg2
from psycopg2 import extras

conn = psycopg2.connect(database="englishbot", user="postgres", password="postgres")

words = {'Car': 'Машина', 'Peace': 'Мир', 'Green': 'Зелёный', 'Hello': 'Привет', 'Cup': 'Чашка',
         'Cat': 'Кошка', 'Water': 'Вода', 'Sun': 'Солнце', 'Light': 'Свет', 'Word': 'Слово'}


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


def check_user(chat_id, get_id=None):
    """Проверяет chat_id на наличие в БД,
     в случае наличия - возвращает True
     При значении параметра get_id равном True
     возвращает id пользователя в таблице USERS БД
     """
    with conn.cursor() as cur:
        cur.execute("""
        SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s
        """, [chat_id])
        result = cur.fetchone()
        if result:
            if get_id:
                print(result[0])
                return
            else:
                return True
        else:
            return False


def add_user_to_db(chat_id):
    """
    Добавляем chat_id пользователя в БД
    """
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


def add_word(word, translation, chat_id):
    """
    Добавляем слова и их перевод в БД, связываем слова и пользователя
    """
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO WORDS(WORD, TRANSLATION) VALUES
            (%s, %s) RETURNING word_id
            """, (word, translation))
            word_id = cur.fetchone()  # Получаем id слова из таблицы word

            cur.execute("""
            SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s 
            """, [chat_id])
            user_id = cur.fetchone()[0]  # Получаем id пользователя из таблицы words

            cur.execute("""
            INSERT INTO USERS_WORDS(USER_ID,WORD_ID) VALUES
            (%s,%s)
            """, (user_id, word_id))  # Связываем добавляемое слово и пользователя

            conn.commit()

        except:
            print(f'[INFO] Ошибка добавления слова в БД')


def get_words(chat_id):
    """
    Получаем 4 случайных пары слов и переводов для заданного пользователя
    """
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
    """
    Возвращает количество слов, которые пользователь учит в данный момент
    """
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
                        FROM USERS_WORDS
                        WHERE USER_ID=%s;
                        """, [user_id])
            words_count = cur.fetchone()[0]
            return words_count
        except:
            print(f'[INFO] Ошибка БД Postgres')


def del_word(word, chat_id):
    """
    Удаляем слово для текущего пользователя
    """
    with conn.cursor() as cur:
        try:
            cur.execute("""
                       SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s
                       """, [chat_id])
            user_id = cur.fetchone()[0]  # Получаем id пользователя из таблицы words
            print(f'User id is: {user_id}')
        except:
            print(f'[INFO] Пользователь {chat_id} отсутствует в БД')
        try:
            cur.execute("""
                        SELECT WORDS.WORD_ID 
                        FROM USERS_WORDS ,WORDS
                        WHERE USERS_WORDS.WORD_ID = WORDS.WORD_ID
                        AND WORDS.TRANSLATION = %s
                        AND USER_ID = %s
                       """, (word, user_id))
            word_id = cur.fetchone()[0]  # Получаем id слова из таблицы words
            print(f'{word} id is {word_id}')
        except:
            print(f'[INFO] Слово {word} отсутствует в БД')

        try:
            cur.execute("""
                DELETE FROM USERS_WORDS
                WHERE user_id=%s AND word_id=%s
            """, (user_id, word_id))  # Удаляем связь пользователя и слова
            print(f'{user_id} {word_id}')
        except:
            print(f'[INFO] Ошибка БД Postgres')

        try:
            cur.execute("""
            DELETE FROM WORDS WHERE TRANSLATION=%s AND WORD_ID=%s;
            """, (word, word_id))
            conn.commit()
        except:
            print(f'[INFO] невозможно удалить слово "{word}" из БД, возможно связано с другими пользователями')


if __name__ == '__main__':
    create_tables()
    # a = get_words_count(5306142)
    # print(a)
    #del_word('Чашка', 5306142)
    #word = 'Дом'
    # with conn.cursor() as cur:
    #     cur.execute("""
    #     SELECT WORD_ID FROM WORDS WHERE TRANSLATION='дом'
    #     """, [word])
    #     word_id = cur.fetchall()
    #     print(word_id)
    # print(get_words_count(5306142))
    # check_user(5306142, get_id=True)
    pass
