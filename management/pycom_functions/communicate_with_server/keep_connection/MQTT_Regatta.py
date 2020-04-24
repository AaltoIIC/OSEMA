"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, client, header_ts):
    header_ts = convert_to_epoch(header_ts)
    for value_pair in data_with_ts:
        timestamp = header_ts + int(value_pair[1] / 1000)
        data_string = format_data(timestamp, value_pair[0])
        try:
            client.publish(topic=TOPIC, msg=data_string)
        except:
            print("Data couldn't be published, resetting board!")
            machine.reset()
