class Task:
    """
    Represents a task in the system.
    """
    def __init__(self, id=None, title="", description="", category="Genel", due_date=None, priority="Orta", status="Bekliyor", user_name="genel"):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.user_name = user_name  # Yeni ekledik

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "user_name": self.user_name
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
            status=row[6],
            user_name=row[7] if len(row) > 7 else "genel" # Veritabanındaki yeni sütunu oku
        )


class Note:
    """
    Represents a personal note in the system.
    """
    def __init__(self, id=None, title="", content="", category="Genel", created_at=None, user_name="genel"):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at
        self.user_name = user_name  # Yeni ekledik

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
            "user_name": self.user_name
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
            created_at=row[4],
            user_name=row[5] if len(row) > 5 else "genel" # Veritabanındaki yeni sütunu oku
        )