from canvasapi import Canvas
import pandas as pd
import threading
from api_caller import make_request

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

    def process_dict(self, user_id_dict):
        ''' filter out non-class id's, create list of student's in dict and student's not in class'''
        # students = self.course.get_users(enrollment_type=["student"])
        # print(students)

        processed_students = []
        extension_dict = {}


        try: 
             response = make_request(f"courses/{self.id}/users")
            #  print(response)
        
        except Exception as e:
            print(f"Error fetching users: {str(e)}")

        # student_mapping = {student['sis_user_id']: student['id'] for student in response}
        # print(student_mapping)






        # Filter out student id not in course, add to unprocessed students.
        def _search_name(student):
           try:
                sis_user_id = student.get('sis_user_id')
                if sis_user_id is not None:
                    sis_user_id_int = int(sis_user_id)  
                    if sis_user_id_int in user_id_dict:
                        processed_students.append(sis_user_id_int)  
                        extension_dict[student['id']] = user_id_dict[sis_user_id_int]
                        self.student_list.append(f"{str(student['name'])}, {user_id_dict[sis_user_id_int]}")
           except ValueError:
                print(f"Invalid value for sis_user_id: {sis_user_id}")
           except Exception as e:
                print(f"Error processing student {student}: {e}")


        # Produce dict of user_id: extension
        # (There's probably a faster way to do this)
        threads = []
        for student in response:
            # print(student)
            t = threading.Thread(target=_search_name, args=(student,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        unprocessed_students = user_id_dict.keys() - processed_students
        if unprocessed_students:
            print("These students were not found in the given class:")
            for student in unprocessed_students:
                print(student)
            input("\nPress enter to continue.")
        
      

        return extension_dict

    # # Get user ID and then add name to student list
    # def get_user_ids(self, student_extensions):
    #     # Get all users with student role in course
    #     students = self.course.get_users(enrollment_type=["student"])
    #     processed_students = set()
    #     user_id_dict = {}

    #     # Find student's name in course and replace with id.
    #     def _search_name(student):
    #         name = student.name
    #         if name in student_extensions:
    #             extension = student_extensions[name]
    #             if pd.isnull(extension):
    #                 print(
    #                     f"{name} does not have an extension associated with them. Skipping."
    #                 )
    #                 return
    #             if extension <= 1.0:
    #                 print(f"Invalid extension ( <= 1.0) for {name}")
    #                 return

    #             processed_students.add(name)
    #             user_id_dict[student.id] = extension
    #             self.student_list.append(f"{str(student)}, {extension}")

    #     # Produce dict of user_id: extension
    #     # (There's probably a faster way to do this)
    #     threads = []
    #     for student in students:
    #         t = threading.Thread(target=_search_name, args=(student,))
    #         t.start()
    #         threads.append(t)
    #     for t in threads:
    #         t.join()

    #     unprocessed_keys = set(student_extensions.keys()) - processed_students
    #     if unprocessed_keys:
    #         print("These students were not found in the given class:")
    #         for key in unprocessed_keys:
    #             print(key)
    #         input("\nPress enter to continue.")

    #     return user_id_dict

    def get_course(self):
        return self.course

    def get_student_list(self):
        return self.student_list

    def set_course(self, course):
        self.course = course
        return
