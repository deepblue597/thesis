
# Autogenerated using jinja files
from quixstreams import Application
from quixstreams.kafka import ConnectionConfig 
from beaver.pipeline import *
from dash import Dash
from dash.dependencies import Input, Output
from dash import dcc, html
import plotly.graph_objs as go
import threading
from plotly.subplots import make_subplots


from river import linear_model
from river import forest
from river import cluster
from river import drift
from river import ensemble
from river import preprocessing
from river import metrics




model2 = linear_model.ALMAClassifier(
    test = 1,
    lr = 0.1,
    dict = {"name" : [1,2]},
    name = 'HELLOITSME',
    test2 = ['1',2]
)
model3 = forest.ARFClassifier(
    optim = model2
)
model4 = cluster.KMeans(
)
model5 = drift.ADWIN(
)
model6 = ensemble.BaggingClassifier(
)
model8 = preprocessing.StandardScaler(
)
model9 = metrics.MAE(
)
model10 = metrics.MSE(
)



#Define connection
connectionConfig = ConnectionConfig(
    bootstrap_servers = 'localhost:39092',
    security_protocol = 'plaintext',
)

#Connection to Kafka
app = Application( 
    broker_address = connectionConfig,
    consumer_group = 'linear_models',
    auto_offset_reset = 'earliest',
)

#Input topics 

input_topic_testdata1 = app.topic("tester_topic", value_deserializer="json")
input_topic_testdata2 = app.topic("tester_topic", value_deserializer="json")

# Create Streaming DataFrames connected to the input Kafka topics

sdf_testdata1 = app.dataframe(topic=input_topic_testdata1)
sdf_testdata2 = app.dataframe(topic=input_topic_testdata2)

#Drop Features

sdf_testdata1.drop(["drop1"])


#Keep Features

sdf_testdata1 = sdf_testdata1[["keep1","keep2"]]

sdf_testdata2 = sdf_testdata2[["keep1","keep2"]]



# Define new features
sdf_testdata1["comp1"]=sdf_testdata1["keep1"]*sdf_testdata1["keep2"]
sdf_testdata2["comp1"]=sdf_testdata2["keep1"]*sdf_testdata2["keep2"]
sdf_testdata2["comp2"]=sdf_testdata2["keep1"]/sdf_testdata2["keep2"]



#Connect composers with preprocessors 

preprocessor_testdata1 =model8+model8|model8




#Pipeline definition 

testPipeline_pipeline = preprocessor_testdata1 |model4
testPipeline_metrics = [model9,model10]


testPipeline = Pipeline(model = testPipeline_pipeline, model_name ='KMeans'  , metrics_list = testPipeline_metrics , name = "testPipeline",output_topic="output_test")



# Output topics initialization

output_topic_testPipeline = app.topic(testPipeline.output_topic, value_deserializer="json")



#Sdf for each pipeline 
#Train and predict method calls for each pipeline
#If the pipeline has an output topic then we call it 

sdf_testPipeline = sdf_testdata1.apply(testPipeline.train_and_predict).to_topic(output_topic_testPipeline)


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
                    id='live-stats-testPipeline',
                    #style={'margin': 'auto', 'display': 'block', 'width':'70%'}
                )
            ]
        )
    ])

    @dash_app.callback(
        Output('live-graph', 'figure'),
        Input('interval', 'n_intervals')
    )
    def update_graph(n):
        fig = make_subplots(rows=1, cols=1 , vertical_spacing=0.1)

        
        testPipeline.add_metrics_traces(fig = fig , row = 1, col = 1 ) 
        

        fig.update_layout(height=600, title="Live Metrics", margin=dict(t=40, b=40), showlegend=True )
        return fig


    
    @dash_app.callback(
        Output(
            component_id='live-stats-testPipeline', 
            component_property='figure'
        ), 
        Input(
            component_id='interval', 
            component_property='n_intervals'
        )
    )

      
    def update_stats_testPipeline(n):
        
        traces = []  
        
        testPipeline.add_stats_traces(traces) 
              

        
        if traces:
            fig = go.Figure(
                    data=traces, 
                    layout= go.Layout(
                        title='testPipeline Statistics'
                    )
            )
            return fig    
    
        return go.Figure()
    
    dash_app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    #Run Plotly on different thread
    threading.Thread(target=run_dash, daemon=True).start()
   
    # Run Quix Streams 
    app.run()