#ifndef DBTESTS_H
#define DBTESTS_H

#include <QObject>
#include <QString>

#include "sqlitedb.h"
#include "config.h"


class DbTests : public QObject
{
    Q_OBJECT

private:
    SQLiteDb db;                         // Объект базы данных
    const QString dbFile = Config::DB_TEST_FILE_PATH; // Путь к тестовой базе данных

private slots:
    // =====================
    // Инициализация и очистка
    // =====================
    void initTestCase();   // Подключение к базе перед тестами
    void cleanupTestCase();// Отключение от базы после всех тестов

    // =====================
    // CRUD Клиентов
    // =====================
    void testAddClient();         // Проверка добавления обычного клиента
    void testAddClientEmptyName();// Проверка добавления клиента с пустым именем
    void testSelectClient();      // Проверка выборки клиента по имени
    void testUpdateClient();
    void testDeleteClient();      // Проверка удаления клиента

    // =====================
    // Спецификации и роботы
    // =====================
    void testAddSpecification();  // Проверка добавления спецификации
    void testAddRobot();          // Проверка добавления робота, связанного с спецификацией

    // =====================
    // ML сессии и результаты
    // =====================
    void testAddMLResult();       // Проверка добавления ML результатов и связанных данных

    // =====================
    // Ошибки подключения и SQL
    // =====================
    void testInvalidSQL();        // Выполнение некорректного SQL-запроса

};

#endif // DBTESTS_H
