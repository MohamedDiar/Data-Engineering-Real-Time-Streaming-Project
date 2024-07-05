"""
This script is used to simulate user behavior and factors that might affect glucose levels.
"""

import random
from .Thresholds_Retreiving import user_id_age, user_id_condition, user_id_medication


# ------------User Behavior and Factors Affecting Glucose Levels------------#

class UserBehavior:
    """
    Represents the behavior of a user in a simulation.

    Attributes:
        user_id (int): The ID of the user.
        age (int): The age of the user.
        condition (str): The medical condition of the user.
        medication (str): The medication taken by the user.
        exercise_intensity (str): The intensity of exercise based on the user's age.
        diet_type (str): The type of diet based on the user's age.

    Methods:
        determine_exercise_intensity: Determines the exercise intensity based on the user's age.
        determine_diet_type: Determines the diet type based on the user's age.
        condition_effect: Determines the effect of the user's medical condition on glucose levels.
        medication_effect: Determines the effect of the user's medication on glucose levels.
        exercise_effect: Determines the effect of exercise on glucose levels.
        diet_effect: Determines the effect of diet on glucose levels.
        glucose_reading_effect: Determines the overall effect of lifestyle factors on glucose levels.
    """

    def __init__(self, user_id, age, condition, medication):
        self.user_id = user_id
        self.age = age
        self.condition = condition
        self.medication = medication
        self.exercise_intensity = self.determine_exercise_intensity()
        self.diet_type = self.determine_diet_type()

    def determine_exercise_intensity(self):
        """
        Determines the exercise intensity based on the user's age.

        Returns:
            str: The exercise intensity ('high', 'medium', 'low', or 'none').
        """

        # Young adults (18-35) are more likely to have high intensity workouts
        if 18 <= self.age <= 35:
            return random.choice(['high', 'medium', 'low'])

        # Middle-aged adults (36-60) have a mix of medium and low intensity
        if 36 <= self.age <= 60:
            return random.choice(['medium', 'low', 'none'])

        # Older adults (>60) primarily have low intensity or no exercise
        return random.choice(['low', 'none'])

    def determine_diet_type(self):
        """
        Determines the diet type based on the user's age.

        Returns:
            str: The diet type ('high_carb', 'balanced', or 'low_carb').
        """

        # Different age groups might have different dietary preferences
        if self.age < 40:
            return random.choice(["high_carb", "balanced", "low_carb"])

        # Older adults (>40) might prefer a low-carb diet or a balanced diet
        return random.choice(["balanced", "low_carb"])

    def condition_effect(self):
        """
        Determines the effect of the user's medical condition on glucose levels.

        Returns:
            float: The effect of the medical condition on glucose levels.
        """

        # Mapping of conditions to their respective ranges
        condition_ranges = {
            "Type 1 Diabetes": (-15, 25),
            "Type 2 Diabetes": (-10, 15),
            "Gestational Diabetes": (-10, 20),
            "Prediabetes": (-10, 10),
            "Insulin Resistance": (-5, 15),
            "Hypoglycemia": (-10, 0),
            "Hyperglycemia": (10, 30),
            "Metabolic Syndrome": (-10, 20),
            "Polycystic Ovary Syndrome": (-5, 15),
            "Cystic Fibrosis-Related Diabetes": (-15, 25),
            "Chronic Pancreatitis": (-10, 20),
            "Monogenic Diabetes": (-10, 20)
        }

        # Gets the range for the current condition. Will default to (0, 0) if not found
        condition_range = condition_ranges.get(self.condition, (0, 0))

        return random.uniform(*condition_range)

    def medication_effect(self):
        """
        Determines the effect of the user's medication on glucose levels.

        Returns:
            float: The effect of the medication on glucose levels.
        """

        # Mapping of medications to a given range
        medication_ranges = {
            "Insulin Glargine": (-10, -5),
            "Metformin": (-16, -10),
            "Insulin Lispro": (-15, -5),
            "Glipizide": (-12, -6),
            "Glyburide": (-15, -10),
            "Dapagliflozin": (-15, -5),
            "Empagliflozin": (-15, -5),
            "Liraglutide": (-15, -5),
            "Exenatide": (-15, -5),
            "Sitagliptin": (-15, -5)
        }

        medication_range = medication_ranges.get(self.medication, (0, 0))

        return random.uniform(*medication_range)

    def exercise_effect(self):
        """
        Determines the effect of exercise on glucose levels.

        Returns:
            float: The effect of exercise on glucose levels.
        """

        # Effect of exercise on glucose levels
        if self.exercise_intensity == 'high':
            return -random.uniform(5, 15)
        if self.exercise_intensity == 'medium':
            return -random.uniform(3, 10)
        return 0

    def diet_effect(self):
        """
        Determines the effect of diet on glucose levels.

        Returns:
            float: The effect of diet on glucose levels.
        """
        # Effect of diet on glucose levels
        if self.diet_type == 'high_carb':
            return random.uniform(10, 30)
        if self.diet_type == 'low_carb':
            return random.uniform(0, 10)
        # balanced diet
        return random.uniform(5, 15)

    def glucose_reading_effect(self):
        """
        Determines the overall effect of lifestyle factors on glucose levels.

        Returns:
            float: The overall effect of lifestyle factors on glucose levels.
        """
        glucose_effect = 0

        # Incorporating condition, medication, exercise, diet
        glucose_effect += self.condition_effect()
        glucose_effect += self.medication_effect()
        glucose_effect += self.exercise_effect()
        glucose_effect += self.diet_effect()

        return glucose_effect


# creating UserBehavior instances
def create_user_behaviors(user_id_age, user_id_condition, user_id_medication):
    """
    Create UserBehavior instances for each user based on their age, condition, and medication

    :param user_id_age: The user ID and age
    :param user_id_condition: The user ID and condition
    :param user_id_medication: The user ID and medication

    :return: A dictionary of user behaviors with user ID as the key
    """
    users_behavior = {}
    for user_id, age in user_id_age:
        condition = next(cond for uid, cond in user_id_condition if uid == user_id)
        medication = next(med for uid, med in user_id_medication if uid == user_id)
        users_behavior[user_id] = UserBehavior(user_id, age, condition, medication)
    return users_behavior

# Will be used to get the glucose effect for a specific user
def get_glucose_effect(user_id, behaviors):
    """
    Get the glucose effect for a specific user

    :param user_id: The user ID to get the glucose effect for
    :param behaviors: The user behaviors dictionary
    
    :return: The glucose effect for the user based on their behavior
    """
    return behaviors[user_id].glucose_reading_effect()


user_behaviors = create_user_behaviors(user_id_age, user_id_condition, user_id_medication)
