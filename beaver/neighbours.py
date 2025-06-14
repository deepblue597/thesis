# Autogenerated from python.template file

from quixstreams import Application
from quixstreams.models import TopicConfig
from quixstreams.kafka import ConnectionConfig 
from pipeline import * 

from river import preprocessing

from dash import Dash
from dash.dependencies import Input, Output
from dash import dcc, html
import plotly.graph_objs as go
import threading

from plotly.subplots import make_subplots
from river import metrics



from river import neighbors






#Define preprocessors
standardScaler = preprocessing.StandardScaler()





#Define metrics
accuracy = metrics.Accuracy()
mae = metrics.MAE()
rmse = metrics.RMSE()


#Define live data algorithms
SWINN = neighbors.SWINN(
    seed =42)
KNNClassifier = neighbors.KNNClassifier(
    engine =SWINN)
KNNRegressor = neighbors.KNNRegressor()


#Connection Configuration for quixstreams
connectionConfig = ConnectionConfig( 
    
    bootstrap_servers ="localhost:39092",
    security_protocol ="plaintext")

#Connection to Kafka 
app = Application( 
    broker_address = connectionConfig,
    consumer_group ="neighboursRegs",
    auto_offset_reset ="earliest")

#Input topics 

input_topic_TrumpApproval = app.topic("TrumpApproval", value_deserializer="json")
input_topic_Phishing = app.topic("Phishing", value_deserializer="json")

# Create Streaming DataFrames connected to the input Kafka topics

sdf_TrumpApproval = app.dataframe(topic=input_topic_TrumpApproval)
sdf_Phishing = app.dataframe(topic=input_topic_Phishing)


# Define new features



#Connect composers with preprocessors 


preprocessor_Phishing =standardScaler



#Pipeline definition 

KNNRegressorPipe_pipeline =KNNRegressor
KNNRegressorPipe_metrics = [rmse]
KNNRegressorPipe = Pipeline(model = KNNRegressorPipe_pipeline , metrics_list = KNNRegressorPipe_metrics ,model_name='KNNRegressor', name = "KNNRegressorPipe",y="five_thirty_eight",output_topic="KNNRegressorBVR")

# KNNClassifierPipe_pipeline = preprocessor_Phishing |KNNClassifier
# KNNClassifierPipe_metrics = [accuracy]
# KNNClassifierPipe = Pipeline(model = KNNClassifierPipe_pipeline , metrics_list = KNNClassifierPipe_metrics, model_name='KNNClassifier' , name = "KNNClassifierPipe",y="class",output_topic="KNNClassifierBVR")

# Output topics initialization

output_topic_KNNRegressorPipe = app.topic(KNNRegressorPipe.output_topic, value_deserializer="json")

# output_topic_KNNClassifierPipe = app.topic(KNNClassifierPipe.output_topic, value_deserializer="json")


#Sdf for each pipeline 
#Train and predict method calls for each pipeline
#If the pipeline has an output topic then we call it 

sdf_KNNRegressorPipe = sdf_TrumpApproval.apply(KNNRegressorPipe.train_and_predict).to_topic(output_topic_KNNRegressorPipe)
# sdf_KNNClassifierPipe = sdf_Phishing.apply(KNNClassifierPipe.train_and_predict).to_topic(output_topic_KNNClassifierPipe)


# ---------- DASHBOARD SETUP ----------

def run_dash():
    dash_app = Dash(__name__)
    dash_app.layout = html.Div([
         html.H2("Pipelines' Plots" , style={
        'textAlign': 'center',  # Center the text

        'fontFamily': 'sans-serif',  # Change the font family
        'font-weight': 'normal',  # Make the text bold
        }),
        dcc.Interval(id='interval', n_intervals=0),
        dcc.Graph(id='live-graph'), 
        html.Div(
            children=[
                dcc.Graph(
                    id='live-stats',
                    style={'margin': 'auto', 'display': 'block', 'width':'70%'}
                )
            ]
        )
    ])

    @dash_app.callback(
        Output('live-graph', 'figure'),
        Input('interval', 'n_intervals')
    )
    def update_graph(n):
        fig = make_subplots(rows=2, cols=1 , vertical_spacing=0.1)

        # Assumes `add_metrics_traces` is defined in your Pipeline class
        KNNRegressorPipe.add_metrics_traces(fig, row=1, col=1)

        fig.update_layout(height=600, title="Live Metrics", margin=dict(t=40, b=40), showlegend=True )
        return fig
    
    
    @dash_app.callback(
        Output(
            component_id='live-stats', 
            component_property='figure'
        ), 
        Input(
            component_id='interval', 
            component_property='n_intervals'
        )
    )    
    def update_stats(n):
        
        traces = []  
        #print('hereee')
        KNNRegressorPipe.add_stats_traces(traces)
        #print(traces) 
        if traces:
            fig = go.Figure(
                    data=traces, 
                    layout= go.Layout(
                        title='Statistics'
                    )
            )
            return fig    
    
        return go.Figure()
    
    dash_app.run(debug=False, use_reloader=False)


# Start Dash in a separate thread
#threading.Thread(target=run_dash, daemon=True).start()


if __name__ == '__main__':
    threading.Thread(target=run_dash, daemon=True).start()
    #update_data()
    # Run Quix Streams 
    app.run()

#Metric plots for each Pipeline

#HoltWintersPipe.metrics_plot()

