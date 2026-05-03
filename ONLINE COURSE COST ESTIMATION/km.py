# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

# Plot settings
plt.rcParams['figure.figsize'] = (10, 6)
plt.style.use('ggplot')

# =========================
# Load Excel data (FIXED)
# =========================
data = pd.read_excel("Geethika_data.xlsx")
print("Input Data and Shape")
print(data.shape)
print(data.head())

# =========================
# Prepare data
# =========================
X = data[['Price']].values  # 2D array for sklearn

# =========================
# KMeans Clustering
# =========================
k = 3
kmeans = KMeans(n_clusters=k, n_init=10)
labels = kmeans.fit_predict(X)
centroids = kmeans.cluster_centers_

print("Centroids:")
print(centroids)

# =========================
# Plotting (2D)
# =========================
plt.scatter(X[:, 0], X[:, 0], c=labels, s=30, alpha=0.5)
plt.scatter(centroids[:, 0], centroids[:, 0], c='red', s=100, marker='*')
plt.xlabel("Cycle to Date Usage (MB)")
plt.ylabel("Cycle to Date Usage (MB)")
plt.title("KMeans Clustering")
plt.show()

# =========================
# Save clustered data
# =========================
data['Cluster'] = labels
data.to_csv("data_op.csv", index=False)

# =========================
# 3D Plot (optional)
# =========================
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(X[:, 0], X[:, 0], X[:, 0], c=labels, s=30, alpha=0.5)
ax.scatter(centroids[:, 0], centroids[:, 0], centroids[:, 0],
           marker='*', c='red', s=100)

ax.set_xlabel("Usage")
ax.set_ylabel("Usage")
ax.set_zlabel("Usage")

plt.title("3D View of Clusters")
plt.show()
