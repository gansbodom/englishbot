import requests


def get_example(word):
    """
    Принимает английское слово и пытается найти для него
    пример использования на сервисе dictionaryapi
    """
    request = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    data = request.json()
    try:
        for mean in data[0]['meanings']:
            definition = mean['definitions'][0]
            if definition.get('example'):
                example = definition['example']
                return example
    except:
        print('[INFO] Не могу получить пример использования слова')
        reply = 'Для данного слова не удалось найти пример😢'
        return reply
