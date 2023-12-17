#include <stdio.h>
#include <stdlib.h>
#include <webots/robot.h>
#include <webots/motor.h>
#include <webots/distance_sensor.h>

#define NUM_SENSORS 9
#define OBSTACLE_THRESHOLD 15
#define AVERAGE_WINDOW 5

static WbDeviceTag sensors[NUM_SENSORS], left_motor, right_motor;
static int time_step = 0;
static double max_speed = 19.1;

static double average_sensor_value = 0;
static int average_count = 0;

static void initialize() {
  wb_robot_init();
  time_step = wb_robot_get_basic_time_step();

  char sensor_name[5];
  for (int i = 0; i < NUM_SENSORS; i++) {
    sprintf(sensor_name, "ds%d", i);
    sensors[i] = wb_robot_get_device(sensor_name);
    wb_distance_sensor_enable(sensors[i], time_step);
  }

  left_motor = wb_robot_get_device("left wheel motor");
  right_motor = wb_robot_get_device("right wheel motor");
  wb_motor_set_position(left_motor, INFINITY);
  wb_motor_set_position(right_motor, INFINITY);
  wb_motor_set_velocity(left_motor, max_speed);
  wb_motor_set_velocity(right_motor, max_speed);
}

int main() {
  initialize();

  while (wb_robot_step(time_step) != -1) {
    double front_sensor_value = wb_distance_sensor_get_value(sensors[3]);
    
    average_sensor_value = ((average_sensor_value * average_count) + front_sensor_value) / (average_count + 1);
    average_count = (average_count < AVERAGE_WINDOW) ? average_count + 1 : AVERAGE_WINDOW;

    printf("Average front sensor value: %lf\n", average_sensor_value);

    if (average_sensor_value > OBSTACLE_THRESHOLD) {
      wb_motor_set_velocity(left_motor, 0.0);
      wb_motor_set_velocity(right_motor, 0.0);
    } else {
      wb_motor_set_velocity(left_motor, max_speed);
      wb_motor_set_velocity(right_motor, max_speed);
    }
  }

  return 0;
}
