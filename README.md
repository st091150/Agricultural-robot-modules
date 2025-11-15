# AgroScout

## Структура проекта

- **src/** - исходные коды
  - **db/**
    - **sqlitedb/**
      - `sqlitedb.cpp` - реализация методов работы с SQLite
      - `sqlitedb.h` - объявления классов и методов
  - **sql/**
    - `schema.sql` - SQL-скрипт для создания схемы базы данных
  - **tests/**
    - **sqlitedbtest/**
      - `dbtests.cpp` - юнит-тесты для SQLiteDb
      - `dbtests.h` - заголовочный файл тестов

- **include/** - заголовочные файлы и интерфейсы
  - **dbinterface/**
    - `dbinterface.h` - интерфейс работы с БД
  - **config/**
    - `config.h` - конфигурационные параметры
  - **status/**
    - `statuscodes.h` - коды статусов для работы с БД
    - `statusmapper.h` - функции для перевода кода в сообщение
    - `logmessages.h` - шаблоны и константы сообщений логирования

- `CMakeLists.txt` - конфигурация сборки CMake
- `README.md` - документация проекта
