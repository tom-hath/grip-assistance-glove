import machine 
import time

flexs = [machine.ADC(machine.pin(1)), machine.ADC(machine.pin(2)),machine.ADC(machine.pin(3)), machine.ADC(machine.pin(4))]

servos = [machine.PWM(machine.pin(5)),machine.PWM(machine.pin(6)), machine.PWM(machine.pin(7)), machine.PWM(machine.pin(8))]

def calibrate(start,finger):
    max = 0 
    min = 0 
    while time.time() - start < 5:
        if flexs[finger].read_u16() > min:
            min = flexs[finger].read_u16()#seems the wrong way round but higher resistance leads to lower voltage value.
        elif flexs[finger].read_u16() < max:
            max = flexs[finger].read_u16()
    return max, min

def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min #linear interpolation for mapping the flex sensor values to servo angles
def setservos(angle,finger):
    servos[finger].duty_u16(int(angle * 65535 / 180))

def main():
    start = time.time()
    max_values = []
    min_values = []
    for i in range(4):
        max, min = calibrate(start, i)
        max_values.append(max)
        min_values.append(min)
    old_value = [0, 0, 0, 0]
    while True:
        for i in range(4):
            flex_value = flexs[i].read_u16()
            if flex_value > old_value[i]:
                servo_value = map_value(min_values[i], min_values[i], max_values[i], 0, 180)#releasing the servos if finger is straightening
            else:
                servo_value = map_value(flex_value, min_values[i], max_values[i], 0, 180) #map the flex sensor value to a servo angle between 0 and 180 degrees
                servos[i].duty_u16(int(servo_value * 65535 / 180)) #set the servo position based on the mapped value
            old_value[i] = flex_value
            setservos(servo_value, i)
            print(servo_value,i)
if __name__ == "__main__":
    main()
