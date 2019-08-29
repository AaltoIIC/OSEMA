"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, client, header_ts):
    #constructing data string
    data_string = format_data(header_ts, data_with_ts)
    try:
        client.publish(topic=TOPIC, msg=data_string)
    except:
        print("Data couldn't be published, resetting board!")
