class InterviewFlow:
    def __init__(self):
        self.history = []
        self.current_question = None

    def set_question(self, q):
        self.current_question = q

    def update(self, answer):
        self.history.append({
            "question": self.current_question,
            "answer": answer
        })
