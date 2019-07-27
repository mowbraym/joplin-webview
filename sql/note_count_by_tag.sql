CREATE VIEW note_count_by_tag
AS
SELECT tags.id AS tag_id,
	tags.title AS tag_title,
	Count(note_tags.id) AS rec_count
FROM tags,
	note_tags
WHERE note_tags.tag_id = tags.id
GROUP BY tags.id,
	tags.title