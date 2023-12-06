import psycopg2
from psycopg2 import extras

conn = psycopg2.connect(database="englishbot", user="postgres", password="postgres")

words = {'NO': 'нет', 'YES': 'ДА'}


def create_tables(conn):
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
        WORD VARCHAR(80) UNIQUE NOT NULL,
        TRANSLATION VARCHAR(80) UNIQUE NOT NULL);
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS USERS_WORDS(
        USER_ID INTEGER NOT NULL REFERENCES USERS(USER_ID),
        WORD_ID INTEGER NOT NULL REFERENCES WORDS(WORD_ID),
        CONSTRAINT PK PRIMARY KEY (USER_ID, WORD_ID)
        );
        """)

        conn.commit()


def check_user(conn, chat_id):
    """Проверяет chat_id на наличие в БД,
     в случае наличия - возвращает True"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
            SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s
            """, [chat_id])
            id = cur.fetchone()[0]
            return
        except:
            pass

def add_user_to_db(conn, chat_id):
    """Добавляем chat_id пользователя в БД"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO USERS(USER_NUMBER) VALUES
            (%s)
            """, [chat_id])
            conn.commit()
        except:
            print('user alerady in db')


def add_word(conn,word,translation,chat_id):
    """Добавляем слова и их перевод в БД"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO WORDS(WORD, TRANSLATION) VALUES
            (%s, %s)
            """, (word, translation))

            cur.execute("""
            SELECT WORD_ID FROM WORDS WHERE WORD=%s 
            """, [word])
            word_id = cur.fetchone() #Получаем значение word_id
            print(f'{word} id is {word_id}')

            cur.execute("""
            SELECT USER_ID FROM USERS WHERE USER_NUMBER=%s
            """, [chat_id])
            user_id = cur.fetchone()[0]
            print(f'{chat_id} : {user_id}')

            cur.execute("""
            INSERT INTO USERS_WORDS(USER_ID,WORD_ID) VALUES
            (%s,%s)
            """, (user_id, word_id))

            conn.commit()

        except:
            print(f'Слово {word} уже добавлено')


def get_words(conn, chat_id):
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
            dct = [{k: v for k, v in record.items()} for record in rows] #создаём словарь
            return dct
        except:
            pass


if __name__ == '__main__':
    #create_tables(conn)
    #add_user_to_db(conn, 123459)
    #for w, t in words.items():
    #    add_word(conn, w, t)

    add_word(conn,'hв', 'ndddd', 5306142)

    #if check_user(conn, 123456):
    #    print('oloo')
    #a = check_user(conn, 123456, return_id=True)
    #print(a)
    #n = get_words(conn, 5306142)
    #print(n)
