import re

file_path = "e:/Study/FPT/S3/ADY201m/real-estate-price-analysis/final_report/presentation/slide_content.txt"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Updates for Ridge Regression to Linear Regression
content = content.replace("Initial Linear Analysis (Ridge Regression)", "Initial Linear Analysis (Linear Regression)")
content = content.replace("baseline Ridge Regression model", "baseline Linear Regression model")

# Updates for Model Count (15 to 5)
content = content.replace("15 different Machine Learning", "5 different Machine Learning")
content = content.replace("15 different, more advanced", "5 different, more advanced")
content = content.replace("Among the 15 models tested", "Among the 5 models tested")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Presentation Slides.")
