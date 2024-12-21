CREATE TABLE company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(100),
    contact_form_url VARCHAR(255),
    linkedin_profile VARCHAR(255),
    twitter_handle VARCHAR(100),
    telegram_handle VARCHAR(100),
    live_chat_url VARCHAR(255)
);

CREATE TABLE contact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id)
);
