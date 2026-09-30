CREATE TABLE IF NOT EXISTS PROGRAMMES (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
    
);

CREATE TABLE IF NOT EXISTS STUDENTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    programme_id INTEGER NOT NULL,
    FOREIGN KEY (programme_id) REFERENCES PROGRAMMES(id)
   
);
CREATE TABLE IF NOT EXISTS COURS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
   
);

CREATE TABLE IF NOT EXISTS INSCRIPTIONS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    note REAL,
    UNIQUE (student_id, cours_id),
    FOREIGN KEY (student_id) REFERENCES STUDENTS(id),
    FOREIGN KEY (cours_id) REFERENCES COURS(id)
);


INSERT INTO PROGRAMMES (id, name) VALUES (1, 'Computer Science');
INSERT INTO PROGRAMMES (id, name) VALUES (2, 'Intelligence Artificielle');

INSERT INTO COURS (id, code, name) VALUES (1, 'AI101', 'Introduction to Artificial Intelligence');
INSERT INTO COURS (id, code, name) VALUES (2, 'AI102', 'Advanced Artificial Intelligence');

INSERT INTO STUDENTS (id, name, email, programme_id) VALUES (1, 'John Doe', 'john.doe@example.com', 1);
INSERT INTO STUDENTS (id, name, email, programme_id) VALUES (2, 'Jane Doe', 'jane.doe@example.com', 2);

INSERT INTO INSCRIPTIONS (student_id, cours_id, note) VALUES (1, 1, 85);
INSERT INTO INSCRIPTIONS (student_id, cours_id, note) VALUES (2, 2, 90);