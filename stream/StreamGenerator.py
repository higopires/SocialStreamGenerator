import paho.mqtt.client as mqtt
import pandas as pd
import json
import pprint
def convert_date(df, columns=['timestamp']):
    for col in columns:
        df[col] = pd.to_datetime(df[col], unit='s', utc=True).dt.tz_convert(
            'US/Eastern')
    return df

def read_data(name):
    conversation_data = pd.read_csv('../sensing/Conversations/conversation_'+name+'.csv')
    return conversation_data


#broker = 'iot.eclipse.org'
broker = '127.0.0.1' #endereço do broker
pub_topic = 'social' # tópico para publicar o fluxo
sub_topic_abnormal = 'com/lsdi/sociability/MONDAY_/AbnormalBehavior' # sub. notificações Comp. Anormal
sub_topic_change = 'com/lsdi/sociability/MONDAY_/ChangeBehavior'   # sub. notificações Mudança Rotina
sub_topic_pattern = 'com/lsdi/sociability/MONDAY_/newPattern' # sub. notificações Comp. Anormal

client = mqtt.Client(client_id="Ivan", clean_session=True, userdata=None, transport="tcp")
print("connecting to broker")
client.connect(broker,port=1883,) #connect to broker

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    #Subscreve
    client.subscribe(sub_topic_abnormal)
    client.subscribe(sub_topic_change)
    client.subscribe(sub_topic_pattern)
    print("Publishing message to topic", pub_topic)


def on_message(client, userdata, message):
    socialEvent = message.payload.decode("utf-8")
    json_object = json.loads(socialEvent)
    print('---------------- Notification --------------------- ')
    pprint.pprint(json_object)
    print('\n')
    #json_formatted_str = json.dumps(json_object, )
    #print(json_formatted_str)

client.on_connect = on_connect
client.on_message = on_message


#ler o dataset
uids = 'u00', 'u02', 'u04', 'u05', 'u08', 'u09', 'u10', 'u12', 'u13', 'u14', 'u17', 'u23', 'u27', 'u30', 'u31', 'u36', 'u51', 'u53', 'u56', 'u57', 'u59'
uid = 'u04'
conv_data = read_data(uid)
convert_date(conv_data, columns=['start_timestamp', 'end_timestamp'])
conv_data['week_group'] = conv_data['start_timestamp'].dt.to_period('W-THU')
conv_data.index = conv_data['start_timestamp']

#publicar eventos sociais
for timestamp in conv_data['start_timestamp']:
    time = str((timestamp))[0:19]
    client.publish(pub_topic, payload=time, qos=2, retain=True)

client.loop_forever()