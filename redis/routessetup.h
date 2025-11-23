#ifndef ROUTES_SETUP_H
#define ROUTES_SETUP_H

#include "redismanager.h"
#include "sqlitedb.h"

void setupRoutes(RedisManager &manager, SQLiteDb &db);

#endif // ROUTES_SETUP_H
