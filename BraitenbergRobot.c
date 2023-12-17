#include <stdio.h>
#include <stdlib.h>
#include <webots/camera.h>
#include <webots/distance_sensor.h>
#include <webots/motor.h>
#include <webots/robot.h>

#define NUM_SENSORS 9
#define RANGE (1024 / 2)
#define BOUND(x, a, b) (((x) < (a)) ? (a) : ((x) > (b)) ? (b) : (x))

static WbDeviceTag sensors[NUM_SENSORS], left_motor, right_motor;
static double matrix[NUM_SENSORS][2] = {
    {-5000, -5000},  {-20000, 40000}, {-30000, 50000}, {-70000, 70000}, {70000, -60000},
    {50000, -40000}, {40000, -20000}, {-5000, -5000},  {-10000, -10000}
};
static double range = RANGE;
static int time_step = 0;
static double max_speed = 19.1;
static double speed_unit = 0.00053429;

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
  wb_motor_set_velocity(left_motor, 0.0);
  wb_motor_set_velocity(right_motor, 0.0);
}

int main() {
  initialize();

  while (wb_robot_step(time_step) != -1) {
    double speed[2] = {0.0, 0.0};
    double sensors_value[NUM_SENSORS];

    for (int i = 0; i < NUM_SENSORS; i++)
      sensors_value[i] = wb_distance_sensor_get_value(sensors[i]);

    for (int i = 0; i < 2; i++) {
      for (int j = 0; j < NUM_SENSORS; j++) {
        speed[i] += speed_unit * matrix[j][i] * (1.0 - (sensors_value[j] / range));
      }
      speed[i] = BOUND(speed[i], -max_speed, max_speed);
    }

    wb_motor_set_velocity(left_motor, speed[0]);
    wb_motor_set_velocity(right_motor, speed[1]);
  }

  return 0;
}
