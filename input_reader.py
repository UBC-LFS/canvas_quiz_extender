import pandas as pd


class InputReader:
    input_csv = None
    df = None

    def __init__(self, input_csv):
        self.input_csv = input_csv
        self.df = pd.read_csv(input_csv)

    def get_student_extensions(self):
        """
        Creates an dictionary of all assignment IDs and assigns a list containing student IDs for each assignment ID
        """

        return self.df.set_index("Student")["Extension"].to_dict()

    def check_duplicate_students(self):
        duplicates = self.df.duplicated(subset=["Student"])
        return duplicates.any()

    def get_quiz_list(self):
        try:
            quiz_list = self.df["Quizzes"].tolist()
        except KeyError:
            quiz_list = None
            # _quiz_query()

        return quiz_list

    # def _quiz_query():
    #     choice = input("Do you want to extend all quizzes with a time limit? [y/n]")
    #     if choice == "y":
    #         return
    #     if choice == "n":
    #         print(
    #             "Please add an additional column in your CSV file labelled Quizzes, with the quiz id's of the quizzes you want to extend. \n(These can be found in the url when navigating to the quiz page.)"
    #         )
    #         sys.exit()
    #     else:
    #         print("Invalid input, make sure it's lower case.")
    #         quiz_query()
