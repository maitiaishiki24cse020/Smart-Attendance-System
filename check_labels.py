import numpy as np

student_info = np.load(
    "student_labels.npy",
    allow_pickle=True
).item()

print("Trained student information:")

for student_id, details in student_info.items():
    print("ID:", student_id)
    print("Name:", details["name"])
    print("Roll Number:", details["roll_no"])
    print("-------------------")