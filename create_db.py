import psycopg2

chat_number=99999

def create_tables(conn):
    """Создаём таблицы БД, добавлена проверка
     слов и их переводов на уникальность"""

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS USERS(
        USER_ID SERIAL PRIMARY KEY,
        USER_NUMBER INTEGER NOT NULL
        );
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


def add_basic_words(conn,word, translation, chat_number):
    """Добавляем слова и их перевод в БД"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO WORDS(WORD, TRANSLATION) VALUES
            (%s, %s)
            """, (word, translation))

            conn.commit()

        except:
            print('words alerady added')

    with conn.cursor() as cur:
        try:
            INSERT INTO USERS_WORDS

def db_init():
    with psycopg2.connect(database="englishbot", user="postgres", password="postgres") as conn:
        create_tables(conn)
        add_words(conn, chat_number)
    conn.close()


if __name__ == "__main__":
    db_init()