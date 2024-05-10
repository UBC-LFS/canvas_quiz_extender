from canvasapi import Canvas
import pandas as pd
import threading


class CourseGetter:
    student_list = []
    id = 0
    course = None

    def __str__(self):
        return __str__(self.course)

    def __init__(self, id, canvas):
        self.id = id
        self.course = canvas.get_course(self.id)

    def update_course(self):
        self.course = canvas.get_course(id)

    def get_quizzes(self):
        # Get all Classic Quizzes in course, then all New Quizzes in course
        quizzes = self.course.get_quizzes()
        new_quizzes = self.course.get_new_quizzes()

        quiz_dict = {}  # 0 for classic quizzes, 1 for new quizzes
        for quiz in quizzes:  # classic
            quiz_dict[quiz] = 0
        for new_quiz in new_quizzes:  # new
            quiz_dict[new_quiz] = 1
        return quiz_dict

    def get_user_ids(self, student_extensions):
        # Get all users with student role in course
        students = self.course.get_users(enrollment_type=["student"])
        processed_students = set()
        user_id_dict = {}

        # Find student's name in course and replace with id.
        def _search_name(student):
            name = student.name
            if name in student_extensions:
                extension = student_extensions[name]
                if pd.isnull(extension):
                    print(
                        f"{name} does not have an extension associated with them. Skipping."
                    )
                    return
                if extension <= 1.0:
                    print(f"Invalid extension ( <= 1.0) for {name}")
                    return

                processed_students.add(name)
                user_id_dict[student.id] = extension
                self.student_list.append(f"{str(student)}, {extension}")

        # Produce dict of user_id: extension
        # (There's probably a faster way to do this)
        threads = []
        for student in students:
            t = threading.Thread(target=_search_name, args=(student,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        unprocessed_keys = set(student_extensions.keys()) - processed_students
        if unprocessed_keys:
            print("These students were not found in the given class:")
            for key in unprocessed_keys:
                print(key)
            input("\nPress enter to continue.")

        return user_id_dict

    def get_course(self):
        return self.course

    def get_student_list(self):
        return self.student_list

    def set_course(self, course):
        self.course = course
        return
