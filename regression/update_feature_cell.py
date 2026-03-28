import json

file_path = "e:/Study/FPT/S3/ADY201m/real-estate-price-analysis/regression/train_models_short.ipynb"
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell.get('source', [])
        source_str = "".join(source)

        if "print(\\\"Training Ridge Regression to extract weights...\\\")" in source_str or "Ridge(alpha" in source_str:
            new_source = [
                "from sklearn.linear_model import LinearRegression\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from sklearn.pipeline import Pipeline\n",
                "\n",
                "print(\"Training Linear Regression to extract weights...\")\n",
                "\n",
                "lr_pipeline = Pipeline(steps=[\n",
                "    ('preprocessor', preprocessor),\n",
                "    ('model', LinearRegression())\n",
                "])\n",
                "\n",
                "lr_pipeline.fit(X_train, y_train)\n",
                "\n",
                "feature_names = preprocessor.get_feature_names_out()\n",
                "coefficients = lr_pipeline.named_steps['model'].coef_\n",
                "\n",
                "coef_df = pd.DataFrame({\n",
                "    'Feature': feature_names,\n",
                "    'Coefficient': coefficients\n",
                "})\n",
                "\n",
                "coef_df['Feature'] = coef_df['Feature'].str.replace('num__', '', regex=False).str.replace('cat__', '', regex=False)\n",
                "coef_df['Abs_Coefficient'] = coef_df['Coefficient'].abs()\n",
                "top_10_features = coef_df.sort_values(by='Abs_Coefficient', ascending=False).head(10)\n",
                "\n",
                "print(\"\\nREGRESSION COEFFICIENTS TABLE (TOP 10):\")\n",
                "display(top_10_features[['Feature', 'Coefficient']])\n",
                "\n",
                "plt.figure(figsize=(10, 6))\n",
                "colors = top_10_features['Coefficient'].apply(lambda x: 'crimson' if x > 0 else 'steelblue')\n",
                "sns.barplot(data=top_10_features, x='Coefficient', y='Feature', palette=colors.tolist())\n",
                "\n",
                "plt.title('Top 10 Features with the Largest Regression Coefficients', fontsize=14, fontweight='bold')\n",
                "plt.xlabel('Regression Coefficient (Billion VND)', fontsize=12)\n",
                "plt.ylabel('Feature', fontsize=12)\n",
                "plt.axvline(x=0, color='black', linestyle='--', linewidth=1) \n",
                "\n",
                "plt.tight_layout()\n",
                "plt.savefig('linear_regression_coefficients.png', dpi=300)\n",
                "plt.show()\n"
            ]
            cell['source'] = new_source
            print("Successfully updated cell.")
            break

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
