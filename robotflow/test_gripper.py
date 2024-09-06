from pymycobot import ElephantRobot
import time

# 将ip更改成P600树莓派的实时ip

elephant_client = ElephantRobot("192.168.10.173", 5001)

# 启动机器人必要指令
elephant_client.start_client()
time.sleep(1)
elephant_client.set_gripper_mode(1)
time.sleep(1)
elephant_client.power_off()#夹爪透传换IO模式时需要先关闭机器再重启机器人一次，仅使用夹爪透传模式不必关闭机器人
elephant_client.power_off()
time.sleep(3)
elephant_client.state_off()
time.sleep(3)
elephant_client.power_on()
time.sleep(3)
elephant_client.state_on()
time.sleep(3)
elephant_client.set_digital_out(16, 0)  # IO恢复低电平
time.sleep(1)
elephant_client.set_digital_out(17, 0)  # IO恢复低电平
time.sleep(1)

# IO模式
#夹爪全开全闭合控制代码，注意在夹爪透传切换IO模式时需要先关闭机器再重启机器人一次，才能切换回夹爪IO模式
for i in range(3):

    elephant_client.set_digital_out(16, 1)  # 闭合夹爪
    time.sleep(1)
    elephant_client.set_digital_out(17, 0)  # IO恢复低电平
    time.sleep(1)
    elephant_client.set_digital_out(16, 0)  #IO恢复低电平
    time.sleep(1)
    elephant_client.set_digital_out(17, 1)  # 打开夹爪
    time.sleep(1)

elephant_client.set_digital_out(16, 0)  # IO恢复低电平
time.sleep(1)
elephant_client.set_digital_out(17, 0)  # IO恢复低电平
time.sleep(1)