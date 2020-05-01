import requests
from random import sample, choice, shuffle
import html
from pprint import pprint
from time import sleep

class QuizGenerator:
    ''' Pulls a number of questions from the free open trivia database. Each question to printed to the user to
    decide whether to add it to the final quiz sheet by pressing 'y' or 'n'.
    The final output will be a .txt file written as follows:
    1. What programming language is this?
    ['foo', 'bar', 'python', 'world']
    Python'''

    final_quiz = []
    quiz_type = 0
    host = 'https://opentdb.com/api.php'
    cats = {"any":"Any Category",
            "9":"General Knowledge",
            "10":"Entertainment: Books",
            "11":"Entertainment: Film",
            "12":"Entertainment: Music",
            "13":"Entertainment: Musicals &amp; Theatres",
            "14":"Entertainment: Television",
            "15":"Entertainment: Video Games",
            "16":"Entertainment: Board Games",
            "17":"Science & Nature",
            "18":"Science: Computers",
            "19":"Science: Mathematics",
            "20":"Mythology",
            "21":"Sports",
            "22":"Geography",
            "23":"History",
            "24":"Politics",
            "25":"Art",
            "26":"Celebrities",
            "27":"Animals",
            "28":"Vehicles",
            "29":"Entertainment: Comics",
            "30":"Science: Gadgets",
            "31":"Entertainment: Japanese Anime & Manga",
            "32":"Entertainment: Cartoon &amp; Animations"}

    def __init__(self):
        self.quiz_len = int(input('how many questions would you like for your quiz? '))
        self.params = self.get_params()
        self.questions_json = self.get_questions()
        self.quiz_builder()
        self.write_quiz()

    def get_params(self):
        while self.quiz_type not in [1, 2]:
            self.quiz_type = int(input('please press 1 to create a random quiz or 2 to customise the quiz. '))

            if self.quiz_type == 1:
                self.selected_categories = choice(list(self.cats.keys()))
                return {"amount" : self.quiz_len,
                        "category" : self.selected_categories,
                        "difficulty" : "medium",
                        "type" : "multiple"}

            elif self.quiz_type == 2:
                pprint(self.cats)
                self.selected_categories = str(input("please enter the category number you want "))
                return {"amount" : self.quiz_len * 5, 
                        "category" : self.selected_categories,
                        "difficulty": "medium",
                        "type" : "multiple"}

            else:
                print("incorrect selection, please try again ")

    def get_questions(self):
        """Generates questions from the free open trivia database.
           qs = Number of questions
           cat = category default is None
           diff = Difficulty
           See documentation - https://opentdb.com/api.php"""

        resp = requests.get(self.host, params = self.params).json()

        if resp['response_code'] != 0:
            for _ in range(0,5):
                sleep(0.5)
                resp = requests.get(self.host, params = self.params).json()
                if resp['response_code'] == 0:
                    break

        if resp['response_code'] != 0:
            print('error fetching questions, please try again later')

        return resp

    def quiz_builder(self):
        if self.quiz_type == 1:
            for each in self.questions_json['results']:
                q = html.unescape(each['question'])
                all_answers = each['incorrect_answers']
                all_answers.append(each['correct_answer'])
                all_answers = [html.unescape(each) for each in all_answers]
                shuffle(all_answers)
                quest = [q, all_answers, html.unescape(each['correct_answer'])]
                self.final_quiz.append(quest)

        else:
            for each in self.questions_json['results']:
                if len(self.final_quiz) < self.quiz_len:
                    q = html.unescape(each['question'])
                    print(q)
                    all_answers = each['incorrect_answers']
                    all_answers.append(each['correct_answer'])
                    all_answers = [html.unescape(each) for each in all_answers]
                    shuffle(all_answers)
                    print(all_answers)
                    add_q = input('add question to output? Y/N ').lower()

                    if add_q == 'y':
                        quest = [q, all_answers, html.unescape(each['correct_answer'])]
                        self.final_quiz.append(quest)

    def write_quiz(self):
        with open('quiz_answers.txt', 'w') as f:
            f.write(f"THE QUIZ CATEGORY IS {self.cats[self.selected_categories].upper()}\n")
            for i, item in enumerate(self.final_quiz, 1):
                f.write(f"{i}. {item[0]}\n")
                f.write(f"{item[1]}\n")
                f.write(f"{item[2]}\n\n")

        with open('quiz.txt', 'w') as f:
            f.write(f"THE QUIZ CATEGORY IS {self.cats[self.selected_categories].upper()}\n")
            for i, item in enumerate(self.final_quiz, 1):
                f.write(f"{i}. {item[0]}\n")
                f.write(f"{item[1]}\n\n")

        print('quiz.txt has been created in your current directory')
