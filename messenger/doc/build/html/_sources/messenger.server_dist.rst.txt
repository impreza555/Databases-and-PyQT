server\_dist - серверная часть дистрибутива.
============================================

    Клиентское приложение для обмена сообщениями. Серверная часть. Поддерживает
    отправку сообщений пользователям которые находятся в сети, сообщения шифруются
    с помощью алгоритма RSA с длинной ключа 2048 bit.

    Поддерживает аргументы командной строки:

    ``python run_server.py {ip адрес прослушивания} {порт} -n или --no_gui {без графической оболочки}``

    1. {ip адрес прослушивания} - адрес с которых будут приниматься сообщения. По умолчанию с любых.
    2. {порт} - порт по которому принимаются подключения
    3. --no_gui - запуск сервера без графической оболочки.

    Все опции командной строки являются необязательными.

    Примеры использования:

    * ``python run_server.py``

    *Запуск приложения с параметрами по умолчанию.*

    * ``python run_server.py ip_address some_port``

    *Запуск приложения с указанием прослушивать ip_address:port*

    * ``python run_server.py --no_gui``

    *Запуск приложения без графического интерфейса*

Subpackages
-----------

    * server - ядро приложения, а так же графический интерфейс.
    * common - общие файлы.
    * log - логирование приложения.
    * tests - unit-тесты.

.. toctree::
   :maxdepth: 4

   messenger.server_dist.common
   messenger.server_dist.log
   messenger.server_dist.server
   messenger.server_dist.tests

Submodules
----------

run\_server.py
--------------

    Запускает серверную часть приложения.

.. automodule:: messenger.server_dist.run_server
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: messenger.server_dist
   :members:
   :undoc-members:
   :show-inheritance:
