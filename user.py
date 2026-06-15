class User:
    def __init__(self, pk, username, password, name, is_staff=False):
        self.pk = pk
        self.username = username
        self.password = password
        self.name = name
        self.is_staff = is_staff
        self.work_list = []

    def __str__(self):
        return self.username

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            pk=data['id'],
            username=data['username'],
            password=data['password'],
            name=' '.join([data['first_name'], data['last_name']]),
            is_staff=data['is_staff']
        )

    def add_work(self, work):
        self.work_list.append(work)
