import requests
from random import sample, choice, shuffle
import html
from pprint import pprint
from time import sleep

class QuizGenerator:
    ''' Pulls a number of questions from the free open trivia database. 
    option 1 = Each question to printed to the user to decide whether to add it to the final quiz sheet by pressing 'y' or 'n'.
    option 2 = Questions are randomly picked at a random difficulty.
    The final output will be 2 .txt file written as follows:
    1. What programming language is this?
    ['foo', 'bar', 'python', 'world']
    *Python* < only on the answer sheet'''
    
    host = 'https://opentdb.com'
    documentation = 'https://opentdb.com/api_config.php'
    
    final_quiz = []
    quiz_type = 0
    difficulty = ''
    api_limit = 50

    cats = {"9":"General Knowledge",
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
        while self.quiz_len > 50:
            self.quiz_len = int(input('how many questions would you like for your quiz? Must be less than 50 '))
        self.params = self.get_params()
        self.questions_json = self.get_questions()
        self.quiz_builder()
        
        if len(self.final_quiz) > 0:
            self.write_quiz()
        else:
            print('no questions added to the final output. please try again. ')
            
    def check_number_qs(self, dif, cat):
        endpoint = '/api_count.php'
        c_params = {"category" : cat}
        resp = requests.get(self.host + endpoint, 
                            params = c_params).json()
        
        self.max_qs = resp['category_question_count'][f'total_{dif}_question_count']
        
        if self.max_qs < self.api_limit:
            self.api_limit = self.max_qs
        if self.max_qs < self.quiz_len:
            self.quiz_len = self.max_qs
        
    def get_params(self):
        
        while self.quiz_type not in [1, 2]:
            self.quiz_type = int(input('please press 1 to create a random quiz or 2 to customise the quiz. '))

            if self.quiz_type == 1:
                self.selected_category = choice(list(self.cats.keys()))
                self.difficulty = choice(["easy", "medium", "hard"])
                
                self.check_number_qs(dif = self.difficulty, cat = self.selected_category)
                
                return {"amount" : self.quiz_len,
                        "category" : self.selected_category,
                        "difficulty" : self.difficulty,
                        }

            elif self.quiz_type == 2:
                pprint(self.cats)
                self.selected_category = str(input("please enter the category number you want "))
                while self.difficulty not in ["easy", "medium", "hard"]:
                    self.difficulty = str(input('please enter a difficult level - either "easy", "medium", "hard": '))
                
                self.check_number_qs(dif = self.difficulty, cat = self.selected_category)
                
                return {"amount" : self.api_limit, 
                        "category" : self.selected_category,
                        "difficulty": self.difficulty,
                        }

            else:
                print("incorrect selection, please try again ")

    def get_questions(self):
        endpoint = '/api.php'
        resp = requests.get(self.host + endpoint, params = self.params).json()

        if resp['response_code'] != 0:
            for _ in range(0,3):
                sleep(0.5)
                resp = requests.get(self.host, params = self.params).json()
                if resp['response_code'] == 0:
                    break

        if resp['response_code'] != 0:
            print(resp)
            if resp['response_code'] == 1:
                print('no results found, please choose a different category/number of questions')
            elif resp['response_code'] == 2:
                print('invalid parameter, please try again')

        return resp

    def quiz_builder(self):
        if self.quiz_type == 1:
            for each in self.questions_json['results']:
                q = html.unescape(each['question'])
                all_answers = each['incorrect_answers'] + [each['correct_answer']]
                all_answers = [html.unescape(each) for each in all_answers]
                shuffle(all_answers)
                quest = [q, all_answers, html.unescape(each['correct_answer'])]
                self.final_quiz.append(quest)

        else:
            for each in self.questions_json['results']:
                if len(self.final_quiz) < self.quiz_len:
                    q = html.unescape(each['question'])
                    print(q)
                    all_answers = each['incorrect_answers'] + [each['correct_answer']]
                    all_answers = [html.unescape(each) for each in all_answers]
                    shuffle(all_answers)
                    print(all_answers)
                    add_q = input('add question to output? Y/N ').lower()

                    while add_q.lower() not in ['y', 'n']:
                        print('incorrect selection - please enter either Y or N ')
                        add_q = input('add question to output? Y/N ').lower()
                    
                    if add_q.lower() == 'y':
                        quest = [q, all_answers, html.unescape(each['correct_answer'])]
                        self.final_quiz.append(quest)
                    elif add_q.lower() == 'n':
                        continue 

    def write_quiz(self):
        cat = ''.join(filter(str.isalpha, self.cats[self.selected_category]))
        quiz_answers = f'{cat}{self.quiz_len}quiz_answers.txt'
        quiz_sheet = f'{cat}{self.quiz_len}quiz.txt'
        
        with open(quiz_answers, 'w') as f:
            f.write(f"THE QUIZ CATEGORY IS {self.cats[self.selected_category].upper()} AND THE DIFFICULTY IS {self.difficulty.upper()}\n")
            for i, item in enumerate(self.final_quiz, 1):
                f.write(f"{i}. {item[0]}\n")
                f.write(f"{item[1]}\n")
                f.write(f"{item[2]}\n\n")

        with open(quiz_sheet, 'w') as f:
            f.write(f"THE QUIZ CATEGORY IS {self.cats[self.selected_category].upper()} AND THE DIFFICULTY IS {self.difficulty.upper()}\n")
            for i, item in enumerate(self.final_quiz, 1):
                f.write(f"{i}. {item[0]}\n")
                f.write(f"{item[1]}\n\n")

        print(f'{quiz_sheet} and {quiz_answers} have been created in your current directory')
        
        
QuizGenerator()