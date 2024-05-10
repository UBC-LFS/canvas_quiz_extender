from canvasapi import Canvas
import math
from datetime import datetime, timedelta, timezone, time
import threading


class QuizExtender:
    def __str__(self):
        addendum = " *" if (self.is_new == 1) else ""
        return f"{self.quiz.title}{addendum} ({self.extension_type})"

    def __init__(self, quiz, is_new, course):
        """
        params:
            class'canvasapi.quiz.Quiz' quiz - canvasapi object of quiz to have availability extended
            boolean is_new - quiz is NewQuiz?
            class'canvasapi.course.Couse' course - canvasapi object of course the quiz is part of
            string extension_type - how should the quiz class variable be extended
            int time-limit - time limit of quiz set in Canvas
        """  # I could probably make the quiz a global class variable, or at least find a way to not need to pipe it everywhere
        self.quiz = quiz
        self.is_new = is_new
        self.course = course
        if is_new:
            self.extension_type = "A"
        else:
            self.extension_type = "B"
        if not self.is_new:  # classic
            self.time_limit = self.quiz.time_limit
        else:  # new
            time_limit_seconds = self.quiz.quiz_settings[
                "session_time_limit_in_seconds"
            ]
            self.time_limit = time_limit_seconds / 60 if time_limit_seconds else None

    def get_added_time(self, extend):
        """
        params:

            float extend - value set in student_extension (1.5 = 50% more time on quiz)
        returns:
            int addded_time - translates proportional time into discrete time for each quiz's time limit
        example:
            time-limit = 20, extra = 1.5 -> added_time = 10
        """
        added_time = int(
            math.ceil(
                self.time_limit * ((float(extend * 100) - 100) / 100) if extend else 0
            )
        )
        # rounds up to the nearest multiple of 5
        rounded_time = math.ceil(added_time / 5) * 5
        return added_time

    def calculate_buffer(self, start, end, duration):
        return (
            (end - start + timedelta(minutes=duration)).total_seconds() / 60
            if end
            else None
        )

    def get_extended_time(self, extra_time, end_time, unlock_time, buffer):
        if not end_time:
            return None
        else:
            time_def = (end_time - unlock_time).total_seconds() / 60
        if extra_time <= time_def:
            return end_time
        return unlock_time + timedelta(minutes=extra_time) + timedelta(minutes=buffer)

    def is_midnight(self, query_time):
        if query_time:
            return query_time.replace(tzinfo=timezone.utc).astimezone(
                tz=None
            ).time() == time(0, 0, 0)
        return False

    def create_extensions(self, user_id_list):
        """
        params:
            Dict<int, int> user_id_list - student id and extension from imported list
        returns:
            List<Dict<"user_id": int, "extra_time": int>> - mimics a JSON file as a dictionary, formatted so that set_extension POST request works
        """
        extension_list = []
        for user_id, extend in user_id_list.items():
            added_time = self.get_added_time(extend)
            # construct the extension dictionary object for the given user_id
            extension_dict = {}
            extension_dict["user_id"] = user_id
            extension_dict["extra_time"] = added_time
            extension_list.append(extension_dict)
        return extension_list

    def create_availability(self, user_id_list):
        """
        params:
            Dict<int, int> user_id_list - student id and extension from imported list
        returns:
            Dict<int, List<int>> overrides - extra time in minutes and List of all student_ids that have the same extra time
        """
        overrides = {}
        for user_id, extend in user_id_list.items():
            added_time = self.get_added_time(extend)
            # If the extend is not already a key in overrides, add it with an empty list
            if added_time not in overrides:
                overrides[added_time] = []
            # Append the current ID to the list corresponding to the value
            overrides[added_time].append(user_id)
        return overrides

    def extend_quiz_availability(self, overrides):
        """
        params:
            Dict<int, List<int>> overrides - extra time in minutes and List of all student_ids that have the same extra time
        returns:
            NULL - POST request is sent to canvas to add assignment overrides to quiz param
        """
        unlock_time = self.quiz.unlock_at_date
        lock_time = self.quiz.lock_at_date if self.quiz.lock_at else None
        due_time = self.quiz.due_at_date if self.quiz.due_at else None
        # turn quiz into assignment so you can add assignment overrides to it
        if not self.is_new:  # classic
            quiz_assignment = self.course.get_assignment(self.quiz.assignment_id)
        else:  # new
            quiz_assignment = self.course.get_assignment(self.quiz.id)
        assignment_overrides = quiz_assignment.get_overrides()
        # clear old overrides
        if assignment_overrides:
            for override in assignment_overrides:
                override.delete()
        if not lock_time and not due_time:
            print(f"No due date or lock time, availability not changed for {self.quiz}")
            return

        # create new overrides
        # create helper function for parralel POST calls

        def _apply_override(added_time, quiz_assignment):
            extended_lock = (
                (lock_time + timedelta(minutes=added_time)) if lock_time else None
            )
            extended_due = (
                (due_time + timedelta(minutes=added_time)) if due_time else None
            )
            if self.is_midnight(extended_lock):
                extended_lock = extended_lock + timedelta(minutes=1)
                # print(
                #     f"Canvas won't set a time to 12 AM. Lock time for {self.quiz.title} set to 12:01 a.m.."
                # )
            if self.is_midnight(extended_due):
                extended_due = extended_due + timedelta(minutes=1)
                # print(
                #     f"Canvas won't set a time to 12 AM. Due date for {self.quiz.title} set to 12:01 a.m."
                # )

            quiz_assignment.create_override(
                assignment_override={
                    "student_ids": overrides[added_time],
                    "due_at": extended_due,
                    "unlock_at": unlock_time,
                    "lock_at": extended_lock,
                    "title": extended_lock,
                }
            )

        # set up threads to make API calls parrallel
        threads = []
        for added_time in overrides:
            t = threading.Thread(
                target=_apply_override, args=(added_time, quiz_assignment)
            )
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def extend_quiz(self, user_id_list):
        """
        params:
            class'canvasapi.quiz.Quiz' quiz - canvasapi object of quiz to have availability extended
            Dict<int, int> user_id_list - student id and extension from imported list
            boolean new - quiz is NewQuiz?
        returns:
            NULL : sends multiple POST requests.
        """
        if self.extension_type == "N":
            return
        if self.time_limit is None or self.time_limit < 1:
            print(
                f"No need to set extensions for {self.quiz.title} as it has no time limit."
            )
            return

        if self.extension_type in ["B", "E"] and self.is_new:
            print(
                f"Sorry, but extra time must be set manually for New Quizzes. Availability (A) can still be automatically adjusted."
            )
            return
        if self.extension_type in ["B", "E"] and not self.is_new:
            extensions = self.create_extensions(user_id_list)
            self.quiz.set_extensions(extensions)
            # print(f"{self.quiz.title} has been given extra time.")
        if self.extension_type in ["B", "A"]:
            overrides = self.create_availability(user_id_list)
            self.extend_quiz_availability(overrides)
            # print(f"{self.quiz.title} has had its availability extended.")
        elif self.extension_type not in ["B", "A", "E"]:
            print(
                "The extension type has been set incorrectly.\n A - Availability, E - Extra Time, B - Both, N - None"
            )
            return
        print(f"{self.quiz.title} extended!")
        return
