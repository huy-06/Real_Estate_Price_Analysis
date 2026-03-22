import pandas as pd
import numpy as np
import joblib # Import thư viện để lưu mô hình
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# ==========================================
# 1. ĐỌC VÀ LỌC DỮ LIỆU
# ==========================================
df = pd.read_csv('../data/train_data.csv')
df["price_billion"] = df["price_total"] / 1000000000
df = df[df['area'].between(15, 1000) & df['price_billion'].between(0.5, 60)]

# ==========================================
# 2. CHIA DỮ LIỆU TRAIN / TEST
# ==========================================
X = df.drop(columns=['price_total', 'price_billion', 'price_per_m2'])
y = df['price_billion'] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# 3. THIẾT LẬP BỘ TIỀN XỬ LÝ (PREPROCESSOR)
# ==========================================
numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# ==========================================
# 4. TẠO PIPELINE EXTRA TREES & HUẤN LUYỆN
# ==========================================
print("Đang huấn luyện mô hình Extra Trees...")

# Khởi tạo Pipeline chỉ với Extra Trees
extra_trees_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=-1)) # n_jobs=-1 để chạy nhanh hơn
])

# Fit dữ liệu
extra_trees_pipeline.fit(X_train, y_train)

# ==========================================
# 5. ĐÁNH GIÁ NHANH MÔ HÌNH
# ==========================================
y_pred = extra_trees_pipeline.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"✔️ Huấn luyện xong!")
print(f"📊 Kết quả trên tập Test: R2 = {r2:.4f} | MAE = {mae:.4f} Tỷ VNĐ")

# ==========================================
# 6. LƯU MÔ HÌNH RA FILE JOBLIB
# ==========================================
# Khai báo tên file (bạn có thể đổi đường dẫn tùy ý, vd: '../models/extra_trees_pipeline.joblib')
model_filename = 'extra_trees_pipeline.joblib' 

joblib.dump(extra_trees_pipeline, "extra_trees_pipeline.joblib", compress=3)

print(f"💾 Mô hình đã được lưu thành công vào file: {model_filename}")