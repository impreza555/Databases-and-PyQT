import os
from subprocess import Popen, CREATE_NEW_CONSOLE

process = []
path = os.path.abspath(os.path.join(os.path.dirname(__file__), './client/'))

while True:
    action = input('Выберите действие: q - выход , s - запустить сервер, '
                   'k - запустить клиенты x - закрыть все окна:')
    if action == 'q':
        break
    elif action == 's':
        process.append(Popen('python server.py',
                             creationflags=CREATE_NEW_CONSOLE))
    elif action == 'k':
        print('Убедитесь, что на сервере зарегистрировано необходимое'
              ' количество клиентов с паролем 123456.')
        print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        for i in range(clients_count):
            process.append(Popen(f'python client_main.py -n test{i + 1} -p 123456', cwd=path,
                                 creationflags=CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            process.pop().kill()
