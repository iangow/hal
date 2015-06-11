WITH l AS (SELECT * FROM director.equilar_proxies WHERE file_name = '%s'),
     r AS (SELECT * FROM director.director)
SELECT director FROM l, r WHERE l.equilar_id=equilar_id(director_id) AND l.fy_end=r.fy_end;
