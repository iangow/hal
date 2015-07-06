WITH ids AS (
    SELECT regexp_replace(director_id, '\..*\.', '.') as director_id FROM crosswalk
    WHERE folder='{{ bio.folder }}' AND director='{{ bio.director_name }}'
),
x AS (
    SELECT regexp_replace(b, '\..*$', '')::integer AS equilar_id
    FROM matched_director_ids JOIN ids
    ON a=director_id
)
SELECT company -- , x.equilar_id
    FROM companies JOIN x
    ON companies.equilar_id=x.equilar_id;
