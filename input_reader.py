import pandas as pd
import os
import re
from pypdf import PdfReader


class InputReader:
    folder_path = None
    user_dict = None
    df = None

    def __init__(self, file):
        self.file = file

    def get_student_extensions(self):
        """
        Iterates though given folder of pdf's and extract a dict of user_id and extension from each of them
        """

        file = self.file

        def _extract_info_from_csv(file):
            self.df = pd.read_csv(file)
            return self.df.set_index("Student")["Extension"].to_dict()

        def _extract_info_from_pdf(file_path):
            try:
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                # Regex to find the student number
                student_number_match = re.search(r"\b\d{8}\b", text)
                if student_number_match:
                    student_number = student_number_match.group()
                else:
                    raise Exception("Could not find student number.")

                # Regex to find the extended time for exams
                extended_time_match = re.search(
                    r"Extended time \((\d+\.?\d*)x\) for all exams", text
                )
                if extended_time_match:
                    extended_time = float(extended_time_match.group(1))
                else:
                    raise Exception("Could not find extension time.")

                print(student_number)
                return (student_number, extended_time)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                return None

        extension_list = []
        if file.endswith(".csv"):
            self.user_dict = _extract_info_from_csv(file)

        else:
            for file_name in os.listdir(file):
                if file_name.endswith(".pdf"):
                    file_path = os.path.join(file, file_name)
                    info = _extract_info_from_pdf(file_path)
                    if info:
                        extension_list.append(info)

            self.user_dict = dict(extension_list)

        return self.user_dict

    def check_duplicate_students(self):
        duplicates = self.df.duplicated(subset=["Student"])
        return duplicates.any()

    # def get_quiz_list(self):
    #     try:
    #         quiz_list = self.df["Quizzes"].tolist()
    #     except KeyError:
    #         quiz_list = None
    #         # _quiz_query()

    #     return quiz_list

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
