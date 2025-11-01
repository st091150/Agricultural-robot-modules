-- Таблица клиентов
CREATE TABLE IF NOT EXISTS Clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ip_address TEXT,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица роботов
CREATE TABLE IF NOT EXISTS Robots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    spec_id INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(spec_id) REFERENCES Specifications(id)
);

-- Таблица полей
CREATE TABLE IF NOT EXISTS Fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    boundary_json TEXT,
    crop_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица спецификаций
CREATE TABLE IF NOT EXISTS Specifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT DEFAULT 'v1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица связи спецификаций и сенсоров
CREATE TABLE IF NOT EXISTS specSens (
    specification_id INTEGER NOT NULL,
    sensor_spec_id INTEGER NOT NULL,
    PRIMARY KEY(specification_id, sensor_spec_id),
    FOREIGN KEY(specification_id) REFERENCES Specifications(id),
    FOREIGN KEY(sensor_spec_id) REFERENCES Sensor_specification(id)
);

-- Таблица сенсоров
CREATE TABLE IF NOT EXISTS Sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    model TEXT NOT NULL,
    mounted_position TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица сессий
CREATE TABLE IF NOT EXISTS Sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    spec_id INTEGER NOT NULL,
    robot_id INTEGER NOT NULL,
    field_id INTEGER,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active',
    FOREIGN KEY(client_id) REFERENCES Clients(id),
    FOREIGN KEY(spec_id) REFERENCES Specifications(id),
    FOREIGN KEY(robot_id) REFERENCES Robots(id),
    FOREIGN KEY(field_id) REFERENCES Fields(id)
);

-- Таблица данных с сенсоров
CREATE TABLE IF NOT EXISTS Sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_json TEXT NOT NULL,
    ML_result_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ML_result_id) REFERENCES ML_results(id)
);

-- Таблица ML результатов
CREATE TABLE IF NOT EXISTS ML_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    module_name TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_json TEXT NOT NULL,
    confidence REAL,
    FOREIGN KEY(session_id) REFERENCES Sessions(id)
);

-- Таблица маршрутов
CREATE TABLE IF NOT EXISTS Routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    processing_time DATE NOT NULL,
    total_distance REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(field_id) REFERENCES Fields(id)
);

-- Таблица секторов
CREATE TABLE IF NOT EXISTS Sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    execution_id INTEGER NOT NULL,
    point_start_id INTEGER NOT NULL,
    point_end_id INTEGER NOT NULL,
    expected_distance REAL NOT NULL,
    actual_distance REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(route_id) REFERENCES Routes(id),
    FOREIGN KEY(execution_id) REFERENCES Sector_execution(id),
    FOREIGN KEY(point_start_id) REFERENCES Points(id),
    FOREIGN KEY(point_end_id) REFERENCES Points(id)
);

-- Таблица выполнения секторов
CREATE TABLE IF NOT EXISTS Sector_execution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT NOT NULL
);

-- Таблица команд секторов
CREATE TABLE IF NOT EXISTS Sector_exec_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_node_id INTEGER NOT NULL,
    commands_id INTEGER NOT NULL,
    sent_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT NOT NULL,
    FOREIGN KEY(sector_node_id) REFERENCES Sector_execution(id),
    FOREIGN KEY(commands_id) REFERENCES Commands(id)
);

-- Таблица команд
CREATE TABLE IF NOT EXISTS Commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    command_text TEXT NOT NULL
);

-- Таблица точек
CREATE TABLE IF NOT EXISTS Points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица наблюдений
CREATE TABLE IF NOT EXISTS Observation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_id INTEGER NOT NULL,
    point_id INTEGER NOT NULL,
    sensor_id INTEGER NOT NULL,
    data_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sector_id) REFERENCES Sectors(id),
    FOREIGN KEY(point_id) REFERENCES Points(id),
    FOREIGN KEY(sensor_id) REFERENCES Sensors(id),
    FOREIGN KEY(data_id) REFERENCES Sensor_data(id)
);

-- Таблица связи роботов и сенсоров
CREATE TABLE IF NOT EXISTS RobSens (
    robot_id INTEGER NOT NULL,
    sensor_id INTEGER NOT NULL,
    PRIMARY KEY(robot_id, sensor_id),
    FOREIGN KEY(robot_id) REFERENCES Robots(id),
    FOREIGN KEY(sensor_id) REFERENCES Sensors(id)
);

-- Таблица спецификаций сенсоров
CREATE TABLE IF NOT EXISTS Sensor_specification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    bytes INTEGER NOT NULL,
    FOREIGN KEY(sensor_id) REFERENCES Sensors(id)
);

-- Таблица рекомендаций
CREATE TABLE IF NOT EXISTS Recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ml_result_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'new',
    target TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ml_result_id) REFERENCES ML_results(id)
);
