class DialogueManager:
    def __init__(self, questions: list):
        self.questions = questions
        self.current_index = 0
        self.answers = []

    def get_next_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def record_answer(self, answer: str):
        self.answers.append(answer)
        self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.questions)

    def get_transcript(self):
        return [
            {"question": self.questions[i], "answer": self.answers[i] if i < len(self.answers) else None}
            for i in range(len(self.questions))
        ]
