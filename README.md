 # MediBot - Autonomus Medicine Delivery And Disinfection Robot
MediBot is an autonomous hospital robot designed to reduce nurse fatigue by taking over repetitive medicine delivery and room-disinfection tasks. It minimizes infection risks, shortens staff workload, and ensures safer, faster, and more reliable patient-care operations.

https://www.youtube.com/watch?v=1O8xAjmjDDk
## Problem Statement 1:
Nurses in hospitals frequently perform exhausting and repetitive tasks such as collecting medicines from the pharmacy and delivering them to patient rooms. This constant movement leads to fatigue, reduced efficiency, and increases the likelihood of human errors, which can compromise patient safety. Moreover, frequent direct contact between nurses/doctors and patients increases the chance of transmitting new germs—both from staff to patients and from patients to staff—especially in contagious environments. 
![problem11](https://github.com/user-attachments/assets/1bfaf9c1-9117-4fee-9d41-5631c09d2367)
![problem12](https://github.com/user-attachments/assets/5246a6fe-ea55-4fcd-b4f5-ea9563c39cf3)

## Problem Statement 2:
Hospitals are environments where infectious pathogens can remain active for long periods, posing serious health risks to both patients and medical staff. Manual cleaning and disinfection methods are often inconsistent, time-consuming, and expose cleaning personnel to harmful microorganisms. Due to the continuous movement of patients, doctors, and nurses, maintaining a consistently sterile environment becomes difficult.
![problem2](https://github.com/user-attachments/assets/5f58607e-3f0d-423b-97e0-50db37f25a2a)
![problem22](https://github.com/user-attachments/assets/b617ff6c-4bbe-44e5-a121-41b2bc9919b1)

## Proposed Solution:
To address both challenges—nurse fatigue caused by repetitive medicine delivery tasks and inconsistent room disinfection—MediBot provides a fully autonomous, safe, and reliable robotic solution designed specifically for hospital environments.

MediBot combines computer vision, autonomous navigation, microcontroller-based actuation, and UV-C disinfection technology to perform two critical healthcare operations without requiring human intervention:

## 1. Autonomous Medicine Delivery

MediBot independently travels from the pharmacy to assigned patient rooms using ArUco-based vision navigation.
Once it reaches the designated room, a servo-powered dispensing mechanism automatically drops the medication, ensuring accurate and contact-free delivery.
This reduces nurse workload, prevents fatigue, and minimizes direct human–patient contact, thereby lowering cross-infection risks.

## 2. Automated UV Disinfection

MediBot autonomously navigates to rooms requiring sanitization.
Using a WiFi-connected micro-ROS control system, the robot activates a UV-C disinfectant LED mounted  on a ESP32-C6 microcontroller.
The robot waits inside the room for a fixed UV exposure time (e.g., 10 seconds), ensuring effective pathogen inactivation.
This ensures consistent, timed, and safe disinfection of rooms, reducing infection spread and protecting both medical staff and patients.

![pic1](https://github.com/user-attachments/assets/92dcded2-4271-49db-b61d-3617a9ee080f)

## Key Features:

Hands-free operation: Fully automated from start to finish.
Real-time status feedback: ROS2 topics report delivery, dispensing, and disinfection states.
Vision-guided precision: ArUco markers ensure centimetre-level accuracy in navigation.
Safe & non-invasive: Avoids unnecessary human exposure to UV-C radiation and infectious surfaces.

![flow diagram final](https://github.com/user-attachments/assets/fc3c37d7-8a23-4e60-a378-0f45139dc0ea)

Here are the components I have used for this MediBot. I’ve created a custom DigiKey My-List that includes the manufacturer part numbers for each item. You can view the complete list using the link below.

Link: https://www.digikey.in/en/mylists/list/USJJ9KHIO1

![component1](https://github.com/user-attachments/assets/559c15aa-361e-4f5e-8054-0ebc407af563)

![component 2](https://github.com/user-attachments/assets/12fb368f-69dc-41e2-b4e6-256986341187)
![components3](https://github.com/user-attachments/assets/cc994e95-4478-43f0-9a05-16903089532b)
![component 4](https://github.com/user-attachments/assets/89571028-1b33-46e2-a31c-a99b896a5346)
![component5](https://github.com/user-attachments/assets/f4740726-70b5-48c2-811f-d5689818991f)![component6](https://github.com/user-attachments/assets/f8ba5d6e-17ef-4bbd-a939-72257683cec7)
![component7](https://github.com/user-attachments/assets/58805e40-0ad5-4394-b2d2-9f70b57f5d50)
![component8](https://github.com/user-attachments/assets/5dd3a2fa-022b-4932-b80d-2dbacbf74fe2)![component 9](https://github.com/user-attachments/assets/0288db60-dfa7-4ce2-aa83-abe89ce3f7a4)

## Building MediBot:
![area](https://github.com/user-attachments/assets/90d5fc05-ee0e-49cc-a19a-2e915548bdfd)
### Step 1 — Assemble the Robot Chassis
#### 1.1 Components Required

4 × DG01D geared motors
4 × Omni-wheels / Mecanum wheels
Acrylic base plate (your 3mm–5mm sheet)
Screws, nuts, standoffs
3D-printed motor mounts (your custom piece)
Battery pack

#### 1.2 Mount the Motors

Align the DG01D motors with the 3D-printed holders.
Place holders at each corner of the acrylic base.
Screw the holders firmly using M3 screws.
Attach the Omni wheels to each DG01D motor shaft.

![WhatsApp Image 2025-11-26 at 221114_6080f05b(0)](https://github.com/user-attachments/assets/26b52cbd-c0e2-4ce6-b823-fd0de6cc8011)

![WhatsApp Image 2025-11-20 at 093339_67e93bf0](https://github.com/user-attachments/assets/eada0f05-a620-47b4-9c70-034c314e9f36)

#### 1.3 Fix the Top Plate

Use 25mm standoffs to mount a second acrylic sheet above the motors.
This plate will hold your ESP32 boards, power distribution, and wiring.

### Step 2 — Install Motor Driver & Drive ESP32 DEVKITV1 (Board A)
### 2.1 Components

ESP32 DEVKIT V1 – Board A
L298N or L9110S motor drivers 
Jumper wires
Common Ground

### 2.2 Wiring Motor Drivers to ESP32 (Board A)

<img width="747" height="505" alt="image" src="https://github.com/user-attachments/assets/26b9ba98-de10-445e-9fc6-438950139afc" />
![ESP32driver board](https://github.com/user-attachments/assets/0fdff685-18f2-46f9-9574-c0ffc3da5673)
![Motordriver](https://github.com/user-attachments/assets/01a73445-96a0-46d0-9007-63d4e8aee51b)


## Step 3 — Install Master ESP32 DEVKITV1 (Board B)
This board controls:

1.TM1637 timer
2.Servo trigger output
3.Disinfection trigger output
4.micro-ROS topics:
    /display_number
    /servo_trigger

### 3.1 Wiring 

![WhatsApp Image 2025-11-21 at 212938_c5522bef](https://github.com/user-attachments/assets/17aca216-4791-46b1-b78d-08e85926ac5f)
![WhatsApp Image 2025-11-21 at 212939_08b3bfc4](https://github.com/user-attachments/assets/81c35d65-b4cc-415a-b0ca-b77bfeeafb3e)

Step 5 — Camera & ArUco Setup
5.1 Mount the Camera

Fix a USB webcam 1.5m–2m above ground.
Ensure the ArUco marker on robot is always visible.
5.2 Generate ArUco Marker

You already have one.
Print at 5cm × 5cm for accurate pose.
