DROP TABLE IF EXISTS {{ table }};

CREATE TABLE {{ table }} (
    a text,
    b text
);

INSERT INTO matched_director_ids (a, b) VALUES
{{ values|safe }};
