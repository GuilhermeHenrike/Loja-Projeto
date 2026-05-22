class User:
    def __init__(self, id, name, email, password_hash, user_type='cliente'):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'user_type': self.user_type
        }