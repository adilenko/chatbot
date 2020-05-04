from dataclasses import dataclass
from dataclasses import field
from typing import List


@dataclass
class Questions:
    id: int
    question: str
    correct_answer: str
    all_answers: list=field(default_factory=list)
    subject: str =field(default="")

@dataclass
class QuestionsList:
    questions: List[Questions]=field(default_factory=list)
    _cursor: int = field(default=-1)
    def get_question_by_id(self, id) -> Questions:
        return list(filter(lambda question: question.id == id, self.questions))[0]

    def __next__(self):
        if self._cursor + 1 >= len(self.questions):
            return None
        self._cursor += 1
        return self.questions[self._cursor]

    def __iter__(self):
        self._cursor = -1
        return self

    def reset(self):
        self._cursor = -1
        self.questions = []

@dataclass
class Answer:
    owner: int
    question_id: int
    correct_answers_num: int
    wrong_answers_num: int
    correct_variant: str
    subject: str


