from envparse import env
import os
import time
from ab2_mqtt import MQTTClient

BASE_SPEED = 40
REVERSE_FACTOR = -1.0

MATRIX = [[1.0, REVERSE_FACTOR],   
          [REVERSE_FACTOR, 1.0]]

DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']
if set(DOCKER_VARENV).issubset(set(os.environ)):
    MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
    MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
else:
    MQTT_HOST = 'localhost'
    MQTT_PORT = 1883

QOS = 0
client = MQTTClient("controller", MQTT_HOST, MQTT_PORT, QOS)

def calculate_motor_speed(sensor_values):
    left_motor_speed = BASE_SPEED
    right_motor_speed = BASE_SPEED

    for i, sensor_value in enumerate(sensor_values):
        if sensor_value == 'True':
            left_motor_speed = MATRIX[i][0] * BASE_SPEED
            right_motor_speed = MATRIX[i][1] * BASE_SPEED

    return left_motor_speed, right_motor_speed

def on_message_sensors(client, userdata, msg):
    sensor_value = msg.payload.decode('utf8')
    
    sensor_values = ['False', 'False']

    if msg.topic == client.TOPIC_OBSTACLE_LEFT:
        sensor_values[0] = sensor_value
    elif msg.topic == client.TOPIC_OBSTACLE_RIGHT:
        sensor_values[1] = sensor_value

    left_motor_speed, right_motor_speed = calculate_motor_speed(sensor_values)

    client.publish(client.TOPIC_MOTORS, f"{left_motor_speed} {right_motor_speed}")

    if 'True' in sensor_values:
        client.publish("log", f"Obstacle detected. Adjusting speed: Left {left_motor_speed}, Right {right_motor_speed}")

client.message_callback_add(client.TOPIC_OBSTACLE_LEFT, on_message_sensors)
client.message_callback_add(client.TOPIC_OBSTACLE_RIGHT, on_message_sensors)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Program stopped by user")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.loop_stop()
    client.disconnect()
