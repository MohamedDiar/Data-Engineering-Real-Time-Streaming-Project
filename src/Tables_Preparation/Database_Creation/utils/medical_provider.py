from faker.providers import BaseProvider

class MedicalProvider(BaseProvider):
    def doctor_occupation(self):
        occupations = [
            "Endocrinologist",  # Specialists in conditions like diabetes
            "Diabetologist",  # Doctors specializing in diabetes management
            "Nephrologist",  # Kidney specialists, as kidney health can be affected by blood glucose levels
            "General Practitioner",  # Often involved in initial diabetes diagnosis and management
            "Pediatric Endocrinologist",  # Specializing in children's endocrine disorders including diabetes
            "Cardiologist",  # As diabetes can affect heart health
            "Ophthalmologist",  # Eye health can be affected by diabetes
            "Podiatrist",  # Foot care specialists, important in diabetes management
            "Dietitian",  # Specializing in dietary management of diabetes
            "Certified Diabetes Educator",  # Specialist in educating patients about diabetes management
            "Urologist",
            "Neurologist",
        ]
        return self.random_element(occupations)

    def relation_to_user(self):
        relations = [
            "Doctor",
            "Father",
            "Mother",
            "Brother",
            "Sister",
            "Cousin",
            "Uncle",
            "Aunt",
            "Grandfather",
            "Grandmother",
        ]
        return self.random_element(relations)

    def medical_condition(self):
        conditions = [
            "Type 1 Diabetes",  # Autoimmune condition affecting blood glucose
            "Type 2 Diabetes",  # More common, lifestyle-related diabetes
            "Gestational Diabetes",  # Diabetes occurring during pregnancy
            "Prediabetes",  # Elevated blood glucose not yet at diabetes level
            "Insulin Resistance",  # Body's reduced response to insulin
            "Hypoglycemia",  # Abnormally low blood glucose levels
            "Hyperglycemia",  # High blood glucose levels
            "Metabolic Syndrome",  # Cluster of conditions including high blood glucose
            "Polycystic Ovary Syndrome",  # Can be associated with insulin resistance
            "Cystic Fibrosis-Related Diabetes",  # Diabetes specific to cystic fibrosis patients
            "Chronic Pancreatitis",  # Can lead to diabetes due to the pancreas damage
            "Monogenic Diabetes",  # Diabetes due to genetic mutations
        ]
        return self.random_element(conditions)

    # Medications
    def medication(self):
        medications = [
            "Metformin",  # Commonly prescribed for Type 2 Diabetes
            "Insulin Glargine",  # Long-acting insulin
            "Insulin Lispro",  # Rapid-acting insulin
            "Glipizide",  # Sulfonylurea for Type 2 Diabetes
            "Glyburide",  # Another Sulfonylurea
            "Glimepiride",  # Sulfonylurea class medication
            "Dapagliflozin",  # SGLT2 inhibitor for Type 2 Diabetes
            "Empagliflozin",  # Another SGLT2 inhibitor
            "Liraglutide",  # GLP-1 receptor agonist
            "Exenatide",  # Used for blood sugar control in Type 2 Diabetes
            "Sitagliptin",  # DPP-4 inhibitor, helps manage blood sugar levels
            "Canagliflozin",  # Another SGLT2 inhibitor for Type 2 Diabetes
            "Pioglitazone",  # A medication for Type 2 Diabetes that helps control blood sugar levels
            "Insulin Aspart",  # A fast-acting form of insulin
            "Repaglinide",  # Stimulates pancreas to release more insulin
            "Nateglinide",  # Another medication that stimulates insulin release
            "Acarbose",  # Alpha-glucosidase inhibitor, slows carbohydrate absorption
            "Miglitol",  # Similar to Acarbose, an alpha-glucosidase inhibitor
            "Linagliptin",  # A DPP-4 inhibitor, used in Type 2 Diabetes management
            "Saxagliptin",  # Another DPP-4 inhibitor for blood sugar regulation
            "Pramlintide",  # An injectable drug for blood sugar control in Type 1 and Type 2 Diabetes
            "Rosiglitazone",  # Thiazolidinedione class, helps improve insulin sensitivity
            "Insulin Detemir",  # Long-acting insulin for maintaining blood sugar levels
            "Insulin Degludec",  # Ultra-long-acting insulin
            "Insulin Glulisine",  # Rapid-acting insulin, similar to Insulin Lispro and Aspart
        ]
        return self.random_element(medications)
