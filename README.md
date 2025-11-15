\# AgroScout



\## Структура проекта



AgroScout/

│

├─ src/

│   ├─ db/

│   │   ├─ sqlitedb/

│   │   │   ├─ sqlitedb.cpp        # Реализация методов работы с SQLite

│   │   │   ├─ sqlitedb.h          # Заголовочный файл с объявлениями классов и методов

│   ├─ sql/

│   │   └─ schema.sql               # Схема базы данных (SQL скрипт)

│   └─ tests/

│       └─ sqlitedbtest/

│           ├─ dbtests.cpp         # Юнит-тесты для SQLiteDb

│           └─ dbtests.h           # Заголовочный файл тестов

│

├─ include/

│   ├─ dbinterface/

│   │   └─ dbinterface.h           # Интерфейс работы с БД

│   ├─ config/

│   │   └─ config.h                # Конфигурационные параметры

│   └─ status/

│       ├─ statuscodes.h           # Коды статусов для работы с БД

│       ├─ statusmapper.h          # Функции для перевода кода в сообщение

│       └─ logmessages.h           # Шаблоны и константы сообщений логирования

│

├─ CMakeLists.txt                  # CMake конфигурация проекта

└─ README.md                        # Документация и описание проекта



