DROP TABLE IF EXISTS experiment;

DROP TABLE IF EXISTS subject;

DROP TABLE IF EXISTS experiment_type;

DROP TABLE IF EXISTS species;

CREATE TABLE species (
    species_id INT GENERATED ALWAYS AS IDENTITY,
    species_name TEXT NOT NULL,
    scientific_name TEXT NOT NULL UNIQUE,
    is_predator BOOLEAN DEFAULT FALSE,
    breathes_air BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (species_id)
);

CREATE TABLE subject (
    subject_id INT GENERATED ALWAYS AS IDENTITY,
    subject_name TEXT NOT NULL,
    species_id INT NOT NULL,
    date_of_birth DATE NOT NULL,
    PRIMARY KEY (subject_id),
    FOREIGN KEY (species_id) REFERENCES species (species_id)
);

CREATE TABLE experiment_type (
    experiment_type_id INT GENERATED ALWAYS AS IDENTITY,
    type_name TEXT NOT NULL UNIQUE,
    max_score DECIMAL DEFAULT 100,
    PRIMARY KEY (experiment_type_id)
);

CREATE TABLE experiment (
    experiment_id INT GENERATED ALWAYS AS IDENTITY,
    subject_id INT NOT NULL,
    experiment_type_id INT NOT NULL,
    experiment_date DATE DEFAULT CURRENT_TIMESTAMP,
    score DECIMAL NOT NULL,
    PRIMARY KEY (experiment_id),
    FOREIGN KEY (subject_id) REFERENCES subject (subject_id),
    FOREIGN KEY (experiment_type_id) REFERENCES experiment_type (experiment_type_id)
);

INSERT INTO experiment_type
    (type_name, max_score)
VALUES
    ('intelligence', 30),
    ('obedience', 10),
    ('aggression', 10)
;

INSERT INTO species
    (species_name, scientific_name, is_predator, breathes_air)
VALUES
    ('Orca', 'orcinus orca', TRUE, TRUE),
    ('Dolphin', 'delphinus truncatus', TRUE, TRUE),
    ('Manatee', 'trichechus manatus', FALSE, TRUE),
    ('Tiger shark', 'Galeocerdo cuvier', TRUE, FALSE),
    ('Tuna', 'thunnus thynnus', FALSE, FALSE)
;

INSERT INTO subject
    (subject_name, species_id, date_of_birth)
VALUES 
    ('Flounder', 5, '2023-01-15'),
    ('Triton', 1, '2022-06-12'),
    ('Moana', 4, '2018-11-10'),
    ('Cindi', 1, '2014-02-03'),
    ('Poseidon', 4, '2021-08-08')
;

INSERT INTO experiment
    (subject_id, experiment_type_id, experiment_date, score)
VALUES
    (1, 1, '2024-01-06', 7),
    (2, 1, '2024-01-06', 27),
    (3, 1, '2024-01-06', 26),
    (4, 1, '2024-01-06', 29),
    (5, 1, '2024-01-06', 17),
    (4, 2, '2024-02-02', 2),
    (2, 2, '2024-02-08', 8),
    (2, 3, '2024-02-06', 1),
    (4, 3, '2024-02-10', 10),
    (5, 2, '2024-02-12', 6)
;
