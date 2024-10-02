import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Dữ liệu từ bảng kết quả phân lớp
data = {
    "True": {"True": 50, "False": 3, "Unknown": 10},
    "False": {"True": 1, "False": 35, "Unknown": 17},
    "Unknown": {"True": 1, "False": 1, "Unknown": 64},
}

# Tạo ma trận confusion
confusion_matrix = np.zeros((3, 3))
labels = ["True", "False", "Unknown"]

for i, row_label in enumerate(labels):
    for j, col_label in enumerate(labels):
        confusion_matrix[i, j] = data[row_label][col_label]

confusion_matrix = confusion_matrix.astype(int)

# Vẽ confusion matrix bằng seaborn
sns.heatmap(
    confusion_matrix,
    annot=True,
    fmt="d",
    xticklabels=labels,
    yticklabels=labels,
    cmap="Blues",
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
# plt.title("Confusion Matrix")
plt.show()
