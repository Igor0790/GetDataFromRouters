# GetDataFromRouters

Скрипт предназначен для сбора данных с CLI роутеров через SSH.

В файле user_data указываются:

username: 'логин'

password: 'пароль'

command: 'show int desc,show ip int'

ip_list: '10.203.202.74,10.203.202.78'

command - перечисление команд через зяпятую. После запятой пробел не нужен.
ip_list - IP адреса роутеров, откуда собирать данные. После запятой пробел не нужен.

Это данные с помощью библиотеки PYYAML забираются в скрипт, передаются в функцию. Результат будет сохранен по пути:

../data/data_[ip]/data.json

Для каждого роутера должна быть своя папка. Папка "data" в корне скрипта должна быть создана заранее.

Внешние библиотеки:

paramiko
yaml

Организована многопоточность сбора. Максимум - 30 потоков.
