CREATE VIEW note_count_by_folder
AS
SELECT notes.parent_id,
	folders.title,
	count(*) AS rec_count
FROM notes
INNER JOIN folders
	ON folders.id = notes.parent_id
GROUP BY notes.parent_id,
	folders.title