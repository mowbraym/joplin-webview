CREATE VIEW myfolder_titles
AS
SELECT folders.id,
	IfNull(folders2.title, '') || IfNull(folders1.title, '') || folders.title AS full_title,
	folders.title,
	CASE 
		WHEN folders1.title IS NULL
			AND folders2.title IS NULL
			THEN 1
		WHEN folders2.title IS NULL
			THEN 2
		ELSE 3
		END AS title_level,
	CASE 
		WHEN folders1.title IS NULL
			AND folders2.title IS NULL
			THEN folders.title
		WHEN folders2.title IS NULL
			THEN folders1.title || ' | ' || folders.title
		ELSE folders2.title || ' | ' || folders1.title || ' | ' || folders.title
		END AS breadcrumb_title,
	replace(hex(zeroblob(CASE 
					WHEN folders1.title IS NULL
						AND folders2.title IS NULL
						THEN 0
					WHEN folders2.title IS NULL
						THEN 1
					ELSE 2
					END)), '00', '    ') || folders.title AS display_title
FROM folders
LEFT JOIN folders folders1
	ON folders1.id = folders.parent_id
LEFT JOIN folders folders2
	ON folders2.id = folders1.parent_id
ORDER BY full_title