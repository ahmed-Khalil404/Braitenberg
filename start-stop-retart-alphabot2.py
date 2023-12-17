from envparse import env
import os
import time

from ab2_mqtt import MQTTClient

obstacle_detected = False
last_stop_time = 0

def on_message_sensors(client, userdata, msg):
    global obstacle_detected, last_stop_time
    sensor_value = msg.payload.decode('utf8')
    if sensor_value == 'True':
        client.publish(client.TOPIC_MOTORS, "0 0")
        client.publish(client.TOPIC_LEDS, "0x200000 0x000000 0x000000 0x200000")
        buzzer_short(client)
        obstacle_detected = True
    else:
        client.publish(client.TOPIC_MOTORS, "20 20")
        obstacle_detected = False
        last_stop_time = time.time()

def buzzer_short(client):
    client.publish(client.TOPIC_BUZZER, "on")
    time.sleep(0.05)
    client.publish(client.TOPIC_BUZZER, "off")

def on_message_move(client, userdata, msg):
    global obstacle_detected, last_stop_time
    command = msg.payload.decode('utf8')
    current_time = time.time()

    if command == 'stop' or (obstacle_detected and (current_time - last_stop_time) < 5):
        client.publish(client.TOPIC_MOTORS, "0 0")
        client.publish(client.TOPIC_LEDS, "0x000000 0x200000 0x200000 0x000000")
    elif command == 'forward':
        client.publish(client.TOPIC_LEDS, "0x200000 0x000000 0x000000 0x200000")  # Set LED color first
        client.publish(client.TOPIC_MOTORS, "50 50")  # Then start moving forward

def test_motors(client):
    client.publish(client.TOPIC_MOTORS, "20 20")
    time.sleep(0.5)

DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']
if set(DOCKER_VARENV).issubset(set(os.environ)):
    MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
    MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
else:
    MQTT_HOST = 'localhost'
    MQTT_PORT = 1883

QOS = 0
client = MQTTClient("controller", MQTT_HOST, MQTT_PORT, QOS)
client.message_callback_add(client.TOPIC_OBSTACLE_LEFT, on_message_sensors)
client.message_callback_add(client.TOPIC_OBSTACLE_RIGHT, on_message_sensors)
client.message_callback_add(client.TOPIC_MOVE, on_message_move)

try:
    test_motors(client)
    client.loop_forever()
except KeyboardInterrupt:
    print("Program stopped by user")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.loop_stop()
    client.disconnect()
