from mlxtend.plotting import plot_decision_regions
import matplotlib.pyplot as plt
from algs import load_alg
import util
from feature_data import DataFeatures

data = util.load_pkl('data/ml/graph_features.pkl')
alg = load_alg('Random_Forest')

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


# Fix feature values
feature_ind = [1, 2]
filler_vals = {0: 1, 3: 1, 4: 1, 5: 1}
filler_ranges = {0: 1, 3: 1, 4: 1, 5: 1}
# feature_cols = {0 : 'degree', 1: 'clustering', 2: 'comm_edge_density',
#                 3: 'comm_sz', 4: 'comm_review_count', 5: 'split'}

plot_x = train_x.copy()
for col in filler_vals:
    plot_x[:, col] = 1
plot_y = y.copy()

print(plot_x)
print(plot_y)

# Plot Decision Region using mlxtend's awesome plotting function
plot_decision_regions(X=plot_x, y=plot_y, clf=clf, legend=2, feature_index=feature_ind,
                            filler_feature_values=filler_vals, filler_feature_ranges=filler_ranges)

# Update plot object with X/Y axis labels and Figure Title
# plt.xlabel(X.columns[0], size=14)
# plt.ylabel(X.columns[1], size=14)
plt.title('Decision Region Boundary', size=16)
plt.show()