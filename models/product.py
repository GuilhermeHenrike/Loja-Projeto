# Entidade Produto e seus atributos

class Product:
    def __init__(self, id, user_id, name, description, price, created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.price = price
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0, # Garante que vira numero no Flutter
            'created_at': self.created_at
        }