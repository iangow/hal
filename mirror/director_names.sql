WITH l AS (SELECT * FROM equilar_proxies WHERE file_name = '%s'),
     r AS (SELECT * FROM director)
SELECT director FROM l, r WHERE l.equilar_id=director.equilar_id(director_id) AND l.fy_end=r.fy_end;
