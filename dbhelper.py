import psycopg2
import models as mod
import random
import string

class DBHelper:
    def __init__(self, dbname="chatbotDB"):
        self.conn = psycopg2.connect(dbname=dbname, user="postgres", password="040316",
                                     host='localhost',port="5432")
        self.cursor = self.conn.cursor()



    # def setup(self):
    #     stmt = "CREATE TABLE IF NOT EXISTS items (questions TEXT, answers TEXT,  owner TEXT)"
    #     itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (questions ASC)"
    #     ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
    #     self.cursor.execute(stmt)
    #     self.cursor.execute(itemidx)
    #     self.cursor.execute(ownidx)
    #     self.conn.commit()
    #
    # def add_questions(self, question_text, owner):
    #     stmt = "INSERT INTO items (question, owner) VALUES (%s, %s)"
    #     args = (question_text,str(owner))
    #     self.cursor.execute(stmt, args)
    #     self.conn.commit()

    def add_answer(self,owner, question_id):
            stmt = "INSERT INTO chatbot_answers (owner,question_id) VALUES (%s, %s)"
            args = (str(owner), question_id)
            self.cursor.execute(stmt, args)
            self.conn.commit()

    def update_answers(self,owner, **kwargs):
        for k, v in kwargs.items():
            if k in ["question_id", "correct_answers_num","wrong_answers_num", "correct_variant", "subject"]:
                stmt = f"UPDATE chatbot_answers SET {k}=(%s) WHERE owner = (%s)"
                args = (v, str(owner))
            else:
                break
            self.cursor.execute(stmt, args)
            self.conn.commit()

    def delete_answer(self, owner):
        stmt = f"DELETE FROM chatbot_answers WHERE owner = {owner}"
        args = (str(owner))
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def get_question(self, id):
        stmt = "SELECT * FROM chatbot_questions  WHERE id = (%s)"
        args = (str(id),)
        self.cursor.execute(stmt, args)
        rows = self.cursor.fetchall()
        prefix =[""]
        return [mod.Questions(x[0],x[1],x[2],x[3],
                              random.sample(x[3:], len(x[3:]))) for x in rows][0]

    def get_question_by_id(self, question_id):
        stmt = "SELECT * FROM chatbot_questions  WHERE id = (%s)"
        args = (str(question_id),)
        self.cursor.execute(stmt, args)
        rows = self.cursor.fetchall()
        return [mod.Questions(x[0],x[1],x[2],random.sample(x[2:-1], len(x[2:-1])),x[-1]) for x in rows][0]

    def get_next_question_num_by_subj(self,subject, previous_qst_id=0):
        stmt = "SELECT MIN(id) FROM chatbot_questions  WHERE subject = (%s) AND id > (%s)"
        args = (str(subject),previous_qst_id)
        self.cursor.execute(stmt, args)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_subjects(self):
        stmt = "SELECT DISTINCT subject FROM chatbot_questions"
        args = (str(id),)
        self.cursor.execute(stmt, args)
        subjects = self.cursor.fetchall()
        return [subject[0] for subject in subjects]



    def get_answer(self, owner):
        stmt = f"SELECT *  FROM chatbot_answers  WHERE owner = {owner}"
        args = (str(owner))
        self.cursor.execute(stmt, args)
        answer = self.cursor.fetchall()
        return [mod.Answer(x[0], x[1], x[2], x[3], x[4], x[5]) for x in answer][0]

    def get_number_of_questions(self, table="chatbot_questions"):
        stmt = f"SELECT id FROM {table}  ORDER BY id DESC LIMIT 1"
        args = (str(table))
        self.cursor.execute(stmt, args)
        num = self.cursor.fetchall()
        return num[0][0]

    def get_users(self):
        stmt = f"SELECT * FROM users "
        # args = (str(id))
        self.cursor.execute(stmt, "")
        users = self.cursor.fetchall()
        return {id:perm  for (id, perm) in users  }

    def close_connection(self):
        self.conn.close()

def main():
    db = DBHelper("chatbotDB")
    res = db.update_answers(3,question_id=4, correct_answers_num = 5, wrong_answers_num = 6 )
    # "correct_answers_num","wrong_answers_num"
    res = db.get_question_by_id(4)
    # db.add_answer(7,1)
    # db.update_answers(7,2)
    # res = db.get_user(5)
    # res = db.get_question(1)
    # print(res)
    # db.setup()
    # db.add_item("some_text")
    # db.add_item("some_text3")
    # db.add_item("some_text4")
    # res = db.get_user()
    # print(res)
    # res = db.get_questions(1)
    # print(res)
    # res = db.get_questions_by_subject("Words")
    db.close_connection()

if __name__ == "__main__":
    main()


