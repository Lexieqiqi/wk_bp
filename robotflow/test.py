from pymycobot import ElephantRobot
import time 

elephant_client = ElephantRobot("192.168.10.173", 5001)

elephant_client.start_client()

# elephant_client.write_angle(0,94.828,1000)

# elephant_client.command_wait_done()
# elephant_client.get_coords()

#  # "夹爪设置透传模式"
# elephant_client.set_gripper_mode(0)
# time.sleep(1)

# # "夹爪完全张开"
# elephant_client.set_gripper_state(0,100)
# time.sleep(2)

# # "夹爪完全闭合"
# elephant_client.set_gripper_state(1,100)
# time.sleep(2)

# # "夹爪张开到指定行程，这里张开到夹爪行程的一半"
# elephant_client.set_gripper_value(50,100)
# time.sleep(2)

# 机器人以当前坐标位置往Z方向正方向整体运动50mm"
elephant_client.jog_relative("X",50,1500,1)

# "等待机器人运动到目标位置再执行后续指令"
elephant_client.command_wait_done() 

# # "机器人以当前J6关节角度增加10度"
# elephant_client.jog_relative("J6",10,1500,0)

# # "等待机器人运动到目标位置再执行后续指令"
# elephant_client.command_wait_done()