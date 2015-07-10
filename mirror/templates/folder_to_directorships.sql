WITH t1 AS
  (SELECT *
   FROM crosswalk
   WHERE folder = '{{ folder }}'),
     t2 AS
  (SELECT *
   FROM matched_director_ids
   JOIN t1 ON a=regexp_replace(director_id, '\..*\.', '.'))
SELECT {{ keys|join:" , "}}
FROM t2
JOIN companies ON regexp_replace(b, '\..*$', '')::integer=equilar_id;
