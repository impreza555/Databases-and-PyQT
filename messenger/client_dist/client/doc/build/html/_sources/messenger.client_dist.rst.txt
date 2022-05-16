client\_dist - клиентская часть дистрибутива.
=============================================

    Клиентское приложение для обмена сообщениями. Поддерживает
    отправку сообщений пользователям которые находятся в сети, сообщения шифруются
    с помощью алгоритма RSA с длинной ключа 2048 bit.

    Поддерживает аргументы командной строки:

    ``python run_client.py {имя сервера} {порт} -n или --name {имя пользователя} -p или -password {пароль}``

    1. {имя сервера} - адрес сервера сообщений.
    2. {порт} - порт по которому принимаются подключения
    3. -n или --name - имя пользователя с которым произойдёт вход в систему.
    4. -p или --password - пароль пользователя.

    Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо использовать в паре.

    Примеры использования:

    * ``python run_client.py``

    *Запуск приложения с параметрами по умолчанию.*

    * ``python run_client.py ip_address some_port``

    *Запуск приложения с указанием подключаться к серверу по адресу ip_address:port*

    * ``python -n test1 -p 123``

    *Запуск приложения с пользователем test1 и паролем 123*

    * ``python run_client.py ip_address some_port -n test1 -p 123``

    *Запуск приложения с пользователем test1 и паролем 123 и указанием подключаться к серверу по адресу ip_address:port*

Subpackages
-----------

    * client - ядро приложения, а так же графический интерфейс.
    * common - общие файлы.
    * log - логирование приложения.
    * tests - unit-тесты.

.. toctree::
   :maxdepth: 4

   messenger.client_dist.client
   messenger.client_dist.common
   messenger.client_dist.log
   messenger.client_dist.tests

Submodules
----------

run\_client.py
--------------

    Файл запуска клиента.

.. automodule:: messenger.client_dist.run_client
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: messenger.client_dist
   :members:
   :undoc-members:
   :show-inheritance:
