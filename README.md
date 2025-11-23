# AgroScout

## Структура проекта

- **src/** - исходные коды
  - **db/**
    - **sqlitedb/**
      - `sqlitedb.cpp` - реализация методов работы с SQLite
      - `sqlitedb.h` - объявления классов и методов
  - **sql/**
    - `schema.sql` - SQL-скрипт для создания схемы базы данных
    - `db.png`- диаграмма структуры базы данных
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
  - `datatypes.h` — унифицированные структуры для хранения и парсинга информации
- **redis/**
  - `redismanager.h`- объявление класса RedisManager для подписки на каналы и обработки сообщений
  - `redismanager.cpp`- реализация методов RedisManager
  - `routessetup.h`- объявление функции setupRoutes для регистрации обработчиков сообщений
  - `routessetup.cpp`- реализация setupRoutes и шаблонов обработчиков
  
- `CMakeLists.txt` - конфигурация сборки CMake
- `README.md` - документация проекта
