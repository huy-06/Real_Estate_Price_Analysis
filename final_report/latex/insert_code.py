import re

file_path = "e:/Study/FPT/S3/ADY201m/real-estate-price-analysis/final_report/latex/final-report.tex"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

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

\vspace{0.5em}
\noindent\textbf{Example Snippet: Python Preprocessing Pipeline}
\begin{small}
\begin{verbatim}
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])
\end{verbatim}
\end{small}
"""

content = content.replace("\\end{itemize}\n\n\\subsection{Missing Data Handling and Feature Selection}", sql_snippet + "\n\\subsection{Missing Data Handling and Feature Selection}")

# Also replace the picture path missed by the regex (due to no width argument etc) if any
content = re.sub(r"\\includegraphics\[?.*?\]?\{([^/]+\.png)\}", r"\\includegraphics{\1}", content) # reset
content = content.replace("ictures/pictures", "pictures") # fix any double replacement

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully injected the SQL and Python code snippets into the LaTeX report.")
