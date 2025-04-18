# Autogenerated from python.template file

from quixstreams import Application
from quixstreams.models import TopicConfig
import seaborn as sns

from river import metrics, preprocessing
from river import cluster
import matplotlib.pyplot as plt
from river import ensemble
from river import optim
from sklearn.metrics import confusion_matrix
from river import compose
from river import preprocessing
import json

import dill
import numpy as np


# Define an application that will connect to Kafka
app = Application(
    broker_address="localhost:39092",  # Kafka broker address
    auto_offset_reset="earliest",
    consumer_group="KMeans9",
)

# Define the Kafka topics
input_topic = app.topic("clusters", value_deserializer="json")

output_topic = app.topic("KMeans-results",
                         # Create a Streaming DataFrame connected to the input Kafka topic
                         value_serializer="json")
sdf = app.dataframe(topic=input_topic)


# Define River Model
model = (

    cluster.KMeans(

        n_clusters=2,
        halflife=0.1,
        sigma=3,
        seed=42,

    ))


# Define new features


# Drop features


# Define metrics
metric = metrics.Silhouette()

Silhouette = []


# Variables for plotting
x_axis = []
y_axis = []

y_true = []
y_pred = []


# Function for training the model
def train_and_predict(X):

    model.learn_one(X)

    y_predicted = model.predict_one(X)

    # Update metric
    metric.update(X, y_predicted,  model.centers)

    print(metric)
    Silhouette.append(metric.get())

    with open('KMeans.pkl', 'wb') as model_file:
        dill.dump(model, model_file)

    x_axis.append(X["0"])
    y_axis.append(X["1"])

    # in some cases model returns one (e.g first learn one iteration in OneVsOneClassifier)
    # so we check if y_pred is not None to add to the lists
    if y_predicted is not None:

        y_pred.append(y_predicted)

    return {
        **X,

        "Prediction": y_predicted,
        "Silhouette": metric.get()

    }


# Apply the train_and_predict function to each row in the filtered DataFrame
sdf = sdf.apply(train_and_predict)

# Output topic
# Run the streaming application (app automatically tracks the sdf!)
sdf = sdf.to_topic(output_topic)
app.run()


centers = np.array([list(model.centers[i].values()) for i in model.centers])
x_axis = np.array(x_axis)
y_axis = np.array(y_axis)
center_colors = [plt.cm.viridis(i / (len(centers) - 1))
                 for i in range(len(centers))]

# Scatter plot: Data points with cluster colors
plt.scatter(x_axis, y_axis, c=y_pred,
            cmap="viridis", alpha=0.6, edgecolors="k", label="Points")


for i, center in enumerate(centers):
    plt.scatter(center[0], center[1], c=[center_colors[i]],
                marker='x', s=200, label=f"Cluster {i} Center")
plt.title('Cluster Centers')
plt.xlabel("0")
plt.ylabel("1")
plt.legend()
plt.show()


plt.plot(Silhouette)
plt.xlabel('Iterations')
plt.ylabel('Silhouette')
plt.title('Silhouette over Training Iterations')
plt.show()
