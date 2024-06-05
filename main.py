from canvasapi import Canvas
import threading
import sys
from quiz_extender import QuizExtender
from input_reader import InputReader
from course import CourseGetter
import time
import settings


class TerminalMenu:
    student_list = []
    quiz_extenders = []
    user_id_dict = {}
    instructions = """Enter "none" to set all quizzes to none.\nEnter the number of the quiz to modify or 'q' to quit.\nEnter 'list' to show the students who will be applied quiz extensions.\nEnter 'run' to extend the quizzes."""
    url = ""
    key = ""

    def __init__(self, url, key):
        self.url = url
        self.key = key

    def display_title(self):
        title = "Canvas Quiz Extender"
        print("\n" + title)
        print("-" * len(title))

    def display_menu(self):
        print("\nQuizzes:")
        for i, quiz in enumerate(self.quiz_extenders, start=1):
            print(f"{i}. {quiz}")
        print("\nA - Availability, E - Extra Time, B - Both, N - None (Skip)")
        print("New Quizzes are marked with *")
        print(f"\n{self.instructions}")

    def modify_menu(self, selected_quiz):  # should probably split up
        """Display menu to modify quiz, processes the action to modify the quiz"""
        print(
            f"\nYou have selected {selected_quiz.quiz.title} ({selected_quiz.extension_type}):"
        )
        print("1. Set type to A")
        print("2. Set type to E")
        print("3. Set type to B")
        print("4. Set type to N")
        print("5. Cancel")

        action = input("> ")

        if action in ["1", "A", "a"]:
            selected_quiz.extension_type = "A"
            return
        elif action in ["2", "E", "e"]:
            if selected_quiz.is_new:
                print(
                    f"Sorry, but extra time must be set manually for New Quizzes. Availability (A) can still be automatically adjusted."
                )
                input("Press enter to continue.")
                self.modify_menu(selected_quiz)
            else:
                selected_quiz.extension_type = "E"
            return
        elif action in ["3", "B", "b"]:
            if selected_quiz.is_new:
                print(
                    f"Sorry, but extra time must be set manually for New Quizzes. Availability (A) can still be automatically adjusted."
                )
                input("Press enter to continue.")
                self.modify_menu(selected_quiz)
            else:
                selected_quiz.extension_type = "B"
            return
        elif action in ["4", "N", "n"]:
            selected_quiz.extension_type = "N"
            return
        elif action in ["5", "Q", "q"]:
            # Cancel
            return
        else:
            print("Invalid action. Please try again.")
            self.modify_menu(selected_quiz)
            return

    def run(self):
        """Run the GUI. Display the menu, process user input, start activating the QuizExtenders"""  # should probably split up as well
        self.display_title()
        while True:
            self.display_menu()
            choice = input("\n> ")
            if choice.lower() == "none":
                for quiz in self.quiz_extenders:
                    quiz.extension_type = "N"
                print("All quizzes set to none.")
                input("\nPress enter to continue.")
                continue
            if choice.lower() == "list":
                for student in self.student_list:
                    print(student)
                input("\nPress enter to continue.")
                continue
            if choice.lower() == "q":
                break
            if choice.lower() == "run":
                # Add extensions for each student for each quiz
                threads = []
                for quiz in self.quiz_extenders:
                    t = threading.Thread(
                        target=quiz.extend_quiz, args=(self.user_id_dict,)
                    )
                    t.start()
                    threads.append(t)

                for t in threads:
                    t.join()

                print("All quizzes extended!")
                break

            try:
                if int(choice) <= 0:
                    raise ValueError
                selected_quiz = self.quiz_extenders[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid command.")
                continue

            self.modify_menu(selected_quiz)

            # Confirm and apply changes...

    def load(self, input_csv):
        """Get all the information for the process to run, make the QuizGetters"""  # all of these should probably be split up a bit
        # Prompt the user for a course ID
        # course_id = input("Enter course ID: ")
        course_id = 143309

        canvas = Canvas(self.url, self.key)
        try:
            course = CourseGetter(course_id, canvas)
        except e:
            print(f"Error detected, check Course ID.")
            return

        reader = InputReader(pdf_folder)
        # if reader.check_duplicate_students():
        #     print(f"Duplicate students detected, use Student ID's instead.")
        #     return

        quiz_dict = course.get_quizzes()
        self.user_id_dict = reader.get_student_extensions()
        self.student_list = course.create_student_list(self.user_id_dict)

        # def filter_quizzes(quiz_list, quiz_dict):
        #     # for quiz, id in quiz_dict.items():
        #     #     print(f"{quiz} + {type(id)}")
        #     filtered_dict = {}
        #     for quiz, new in quiz_dict.items():
        #         if new:
        #             if int(quiz.id) in quiz_list:
        #                 filtered_dict[quiz] = 1
        #             else:
        #                 continue
        #         else:
        #             if quiz.id in quiz_list:
        #                 filtered_dict[quiz] = 0
        #             else:
        #                 continue

        #     return filtered_dict

        # quiz_list = reader.get_quiz_list()
        # if quiz_list:
        #     quiz_dict = filter_quizzes(quiz_list, quiz_dict)

        extenders = []
        for quiz, new in quiz_dict.items():
            # print(f"Quiz:{quiz}")
            # print(f"New:{new}")
            extenders.append(QuizExtender(quiz, new, course.get_course()))
        self.quiz_extenders = extenders

        self.run()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_folder = sys.argv[1]
    else:
        print(
            "Please run the program again with the csv file passed as command-line arguments"
        )
        sys.exit()

    menu = TerminalMenu(url=settings.API_URL, key=settings.API_KEY)
    menu.load(pdf_folder)
