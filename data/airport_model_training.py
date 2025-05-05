#Training a model to locate the airports.
"""
import numpy as np
from sklearn.cluster import KMeans
import joblib
import matplotlib.pyplot as plt

# Step 1: Airport coordinates (IATA → (lat, lon))
airport_coords = {
    'ATL': (33.6407, -84.4277), 'LAX': (33.9416, -118.4085), 'ORD': (41.9742, -87.9073),
    'DFW': (32.8998, -97.0403), 'DEN': (39.8561, -104.6737), 'JFK': (40.6413, -73.7781),
    'SFO': (37.6213, -122.3790), 'SEA': (47.4502, -122.3088), 'LAS': (36.0840, -115.1537),
    'MCO': (28.4312, -81.3081), 'CLT': (35.2140, -80.9431), 'EWR': (40.6895, -74.1745),
    'PHX': (33.4342, -112.0116), 'MIA': (25.7959, -80.2870), 'IAH': (29.9902, -95.3368),
    'BOS': (42.3656, -71.0096), 'MSP': (44.8848, -93.2223), 'FLL': (26.0726, -80.1527),
    'DTW': (42.2162, -83.3554), 'PHL': (39.8744, -75.2424), 'LGA': (40.7769, -73.8740),
    'BWI': (39.1754, -76.6684), 'SLC': (40.7899, -111.9791), 'SAN': (32.7338, -117.1933),
    'TPA': (27.9755, -82.5332), 'HNL': (21.3245, -157.9251), 'PDX': (45.5898, -122.5951),
    'DAL': (32.8471, -96.8517), 'STL': (38.7487, -90.3700), 'AUS': (30.1975, -97.6664),
    'RDU': (35.8776, -78.7875), 'MCI': (39.2976, -94.7139), 'OAK': (37.7126, -122.2197),
    'SMF': (38.6951, -121.5908), 'SJC': (37.3627, -121.9290), 'IND': (39.7173, -86.2944),
    'CLE': (41.4117, -81.8498), 'PIT': (40.4915, -80.2329), 'CMH': (39.9980, -82.8919),
    'CVG': (39.0488, -84.6675), 'JAX': (30.4941, -81.6879), 'MSY': (29.9934, -90.2580),
    'MKE': (42.9472, -87.8966), 'SAT': (29.5337, -98.4698), 'SNA': (33.6757, -117.8678),
    'ONT': (34.0559, -117.6005), 'BUF': (42.9405, -78.7322), 'PBI': (26.6832, -80.0956),
    'BOI': (43.5644, -116.2228), 'ANC': (61.1743, -149.9983), 'BNA': (36.1263, -86.6774),
    'RNO': (39.4991, -119.7681), 'OMA': (41.3032, -95.8941), 'OKC': (35.3931, -97.6007),
    'TUL': (36.2007, -95.8881), 'ABQ': (35.0494, -106.6170), 'RIC': (37.5052, -77.3197),
    'CHS': (32.8980, -80.0405), 'ALB': (42.7481, -73.8029), 'SAV': (32.1276, -81.2021),
    'TYS': (35.8110, -83.9940), 'BHM': (33.5629, -86.7535), 'GSO': (36.0978, -79.9373),
    'DSM': (41.5341, -93.6631), 'GRR': (42.8808, -85.5228), 'LEX': (38.0366, -84.6059),
    'ELP': (31.8072, -106.3776), 'LIT': (34.7294, -92.2245), 'FAT': (36.7762, -119.7181),
    'SDF': (38.1744, -85.7360), 'COS': (38.8058, -104.7000), 'PSP': (33.8297, -116.5070),
    'GEG': (47.6253, -117.5372), 'MYR': (33.6827, -78.9283), 'ECP': (30.3571, -85.7954),
    'PWM': (43.6462, -70.3093), 'BTV': (44.4711, -73.1533), 'GSP': (34.8957, -82.2189),
    'MDT': (40.1935, -76.7634), 'AVL': (35.4362, -82.5419), 'BZN': (45.7775, -111.1523),
    'XNA': (36.2819, -94.3068), 'ICT': (37.6499, -97.4331), 'SRQ': (27.3954, -82.5540),
    'MLI': (41.4485, -90.5075), 'TLH': (30.3965, -84.3503), 'MSN': (43.1399, -89.3375),
    'FSD': (43.5820, -96.7419), 'CAK': (40.9161, -81.4422), 'ROA': (37.3255, -79.9754),
    'JAN': (32.3112, -90.0759), 'CRP': (27.7742, -97.5122), 'SPI': (39.8441, -89.6779),
    'DAB': (29.1799, -81.0581), 'BGR': (44.8074, -68.8281)
}

# Step 2: Prepare data
airport_codes = list(airport_coords.keys())
coords = np.array(list(airport_coords.values()))

# Step 3: Fit K-Means model
k = 40  # You can adjust this
kmeans = KMeans(n_clusters=k, random_state=42)
labels = kmeans.fit_predict(coords)

# Step 4: Save model
joblib.dump(kmeans, 'airport_kmeans_model.pkl')

# Step 5: (Optional) Visualize clusters
colors = plt.cm.get_cmap('tab10', k)
plt.figure(figsize=(10, 6))

for i, coord in enumerate(coords):
    plt.scatter(coord[1], coord[0], color=colors(labels[i]), label=f"{airport_codes[i]} (C{labels[i]})", s=25)

plt.title("K-Means Clustering of US Airports")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 6: Print cluster assignments
for i, code in enumerate(airport_codes):
    print(f"{code}: Cluster {labels[i]}")"
"""