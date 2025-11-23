#ifndef ROUTES_SETUP_H
#define ROUTES_SETUP_H

#include "redismanager.h"
#include "sqlitedb.h"

// Главная функция, которая настраивает маршруты Redis для разных типов сообщений.
// manager — объект RedisManager, db — база данных SQLiteDb
void setupRoutes(RedisManager &manager, SQLiteDb &db);

#endif // ROUTES_SETUP_H
