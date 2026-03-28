import re

file_path = "e:/Study/FPT/S3/ADY201m/real-estate-price-analysis/final_report/latex/final-report.tex"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Image Paths
content = re.sub(r"\\includegraphics\[(.*?)\]\{([^\/]+?\.png)\}", r"\\includegraphics[\1]{pictures/\2}", content)

# 2. Update Model Count
content = content.replace("15 different Machine Learning algorithms", "5 different Machine Learning algorithms")
content = content.replace("Performance Ranking of 15 Machine Learning", "Performance Ranking of 5 Machine Learning")

# 3. Update Ridge Regression to Linear Regression
content = content.replace("\\textbf{Ridge Regression}", "\\textbf{Linear Regression}")
content = content.replace("Ridge explains market trends well", "Linear Regression explains market trends well")
content = content.replace("ridge_coefficients.png", "linear_regression_coefficients.png")

# 4. Insert Code Snippet in Section 5.1
# Locate the end of Section 5.1 (the itemize block ends with \end{itemize})
# We will insert the SQL verbatim block right after the \end{itemize} of Section 5.1

sql_snippet = r"""\end{itemize}

\vspace{0.5em}
\noindent\textbf{Example Snippet: Filtering Price Outliers (SQL)}
\begin{small}
\begin{verbatim}
delete from raw_data
where post_id in (
    select post_id from (
        select post_id, price_total,
               avg(price_total) over (partition by category) as avg_price,
               stdev(price_total) over (partition by category) as std_dev
        from raw_data
    ) as calc_table
    where price_total > (avg_price + 3 * std_dev)
)
\end{verbatim}
\end{small}
"""

# Replace the specific \end{itemize} that precedes Section 5.2
content = content.replace("\\end{itemize}\n\n\\subsection{Handling Missing Data and Feature Selection}", sql_snippet + "\n\\subsection{Handling Missing Data and Feature Selection}")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated LaTeX report.")
