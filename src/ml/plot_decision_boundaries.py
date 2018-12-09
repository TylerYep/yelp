from mlxtend.plotting import plot_decision_regions
import matplotlib.pyplot as plt
from algs import load_alg
import util

data = util.load_pkl('data/ml/graph_features.pkl')
alg = load_alg('LinearReg')

clf = alg.clf
X = data.get_joint_matrix(util.features)

train_x = X[data.train_indices]
# train_y = data.labels[data.train_indices]
val_x = X[data.val_indices]
# val_y = data.labels[data.val_indices]
y = data.labels[data.train_indices]
for i in range(len(y)):
    if i > 50:
        y[i] = 1
    else:
        y[i] = 0
print(train_x[:, :2].shape)
print(y.shape)

# Plot Decision Region using mlxtend's awesome plotting function
plot_decision_regions(X=train_x, y=y, clf=clf, legend=2, filler_feature_values={2: 47, 3: 284, 4: 19, 5: 1, 6: 1},
                            filler_feature_ranges={2: 1, 3: 1, 4: 1, 5: 1, 6: 1})

# Update plot object with X/Y axis labels and Figure Title
# plt.xlabel(X.columns[0], size=14)
# plt.ylabel(X.columns[1], size=14)
plt.title('SVM Decision Region Boundary', size=16)
plt.show()