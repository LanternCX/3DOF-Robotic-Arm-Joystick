import pygame
import time
import serial

pygame.init()
pygame.joystick.init()

joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("Unable to find any controller！")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Connect to controller: {joystick.get_name()}")

ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)

speed_mode = True

control_val = {
    "A": 0,
    "B": 0,
    "X": 0,
    "Y": 0,
    "LEFT_SHOULDER": 0,
    "RIGHT_SHOULDER": 0,
    "LEFT_THUMB": 0,
    "RIGHT_THUMB": 0,
    "LEFT_TRIGGER": 0.0,
    "RIGHT_TRIGGER": 0.0,
    "LEFT_JOYSTICK_X": 0.0,
    "LEFT_JOYSTICK_Y": 0.0,
    "RIGHT_JOYSTICK_X": 0.0,
    "RIGHT_JOYSTICK_Y": 0.0
}

handle_map = {
    0: "LEFT_JOYSTICK_X",
    1: "LEFT_JOYSTICK_Y",
    2: "RIGHT_JOYSTICK_X",
    3: "RIGHT_JOYSTICK_Y",
    4: "RIGHT_TRIGGER",
    5: "LEFT_TRIGGER"
}

# main loop
try:
    while True:
        command = ''
        # Handle Controller Event
        for event in pygame.event.get():
            # Trigger and Joystick event
            if event.type == pygame.JOYAXISMOTION:
                for axis in range(joystick.get_numaxes()):
                    axis_value = joystick.get_axis(axis)
                    # print(f"Handle {axis} value: {axis_value:.2f}")
                    if axis in handle_map and abs(axis_value) > 0.1:
                        control_val[handle_map[axis]] = axis_value
                    else :
                        control_val[handle_map[axis]] = 0.0
            # Button Event：X -> CATCH ON；Y -> CATCH OFF
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    speed_mode = not speed_mode
                    print("Speed mode " + "ON" if speed_mode else "OFF")
                if event.button == 2:  # X 按下
                    command = "CATCH ON"
                elif event.button == 3:  # Y 按下
                    command = "CATCH OFF"

        # print(f"x_speed: {control_val['LEFT_JOYSTICK_Y']}, y_speed：{control_val['RIGHT_JOYSTICK_X']}")

        # 计算第四个参数：左板机为正，右板机为负
        # 负闭合 正张开
        trigger_val = int(control_val['LEFT_TRIGGER'] * 100 - control_val['RIGHT_TRIGGER'] * 100)

        if speed_mode:
            command = (
                    "SPEED "
                    + str(int(control_val['RIGHT_JOYSTICK_Y'] * 50)) + ' '
                    + str(int(control_val['LEFT_JOYSTICK_Y'] * 50)) + ' '
                    + str(int(control_val['RIGHT_JOYSTICK_X'] * 50)) + ' '
                    + str(trigger_val)
            )
        ser.write((command + "\n").encode())
        print("Tx: " + command)

        # if ser.in_waiting:
        #     line = ser.readline().decode(errors='ignore').strip()
        #     if line:
        #         print("Rx：", line)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Keyboard interrupt")
finally:
    pygame.quit()
