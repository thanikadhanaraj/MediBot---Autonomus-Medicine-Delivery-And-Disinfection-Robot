/* Master ESP32 (Board B)
   - existing TM1637 display logic (display_number)
   - pulses SERVO_OUT_PIN when /servo_trigger received
*/

#include <Arduino.h>
#include <WiFi.h>
#include <micro_ros_arduino.h>
#include <TM1637Display.h>

// micro-ROS core headers
extern "C" {
  #include <rcl/rcl.h>
  #include <rcl/error_handling.h>
  #include <rclc/executor.h>
  #include <rclc/rclc.h>
  #include <rclc/subscription.h>
  #include <std_msgs/msg/int32.h>
}

// -------- CONFIG - EDIT THESE ----------
#define WIFI_SSID     "11R5G"
#define WIFI_PASSWORD "12345612"
#define AGENT_IP      "172.29.29.3"
#define AGENT_PORT    8888

// TM1637 pins (your values)
#define CLK_PIN 22
#define DIO_PIN 21

// Existing control pin to slave for purple LED (keep your pin)
#define CONTROL_PIN 18

// NEW: pin used to pulse servo trigger to the slave
#define SERVO_OUT_PIN 19

// Countdown interval (ms)
#define COUNTDOWN_INTERVAL_MS 1000UL
// ---------------------------------------

TM1637Display display(CLK_PIN, DIO_PIN);

// micro-ROS objects
rcl_subscription_t display_sub;
rcl_subscription_t servo_sub;
std_msgs_msg_Int32 recv_msg;
std_msgs_msg_Int32 servo_recv_msg;
rclc_executor_t executor;
rcl_allocator_t allocator;
rcl_node_t node;
rclc_support_t support;

// Countdown state
volatile int display_value = 0;
volatile bool countdown_active = false;
unsigned long next_tick_ms = 0;
unsigned long led_end_time_ms = 0;

void display_callback(const void * msgin)
{
  const std_msgs_msgInt32 * msg = (const std_msgsmsg_Int32 *)msgin;
  int number = msg->data;
  if (number < 0) number = 0;
  if (number > 99) number = 99;

  display_value = number;
  countdown_active = true;
  next_tick_ms = millis() + COUNTDOWN_INTERVAL_MS;

  if (number > 0) {
    led_end_time_ms = millis() + (unsigned long)number * 1000UL;
    digitalWrite(CONTROL_PIN, HIGH);
  } else {
    led_end_time_ms = 0;
    digitalWrite(CONTROL_PIN, LOW);
  }

  display.clear();
  display.showNumberDecEx(display_value, 0, true, 2, 1);
}

void servo_callback(const void * msgin)
{
  const std_msgs_msgInt32 * msg = (const std_msgsmsg_Int32 *)msgin;
  Serial.print("[master] servo trigger received: ");
  Serial.println(msg->data);

  // short pulse to slave
  digitalWrite(SERVO_OUT_PIN, HIGH);
  delay(120); // short rising pulse
  digitalWrite(SERVO_OUT_PIN, LOW);
  Serial.println("[master] servo pulse sent");
}

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("Master booting...");

  // TM1637 init
  display.setBrightness(0x0f);
  display.clear();

  pinMode(CONTROL_PIN, OUTPUT);
  digitalWrite(CONTROL_PIN, LOW);

  pinMode(SERVO_OUT_PIN, OUTPUT);
  digitalWrite(SERVO_OUT_PIN, LOW);

  // Connect Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // micro-ROS WiFi transport
  set_microros_wifi_transports((char*)WIFI_SSID, (char*)WIFI_PASSWORD, (char*)AGENT_IP, AGENT_PORT);

  // rclc init
  allocator = rcl_get_default_allocator();
  rclc_support_init(&support, 0, NULL, &allocator);
  rclc_node_init_default(&node, "esp32_display_node", "", &support);

  // subscriptions
  rclc_subscription_init_default(
    &display_sub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "display_number"
  );

  rclc_subscription_init_default(
    &servo_sub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "servo_trigger"
  );

  // executor with 2 subscriptions
  rclc_executor_init(&executor, &support.context, 2, &allocator);
  rclc_executor_add_subscription(&executor, &display_sub, &recv_msg, &display_callback, ON_NEW_DATA);
  rclc_executor_add_subscription(&executor, &servo_sub, &servo_recv_msg, &servo_callback, ON_NEW_DATA);

  Serial.println("micro-ROS initialized, waiting for messages...");
}

void loop()
{
  // Keep micro-ROS executor alive
  rclc_executor_spin_some(&executor, RCL_MS_TO_NS(50));

  // Countdown tick logic
  if (countdown_active) {
    unsigned long now = millis();
    if (now >= next_tick_ms) {
      if (display_value > 0) {
        display_value--;
        display.clear();
        display.showNumberDecEx(display_value, 0, true, 2, 1);
      }
      next_tick_ms += COUNTDOWN_INTERVAL_MS;

      if (display_value <= 0) {
        countdown_active = false;
        display_value = 0;
        digitalWrite(CONTROL_PIN, LOW);
        led_end_time_ms = 0;
        Serial.println("Countdown finished.");
      }
    }
  }

  // Ensure control line is turned off when time expired
  if (led_end_time_ms != 0 && millis() >= led_end_time_ms) {
    digitalWrite(CONTROL_PIN, LOW);
    led_end_time_ms = 0;
    Serial.println("Control line turned OFF (timeout).");
  }

  delay(5);
}