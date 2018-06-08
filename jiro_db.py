# from __future__ import absolute_import
# from __future__ import unicode_literals
# import mysql.connector
#
#
# class DB:
#     def __init__(self, user, password, database):
#         self.user = user
#         self.password = password
#         self.database = database
#         self._config = dict()
#         self._config["user"] = self.user
#         self._config["password"] = self.password
#         self._config["database"] = self.database
#         print("true")
#
#     def connect_db(self):
#         config = self._config
#
#         # DBに接続
#         cnx = mysql.connector.connect(**config)
#         cursor = cnx.cursor()
#         return cnx, cursor
#
#     def insert(self, query, query_value=None):
#         cnx, cursor = self.connect_db()
#         stmt = query
#         # "insert into jiro_copype (id, title, body) values (%s, %s, %s);"
#         cursor.execute(stmt, query_value)
#         cnx.commit()
#         cursor.close
#         cnx.close
#
#     def select(self, query, query_value=None):
#         cnx, cursor = self.connect_db()
#         stmt = query  # sql文の作成。%sにはdesign_idを入れる
#         cursor.execute(stmt, query_value)  # sqlの実行。
#         cursor.close
#         cnx.close
#
#         return cursor.fetchall()
#
#
# if __name__ == "__main__":
#     jiro_db = DB("root", "", "jirokkason")
#     data = jiro_db.select("select * from jiro_copype")
#     print(data)