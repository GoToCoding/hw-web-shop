class Product:
    def __init__(self, name, code, category, is_deleted=False):
        self.name = name
        self.code = code
        self.category = category
        self.is_deleted = is_deleted

    def to_dict(self):
        res = {
            'name': self.name,
            'code': self.code,
            'category': self.category,
        }
        if self.is_deleted:
            res['is_deleted'] = True
        return res
