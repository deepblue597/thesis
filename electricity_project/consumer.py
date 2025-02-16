from quixstreams import Application
from quixstreams.models import TopicConfig
from river import time_series

import pickle


# A minimal application reading temperature data in Celsius from the Kafka topic,
# converting it to Fahrenheit and producing alerts to another topic.

# Define an application that will connect to Kafka
app = Application(
    broker_address="localhost:39092",  # Kafka broker address
    auto_offset_reset="earliest",
    consumer_group="model-electricity-snarimax",
)


read_topic = app.topic("electricity-24", value_deserializer="json")
write_topic = app.topic("model-hist-var-24",
                        value_serializer="json")


# Create a Streaming DataFrame connected to the input Kafka topic
sdf = app.dataframe(topic=read_topic)

# select only the columns we need
sdf_filtered = sdf[['Datetime (UTC)', 'Carbon Intensity gCO₂eq/kWh (direct)']]


# River model

period = 24
model = time_series.SNARIMAX(
    p=1,
    d=1,
    q=1,
    m=24,
    sd=1

)
print('model created')


# learn and predict method

# Function to train the model on each row of data


def train_and_predict(row):

    y = row['Carbon Intensity gCO₂eq/kWh (direct)']

    # Train the model
    model.learn_one(y)

    # print('model updated')

    with open('SNARIMAX_electricity_h.pkl', 'wb') as model_file:
        pickle.dump(model, model_file)

    print('model saved')

    return row


# Apply the train_and_predict function to each row in the filtered DataFrame
sdf_filtered = sdf_filtered.apply(train_and_predict)


sdf_filtered = sdf_filtered.to_topic(write_topic)


# Run the streaming application (app automatically tracks the sdf!)
app.run()
