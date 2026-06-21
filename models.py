class Task:
    """
    Represents a task in the system.
    """
    def __init__(self, id=None, title="", description="", category="Genel", due_date=None, priority="Orta", status="Bekliyor"):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.due_date = due_date  # date object or string 'YYYY-MM-DD'
        self.priority = priority  # 'Düşük', 'Orta', 'Yüksek'
        self.status = status      # 'Bekliyor', 'Tamamlandı'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status
        }

    @staticmethod
    def from_row(row):
        """
        Creates a Task object from a SQLite row tuple.
        """
        if not row:
            return None
        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            category=row[3],
            due_date=row[4],
            priority=row[5],
            status=row[6]
        )


class Note:
    """
    Represents a personal note in the system.
    """
    def __init__(self, id=None, title="", content="", category="Genel", created_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at  # datetime string

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at
        }

    @staticmethod
    def from_row(row):
        """
        Creates a Note object from a SQLite row tuple.
        """
        if not row:
            return None
        return Note(
            id=row[0],
            title=row[1],
            content=row[2],
            category=row[3],
            created_at=row[4]
        )