from . import db

class Contest(db.Model):
    __tablename__ = 'contests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    length = db.Column(db.String(128))
    time = db.Column(db.String(128))
    rating = db.Column(db.String(128))
    platform = db.Column(db.String(128))
    update_time = db.Column(db.String(128))
    date = db.Column(db.String(128))

    def serialize(self):
        return {
            "title": self.title,
            "length": self.length,
            "time": self.time,
            "rating": self.rating,
            "platform": self.platform,
            "update_time": self.update_time,
            "id": self.id,
            "date": self.date,
        }
