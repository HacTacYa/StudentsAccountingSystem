from flask_login import UserMixin


class UserLogin(UserMixin):

    def fromDB(self, user_id, db):
        self.__user = db.getUserbyid(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "Без имени"

    def getSurName(self):
        return self.__user['surname'] if self.__user else "Без фамилии"

    def getPatronymic(self):
        return self.__user['patronymic'] if self.__user else "Без отчества"

    def getavatar(self):
        return self.__user['avatar'] if self.__user else "Нет аватарки"

    def getEmail(self):
        return self.__user['email'] if self.__user else "Без email"

    def getrole(self):
        return self.__user['role']
