from pymycobot import ElephantRobot
import time

# 将ip更改成P600树莓派的实时ip

elephant_client = ElephantRobot("192.168.10.173", 5001)

# 启动机器人必要指令
elephant_client.start_client()
time.sleep(1)
elephant_client.set_gripper_mode(0)
time.sleep(1)
# elephant_client.power_off()#夹爪透传换IO模式时需要先关闭机器再重启机器人一次，仅使用夹爪透传模式不必关闭机器人
# elephant_client.state_off()
# time.sleep(3)
# elephant_client.power_on()
# time.sleep(3)
# elephant_client.state_on()
# time.sleep(3)

#透传模式

for i in range(3):
    # 夹爪完全张开
    elephant_client.set_gripper_state(0,100)
    time.sleep(1)
    # 夹爪完全闭合
    elephant_client.set_gripper_state(1,100)
    time.sleep(1)
    elephant_client.set_gripper_state(50,100)
    time.sleep(1)