
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import threading
import json
from datetime import datetime
from snews_pt import snews_sub
subscriber = snews_sub.Subscriber()

app = dash.Dash(__name__)

# Dash app layout
app.layout = html.Div([
    html.H1("Alert Viewer"),
    html.H3("(Updated every 5sec) Last Alert Received:"),
    html.Div([
        dcc.Textarea(id='message-display', readOnly=True, style={'width': '70%', 'height': '200px'}),
        html.Img(id='gif-display', style={'width': '30%', 'height': '200px', 'object-fit': 'contain'}),
    ], style={'display': 'flex'}),
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
    dcc.Interval(id='clock-interval', interval=1000, n_intervals=0),
    html.Div(id='clock-display', style={'font-size': '24px', 'margin-top': '20px'}),
    dcc.Interval(id='table-interval', interval=5000, n_intervals=0),  # Update table every 5 seconds
    html.Div(id='table-display')
])

# Global variables
giphy_snews = "https://raw.githubusercontent.com/SNEWS2/hop-SNalert-app/snews2_dev/hop_comms/auxiliary/snalert.gif"
update_link = "https://cdn.pixabay.com/photo/2016/09/15/18/29/update-1672353_1280.png"
retract_link = "https://d2cbg94ubxgsnp.cloudfront.net/Pictures/380x253/3/4/1/101341_0816cw_comment_retracted_300tb.jpg"
quiet_link = "data:image/jpeg;base64,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"

fmt = '%Y-%m-%d %H:%M:%S'
current_time = datetime.now().strftime(fmt)
collected_messages = [{"timestamp":datetime.now().strftime(fmt),"alert_message": {"None":"No messages received yet", "alert_type":"None"}}]
alert_types = ["COINC_MSG", "COINC_MSG_STAGGERED", "UPDATE", "RETRACTION"]

############################## Subscribe and retrieve the alert messages ##############################
# Function to simulate the behavior of subscribe_and_redirect_alert
def subscribe_and_redirect_alert(outputfolder):
    global collected_messages
    for message in subscriber.subscribe_and_redirect_alert(outputfolder="./stored_alerts", _display=False, _return='message'):
        timestamp = datetime.now().strftime(fmt)
        collected_messages.insert(0, {"timestamp":timestamp, "alert_message":message})

# Thread function to run subscribe_and_redirect_alert
def subscriber_thread():
    subscribe_and_redirect_alert(outputfolder="./")

# Start subscriber thread
subscriber_thread = threading.Thread(target=subscriber_thread)
subscriber_thread.start()

############################## Dash callbacks ##############################
# Callback to update the message display
@app.callback([Output('message-display', 'value'),
               Output('gif-display', 'src')],
              [Input('interval-component', 'n_intervals')])
def update_message_display(n):
    global collected_messages
    text = json.dumps(collected_messages[0]["alert_message"], indent=2)
    alerttime = datetime.strptime(collected_messages[0]["timestamp"], fmt)
    now = datetime.now()
    time_elapsed = (now - alerttime).total_seconds()
    if time_elapsed > 60:
        image = quiet_link
    else:
        if "RETRACT" in collected_messages[0]["alert_message"]["alert_type"]:
            image = retract_link
        elif "UPDATE" in collected_messages[0]["alert_message"]["alert_type"]:
            image = update_link
        else:
            image = giphy_snews
    return text, image

#  Callback to update the clock display
@app.callback(Output('clock-display', 'children'),
              [Input('clock-interval', 'n_intervals')])
def update_clock_display(n):
    global current_time
    current_time = datetime.now().strftime(fmt)
    return f"Current Time: {current_time}"

# Callback to update the table display
@app.callback(Output('table-display', 'children'),
              [Input('table-interval', 'n_intervals')])
def update_table_display(n):
    """
    Update the table display with the collected messages
    """
    global collected_messages

    table_content = []
    for msg in collected_messages:
        timestamp = msg["timestamp"]
        message = msg["alert_message"]
        table_content.append(html.Tr(
            [html.Td(timestamp, style={'white-space': 'nowrap'}),
             html.Td("-"*30),
             html.Td("-"*30)]))
        for key, value in message.items():
            table_content.extend([
                html.Tr([html.Td(timestamp, style={'white-space': 'nowrap'}), html.Td(key), html.Td(value)])
            ])
    return html.Table([html.Tr([html.Th('Timestamp'), html.Th('Key'), html.Th('Value')])] + table_content,
                      style={'width': '100%', 'overflowX': 'auto'}
                      )

if __name__ == '__main__':
    app.run_server(debug=True)
