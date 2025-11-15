#include "dbtests.h"
#include "sqlitedb.h"
#include <QtTest>

// ============================================
// Тестовые данные для DbTests
// ============================================

// Клиенты:
//   "Test Client42"   - основной клиент для CRUD тестов
//   "MLTestClient"    - клиент для ML теста

// Спецификации:
//   "v1.1"           - базовая спецификация для обычных роботов
//   "MLTestSpec"     - спецификация для ML теста

// Роботы:
//   "TestRobot"      - робот для обычных тестов
//   "MLTestRobot"    - робот для ML теста

// Сессии:
//   Статус сессии: "active"

// ML результаты:
//   module_name = "MLModule"
//   results_json = "{\"result\":42}"
//   confidence = 0.95

// SensorData:
//   JSON-данные сенсоров могут быть любыми, но не пустыми для теста

// Recommendations:
//   Приоритет: "medium"
//   Статус: "new"
//   Target: "operator" (для кого предназначена рекомендация)


// =====================
// Инициализация и очистка
// =====================
void DbTests::initTestCase()
{
    // Подключение к тестовой базе данных
    QVERIFY(db.connect(dbFile) == StatusCode::SUCCESS);
}

void DbTests::cleanupTestCase()
{
    // Отключение от базы после всех тестов
    db.disconnect();
}

// =====================
// CRUD Клиентов
// =====================

void DbTests::testAddClient()
{
    // Проверка добавления обычного клиента
    QCOMPARE(db.addClient("Test Client"), StatusCode::SUCCESS);
}

void DbTests::testAddClientEmptyName()
{
    // Проверка добавления клиента с пустым именем
    // Должен вернуть ошибку SQL запроса
    QCOMPARE(db.addClient(""), StatusCode::DB_QUERY_FAILED);
}

void DbTests::testSelectClient()
{
    // Проверка выборки клиента по имени
    auto result = db.executeSQL("SELECT * FROM Clients WHERE name='Test Client';");
    QCOMPARE(result.code, StatusCode::SUCCESS);

    // Проверка, что хотя бы одна запись найдена
    auto rows = result.data.value<QVector<QVariantMap>>();
    QVERIFY(!rows.isEmpty());
}

void DbTests::testUpdateClient()
{
    // Добавляем клиента для теста
    QCOMPARE(db.addClient("ClientToUpdate"), StatusCode::SUCCESS);

    // Обновляем имя напрямую через SQL
    auto updateResult = db.executeSQL(
        "UPDATE Clients SET name='UpdatedClient' WHERE name='ClientToUpdate';"
        );
    QCOMPARE(updateResult.code, StatusCode::SUCCESS);

    // Проверяем, что новое имя сохранилось
    auto selectResult = db.executeSQL(
        "SELECT * FROM Clients WHERE name='UpdatedClient';"
        );
    QVERIFY(!selectResult.data.value<QVector<QVariantMap>>().isEmpty());
}


void DbTests::testDeleteClient()
{
    // Удаление клиента и проверка статуса
    QCOMPARE(db.executeSQL("DELETE FROM Clients WHERE name='UpdatedClient';").code, StatusCode::SUCCESS);

    // Проверка, что запись действительно удалена
    auto select = db.executeSQL("SELECT * FROM Clients WHERE name='UpdatedClient';");
    auto rows = select.data.value<QVector<QVariantMap>>();
    QCOMPARE(rows.size(), 0);
}

// =====================
// Спецификации и роботы
// =====================
void DbTests::testAddSpecification()
{
    // Добавление новой спецификации
    QCOMPARE(db.addSpecification("v1.1"), StatusCode::SUCCESS);
}

void DbTests::testAddRobot()
{
    // Получаем id ранее созданной спецификации
    auto select = db.executeSQL("SELECT id FROM Specifications WHERE version='v1.1';");
    int specId = select.data.value<QVector<QVariantMap>>().first()["id"].toInt();

    // Добавление робота, привязанного к спецификации
    QCOMPARE(db.addRobot("TestRobot", specId, "Описание робота"), StatusCode::SUCCESS);
}

// =====================
// ML сессии и результаты
// =====================
void DbTests::testAddMLResult()
{
    // Создаём временного клиента для ML-теста
    QCOMPARE(db.addClient("MLTestClient"), StatusCode::SUCCESS);

    // Получаем ID клиента
    auto selectClient = db.executeSQL("SELECT id FROM Clients WHERE name='MLTestClient';");
    int clientId = selectClient.data.value<QVector<QVariantMap>>().first()["id"].toInt();

    // Создаём спецификацию и робота для ML-теста
    QCOMPARE(db.addSpecification("MLTestSpec"), StatusCode::SUCCESS);
    auto selectSpec = db.executeSQL("SELECT id FROM Specifications WHERE version='MLTestSpec';");
    int specId = selectSpec.data.value<QVector<QVariantMap>>().first()["id"].toInt();

    QCOMPARE(db.addRobot("MLTestRobot", specId, "Для ML теста"), StatusCode::SUCCESS);
    auto selectRobot = db.executeSQL("SELECT id FROM Robots WHERE model='MLTestRobot';");
    int robotId = selectRobot.data.value<QVector<QVariantMap>>().first()["id"].toInt();

    // Создаём сессию
    QCOMPARE(db.addSession(clientId, robotId, specId, -1, "active"), StatusCode::SUCCESS);

    // Получаем ID созданной сессии
    auto selectSession = db.executeSQL("SELECT id FROM Sessions ORDER BY id DESC LIMIT 1;");
    int sessionId = selectSession.data.value<QVector<QVariantMap>>().first()["id"].toInt();

    // Добавляем ML результат и проверяем статус
    QCOMPARE(db.addMLResult(sessionId, "MLModule", "{\"result\":42}", 0.95), StatusCode::SUCCESS);
}

// =====================
// Ошибки подключения и SQL
// =====================
void DbTests::testInvalidSQL()
{
    // Выполнение некорректного SQL-запроса
    auto result = db.executeSQL("SELECT * FROM NonExistingTable;");
    QCOMPARE(result.code, StatusCode::DB_QUERY_FAILED);
}



QTEST_MAIN(DbTests)
#include "dbtests.h"
