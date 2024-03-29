# -*- coding: utf-8 -*-
from enum import Enum, auto
from Core.Robo import Robo
from Sensor.search_ball import FindBall  # 공이 있으면 true, 없으면 false
from Sensor.ball_y_center import BallyCenterMeasurer  # 공이 가운데, 위, 아래 중 어디에 있는지 (C, U, D)
from Sensor.ball_x_center import BallxCenterMeasurer  # 공이 가운데, 왼쪽, 오른쪽 중 어디에 있는지 (C, L, R)
from Sensor.tan_dist_measure import DistMeasurer  # 로봇에서부터 공과의 거리
from Sensor.t_put_judge import Tputting_y_BallCenterMeasurer  # 공이 Y축 기준으로 가운데 있을 때 true, 아니면 false
from Sensor.t_put_x_judge import Tputting_x_BallCenterMeasurer  # 공이 X축 기준으로 가운데 있을 때 true, 아니면 false
from Sensor.flag_x_center import FlagxCenterMeasurer  # 깃발이 가운데, 왼쪽, 오른쪽 중 어디에 있는지 (C, L, R)
from Sensor.flag_y_center import FlagyCenterMeasurer  # 깃발이 가운데, 위, 아래 중 어디에 있는지 (C, U, D)
from Sensor.HitPoint import HitPointer  # 타격지점 구하는 코드
from Sensor.GoalDetection import GoalDetect # 홀인 했는지 확인하는 코드
import time
import copy


class Act(Enum):
    START = auto()  # 시작 - 아무런 동작도 안 함
    SEARCH_FIRST = auto()  # T샷 시작
    SEARCH_FLAG = auto()  # 깃발 찾기
    SEARCH_BALL = auto()  # 공 찾기
    SEARCH_PUTTING_LOCATION = auto()  # 치는 위치 찾기
    CHECK = auto()  # 홀인 확인
    EXIT = auto()  # 종료
    TEST = auto() # 테스트때 사용


# 상황 판단 하는 파트
class Controller:
    robo: Robo = Robo()
    # act: Act = Act.START  # 순서도 시작
    act: Act = Act.START
    # act: Act = Act.START가 시작 지점

    count_putting: int = 0  # 퍼팅 횟수
    check_holein: int = 0  # 홀인 판단 횟수
    area: str = ""  # 현재 맵
    ball: bool  # 공 T/F

    # T샷할 때 사용하는 위치 파악하는 변수 위치가 파악되면 그 위치의 변수가 1이 된다.
    L_right: int = 0  # 로봇: L / 공: right
    L_center: int = 0  # 로봇: L / 공: center
    L_left: int = 0  # 로봇: L / 공: left
    C_right: int = 0  # 로봇: C / 공: right
    C_center: int = 0  # 로봇: C / 공: center
    C_left: int = 0  # 로봇: C / 공: left

    canPutting: float = 11.0  # 칠 수 있는 거리있는지 판단 변수 (길이)

    ###################################################################################################
    # 티샷에서 공이 어디에 있는지 확인하는 코드
    @classmethod
    def check_ball_first(self):
        L_right = self.L_right  # 로봇: L / 공: right
        L_center = self.L_center  # 로봇: L / 공: center
        L_left = self.L_left  # 로봇: L / 공: left
        C_right = self.C_right  # 로봇: C / 공: right
        C_center = self.C_center  # 로봇: C / 공: center
        C_left = self.C_left  # 로봇: C / 공: left

        #  .process():  공에 유무를 반환함 T/F
        dir_list = [46, 50, 73, 85]  # 임의로 지정한 로봇 머리의 각도 값 (실제 경기장에서 다시 설정해야 할 수도..)
        dir = 3  # dir_list에서 90을 고를 수 있도록 설정하는 값
        cnt = 0  # 로봇이 어디에서 찾았는지 구분하는 변수

        time.sleep(1)  # 함수를 실행할 때 오류가 안 나도록 하는 time.sleep

        # 로봇이 왼쪽에 있다고 가정
        Tput_y_center = Tputting_y_BallCenterMeasurer().process()
        for i in range(3):  # 티샷이 3개이므로 3번 반복
            self.robo._motion.set_head("DOWN", dir_list[dir])  # 고개 내리면서 확인
            dir -= 1
            time.sleep(0.1)
            Tput_y_center = Tputting_y_BallCenterMeasurer().process()
            print("Ball find and center T/F: ", Tput_y_center)  # 공 센터의 T/F값 출력

            if Tput_y_center == False:  # 공이 발견되지 않았을 때
                cnt += 1

            elif Tput_y_center == True:  # 공이 발견됐을 때
                print("공을 찾았습니다.")
                if cnt == 0:
                    self.L_right = 1
                    print("LEFT: 공을 오른쪽에서 찾았습니다.")
                elif cnt == 1:
                    self.L_center = 1
                    print("LEFT: 공을 가운데에서 찾았습니다.")
                elif cnt == 2:
                    self.L_left = 1
                    print("LEFT: 공을 왼쪽에서 찾았습니다.")
                break

            else:
                print("왼쪽 위치에 있지 않거나, 문제가 있을 수 있습니다.")
                print("로봇이 가운데 위치한다고 생각하고 시작하겠습니다.")

        # 로봇이 가운데 있다고 가정
        dir = 0
        self.robo._motion.set_head("DOWN", dir_list[dir])

        if Tput_y_center == False:
            print("로봇이 가운데에 있다고 생각하겠습니다.")
            # Tput_center_y_Big = Tputting_y_BallCenterMeasurer().process()
            # print("Ball find and y center T/F: ", Tput_center_y_Big)
            Tput_x_center = Tputting_x_BallCenterMeasurer().process()
            print("Ball find and x center T/F: ", Tput_x_center)

            if Tput_x_center == True:
                if cnt == 3:
                    print("Center: 공을 가운데에서 찾았습니다.")
                    self.C_center = 1
                    return
                    
            elif Tput_x_center == False:
                print("가운데 가운데 X")
                self.robo._motion.set_head("LEFT", 45)
                time.sleep(0.1)
                Tput_x_center = Tputting_x_BallCenterMeasurer().process()
                time.sleep(0.1)
                cnt += 1
                print("Tput_x_center: ", Tput_x_center)

                if Tput_x_center == True:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                    if cnt == 4:
                        print("Center: 공을 왼쪽에서 찾았습니다.")
                        self.C_left = 1
                        return

                print("가운데 왼쪽 X")
                self.robo._motion.set_head("RIGHT", 69)
                time.sleep(0.1)
                Tput_x_center = Tputting_x_BallCenterMeasurer().process()
                time.sleep(0.1)
                cnt += 1
                print("Tput_x_center: ", Tput_x_center)
                
                if Tput_x_center == True:
                    if cnt == 5:
                        print("Center: 공을 오른쪽에서 찾았습니다.")
                        self.C_right = 1
                        return

            else:
                print("티샷 부분에서 공을 어디서도 찾지 못했습니다.")
                        
    ###################################################################################################
    # 깃발이 있는지 찾는 코드
    @classmethod
    def check_flag(self):
        down_y = [80, 90, 100, 110] # 깃발 찾기 위한 Y축
        right_left = [30, 45, 54, 60, 90] # 일단 모션에 있는 값 넣었는데, 확인하고 바꿔야 함..
        
        flag = FlagxCenterMeasurer(img_width=640, img_height=480)
        find_flag = flag.run()
        
        print("find_flag: ", find_flag)
        
        y_dir = 0
        while find_flag[3] != True:   # 깃발을 못 찾았을 때 (find_flag[3]: have_flag)
            print("깃발 찾는 함수(check_flag) 실행")
            print("find_flag[3] (have_flag): ", find_flag[3])
            
            find_flag = flag.run()
            x_dir = 0
            self.robo._motion.set_head("DOWN", down_y[y_dir])
            y_dir += 1
            time.sleep(0.2)
            
            if y_dir == len(down_y):
                break
        
            global tmp_angle
            # 고개 오른쪽으로 찾기
            for i in range(len(right_left)):
                find_flag = FlagxCenterMeasurer(img_width=640, img_height=480).run
                time.sleep(0.1)
                print("깃발이 안 보여 오른쪽부터 찾겠습니다.")
                self.robo._motion.set_head("RIGHT", right_left[x_dir])
                print("Debug: ", right_left[x_dir])
                print("=============================")
                x_dir += 1
                time.sleep(0.2)
                if (find_flag == True) or (x_dir == len(right_left)):
                    # print("find_flag == True: ", find_flag == True)  # 테스트용
                    # print("x_dir == len(right_left): ", x_dir == len(right_left))  # 테스트용
                    tmp_angle = right_left[x_dir-2]
                    break
            self.robo._motion.set_head("LEFTRIGHT_CENTER") # 고개 원위치로 (가운데로)
            time.sleep(0.2)
            
            x_dir = 0
            # 고개 왼쪽으로 찾기
            for i in range(len(right_left)):
                find_flag = FlagxCenterMeasurer(img_width=640, img_height=480).run
                time.sleep(0.1)
                print("깃발이 안 보여 왼쪽부터 찾겠습니다.")
                self.robo._motion.set_head("LEFT", right_left[x_dir])
                print("Debug: ", right_left[x_dir])
                print("=============================")
                x_dir += 1
                time.sleep(0.2)
                if (find_flag == True) or (x_dir == len(right_left)):
                    # print("find_flag == True: ", find_flag == True)  # 테스트용
                    # print("x_dir == len(right_left): ", x_dir == len(right_left))  # 테스트용
                    tmp_angle = -right_left[x_dir-2]
                    print("self.robo._motion.x_head_angle: ", tmp_angle)
                    break
            self.robo._motion.set_head("LEFTRIGHT_CENTER") # 고개 원위치로 (가운데로)
            time.sleep(0.2)
            
            if tmp_angle < 0:  # 로봇 머리 각도가 왼쪽에
                best_angle = self.find_best(abs(tmp_angle))  # 들어온 값이 마이너스이므로 플러스로 바꾸기
                self.robo._motion.set_head("LEFT", best_angle)
                self.robo._motion.x_head_angle = tmp_angle  # 저장된 각도를 돌린 각도로 바꾸기
                print("!!!로봇 머리 각도 왼쪽!!!!!!: ", self.robo._motion.x_head_angle)
                break
            elif tmp_angle > 0:   # 로봇 머리 각도가 오른쪽에
                best_angle = self.find_best(tmp_angle)
                self.robo._motion.set_head("RIGHT", best_angle)
                self.robo._motion.x_head_angle = tmp_angle
                break
            else:
                print("로봇 머리 각도는 정면입니다.")
                print("!!!로봇 머리 각도 가운데!!!!!!: ", self.robo._motion.x_head_angle)
                break

            # 여기까지 오면 깃발을 찾은 상황 -> 깃발 센터 맞추는 함수로 넘어가기
            self.check_flag_distance()
                
    ###################################################################################################
    # 깃발 1도씩 조정하면서 각도 확인
    @classmethod
    def check_flag_distance(self):
        flagxcenter = FlagxCenterMeasurer(img_width=640, img_height=480)
        flagycenter = FlagyCenterMeasurer(img_width=640, img_height=480)

        correctAngle = 0  # 깃발이 센터에 왔을 때 1로 변경

        # 깃발을 못 찾았을 때 반환하는 값

        while correctAngle != 1:
            flag_x_angle = flagxcenter.run()
            time.sleep(0.2)
            print("flag_x_angle: ", end="")
            print(flag_x_angle[0])
            print(flag_x_angle[0] == "C")

            if flag_x_angle[0] == "C":
                print("통과했어요")
                flag_y_angle = flagycenter.run()
                print(flag_y_angle[0])
                time.sleep(0.2)

                if flag_y_angle[0] == "C":
                    print("flag_x_angle: ", flag_x_angle[0])
                    print("flag_y_angle: ", flag_y_angle[0])
                    print("중앙에 있습니다.")
                    correctAngle = 1
                    break

                elif flag_y_angle[0] == "D" or flag_y_angle[0] == "U":
                    recent_will_angle = 3
                    while flag_y_angle[0] != "C":
                        before_flag_y_angle = copy.copy(flag_y_angle[0])
                        flag_y_angle = flagycenter.run()  # 여기서 U/C/D 판단
                        time.sleep(0.2)
                        print("flag_y: ", flag_y_angle[0])  # 판단 내용 출력

                        if before_flag_y_angle != flag_y_angle[0]:
                            recent_will_angle = 1

                        if flag_y_angle[0] == "U":  # 판단 내용 판단
                            self.robo._motion.set_head_small("UP", recent_will_angle)
                            time.sleep(0.1)

                        if flag_y_angle[0] == "D":  # 판단 내용 판단
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                            time.sleep(0.1)

                    correctAngle = 1
                    print("중앙에 왔습니다.")
                    break

                else:
                    print("check_flag_distance 함수에서 원하는 Y angle이 안 들어왔습니다.")

            elif flag_x_angle[0] == "L" or flag_x_angle[0] == "R":
                print("flag_x_angle: R or L이 들어왔습니다.")
                print(flag_x_angle[0])
                recent_will_angle = 3
                while flag_x_angle[0] != "C":
                    print("while문이 실행되었습니다.")
                    before_flag_x_angle = copy.copy(flag_x_angle[0])
                    flag_x_angle = flagxcenter.run()  # 여기서 U/C/D 판단
                    time.sleep(0.2)
                    print("flag_x: ", flag_x_angle[0])  # 판단 내용 출력

                    if before_flag_x_angle != flag_x_angle[0]:
                        recent_will_angle = 1

                    if flag_x_angle[0] == "L":
                        self.robo._motion.set_head_small("LEFT", recent_will_angle)
                        time.sleep(0.1)
                    if flag_x_angle[0] == "R":
                        self.robo._motion.set_head_small("RIGHT", recent_will_angle)
                        time.sleep(0.1)
            else:
                print("flag_ball_distance 함수에서 원하는 X angle이 안 들어왔습니다.")
                        
    ###################################################################################################
    # 공 찾는 코드 + 공 1도씩 조정하면서 각도 확인하는 함수
    @classmethod
    def check_ball_distance(self):
        correctAngle = 0  # 공이 센터에 왔을 때 1로 변경

        ballxcenter = BallxCenterMeasurer(img_width=640, img_height=480)
        ballycenter = BallyCenterMeasurer(img_width=640, img_height=480)
        
        # 공을 못 찾았을 때 반환하는 값
        ball_x_angle = ["N", "N", "N"]
        ball_y_angle = ["N"]
        
        # 공과 로봇의 거리(dist)와 공이랑 깃발 사이의 각도(flag_ball_angle_fin), 방향(direction)을 구하는 부분
        flag_angle = self.robo._motion.x_head_angle  # 깃발 각도 저장
        down_y = [20, 50, 80] # 공 찾기 위한 Y축
        right_left = [30, 45, 54, 60, 90] # 일단 모션에 있는 값 넣었는데, 확인하고 바꿔야 함..
        find_ball = FindBall().process()
        
        
        print("ball_x_angle[0]: ", ball_x_angle[0] == "N") # Debug
        print("find_ball (T/F): ", find_ball) # 공 찾는거 T/F
        
        if ball_x_angle[0] == "N":
            y_dir = 0
            while find_ball != True:
                print("find_ball", find_ball)
                x_dir = 0
                self.robo._motion.set_head("DOWN", down_y[y_dir])
                y_dir += 1
                time.sleep(0.2)
                if y_dir == len(down_y):
                    break
        
                # 고개 오른쪽으로 찾기
                for i in range(len(right_left)):
                    find_ball = FindBall().process()
                    time.sleep(0.1)
                    print("공이 안 보여 오른쪽부터 찾겠습니다.")
                    self.robo._motion.set_head("RIGHT", right_left[x_dir])
                    print("Debug: ", right_left[x_dir])
                    print("=============================")
                    x_dir += 1
                    time.sleep(0.2)
                    if (find_ball == True) or (x_dir == len(right_left)):
                        # print("find_ball == True: ", find_ball == True)  # 테스트용
                        # print("x_dir == len(right_left): ", x_dir == len(right_left))  # 테스트용
                        break
                self.robo._motion.set_head("LEFTRIGHT_CENTER") # 고개 원위치로 (가운데로)
                time.sleep(0.2)
                
                x_dir = 0
                # 고개 왼쪽으로 찾기
                for i in range(len(right_left)):
                    find_ball = FindBall().process()
                    time.sleep(0.1)
                    print("공이 안 보여 왼쪽부터 찾겠습니다.")
                    self.robo._motion.set_head("LEFT", right_left[x_dir])
                    print("Debug: ", right_left[x_dir])
                    print("=============================")
                    x_dir += 1
                    time.sleep(0.2)
                    if (find_ball == True) or (x_dir == len(right_left)):
                        # print("find_ball == True: ", find_ball == True)  # 테스트용
                        # print("x_dir == len(right_left): ", x_dir == len(right_left))  # 테스트용
                        break
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.2)
            # 여기까지 오면 공을 찾은 상황
 
        # 공 센터 맞추는 부분
        while correctAngle != 1:
            ball_x_angle = ballxcenter.process()
            time.sleep(0.2)
            print("ball_x_angle: ", end="")
            print(ball_x_angle[0])

            # x축 기준으로 센터라면, y축 기준으로 센터를 맞추기
            if ball_x_angle[0] == "C":
                ball_y_angle = ballycenter.process()
                time.sleep(0.2)
                if ball_y_angle[0] == "C":
                    print("ball_x_angle: ", ball_x_angle[0])
                    print("ball_y_angle: ", ball_y_angle[0])
                    print("중앙에 왔습니다.")
                    correctAngle = 1
                    break

                elif ball_y_angle[0] == "D" or ball_y_angle[0] == "U":
                    # 아래로 1도씩 움직이기
                    recent_will_angle = 3
                    while ball_y_angle[0] != "C":
                        before_ball_y_angle = copy.copy(ball_y_angle[0])
                        ball_y_angle = ballycenter.process()
                        time.sleep(0.2)
                        print("ball_y: ", ball_y_angle[0])

                        if before_ball_y_angle != ball_y_angle[0]:
                            recent_will_angle = 1

                        if ball_y_angle[0] == "U":
                            self.robo._motion.set_head_small("UP", recent_will_angle)
                            time.sleep(0.1)

                        if ball_y_angle[0] == "D":
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                            time.sleep(0.1)

                    correctAngle = 1
                    print("중앙에 왔습니다.")
                
                    # 공 센터 맞추면 해당 각도 저장
                    ball_angle = self.robo._motion.x_head_angle
                    print("공을 센터에 맞추고, 각도를 저장하였습니다.")
                    print("=============================")
                
                    # 공 센터 맞추면 로봇과 공의 거리 구하는 코드 실행
                    dist_Process = DistMeasurer()
                    self.dist = dist_Process.display_distance(ball_angle)  # dist: 공과 로봇의 거리 ?? self.dist에 대한 정의가 없는데 어떻게 씀?
                    time.sleep(0.1)
                
                    # flag_ball_angle_fin: 공이랑 깃발 사이의 각도
                    self.flag_ball_angle_fin = abs(ball_angle - flag_angle)
                    print("공이랑 깃발 각도를 저장하였습니다.")
                    print("=============================")
                                
                    # direction: 방향
                    if (ball_angle - flag_angle) > 0:
                        direction = "R"
                    elif (ball_angle - flag_angle) < 0:
                        direction = "L"
                    else:
                        direction = ""  # 여기 나오면 안 되긴 함..
                    print("방향을 저장하였습니다.")
                    print("=============================")
                    
                    break

                else:
                    print("check_ball_distance 함수에서 원하는 Y angle이 안 들어옴.")

            # x축 기준으로 공의 센터가 안 맞는다면 실행
            elif ball_x_angle[0] == "L" or ball_x_angle[0] == "R":
                recent_will_angle = 3
                while ball_x_angle[0] != "C":
                    before_ball_x_angle = copy.copy(ball_x_angle[0])
                    ball_x_angle = ballxcenter.process()
                    time.sleep(0.2)
                    print("ball_x: ", ball_x_angle[0])

                    if before_ball_x_angle != ball_x_angle[0]:
                        recent_will_angle = 1

                    if ball_x_angle[0] == "L":
                        self.robo._motion.set_head_small("LEFT", recent_will_angle)
                        time.sleep(0.1)
                    if ball_x_angle[0] == "R":
                        self.robo._motion.set_head_small("RIGHT", recent_will_angle)
                        time.sleep(0.1)

            else:
                print("check_ball_distance 함수에서 원하는 X angle이 안 들어옴.")
                
    ###################################################################################################
    # 공이 가운데, 오른쪽, 왼쪽 중 어디에 있는지 확인해서 로봇을 옆으로(왼쪽, 오른쪽) 움직이는 모션 (walk_side)
    @classmethod
    def ball_feature_ball(self):
        print("Debug in ball_feature_ball")
        ball_is_x_center = ["N", "N", "N"]  # fix
        # [공의 가운데 여부, 공의 x 중심좌표, 공의 y 중심좌표]

        # ball_ball_feature_measure 에서 return 값: L / C / R
        while ball_is_x_center[0] != "C":
            ball_is_x_center = BallxCenterMeasurer().process()
            print("카메라 기준(공): ", ball_is_x_center[0])  # 카메라 기준(공): L or C or R

            if ball_is_x_center[0] == "L":
                print("공이 왼쪽에 있습니다.")
                self.robo._motion.walk_side("LEFT")
                time.sleep(0.5)

            elif ball_is_x_center[0] == "C":
                print("공이 가운데 있습니다.")
                break

            elif ball_is_x_center[0] == "R":
                print("공이 오른쪽에 있습니다.")
                self.robo._motion.walk_side("RIGHT")
                time.sleep(0.5)
            else:
                print("원하는 값이 반환되지 않았습니다.")
                
###################################################################################################
    # 로봇 몸체랑 깃발이랑 일직선 만들기
    @classmethod
    def putting_robot_turn(self):
        # 여기까지 오면 깃발 찾고, 센터까지 맞춘 상황
        if self.robo._motion.x_head_angle != 0:
            if self.robo._motion.x_head_angle < 0:  # 로봇 머리 각도가 왼쪽에 있음
                print("Turn Right")
                angle = self.find_best(abs(self.robo._motion.x_head_angle))
                print("TEST find_best_angle: ", angle)
                self.robo._motion.turn("LEFT", angle)
                time.sleep(0.1)
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.1)
            elif self.robo._motion.x_head_angle > 0:  # 로봇 머리 각도가 오른쪽에 있음
                print("Turn Left")
                angle = self.find_best(abs(self.robo._motion.x_head_angle))
                print("TEST find_best_angle: ", angle)
                self.robo._motion.turn("RIGHT", angle)
                time.sleep(0.1)
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.1)
            else:
                print("None 값이 나와서 오류남")
                return
        else:  # 로봇 몸체와 깃발이 일직선
            print("Turn Center")
            return

    ###################################################################################################
    # 로봇과 깃발을 일직선으로 만들 때, 들어온 앵글값에서 가장 가까운(최적의) 값을 찾아 턴 하는 함수
    @classmethod
    def find_best(self, target_angle):
        # target_angle: 로봇과 깃발을 일직선으로 맞추기 위해 틀어야 하는 각도
        actions = [60, 45, 20, 10, 5, 3]  # 가능한 동작 리스트
        remaining_angle = target_angle
        
        while remaining_angle > 0 and actions:
            best_action = min(actions, key=lambda x: abs(target_angle - x))
            if best_action <= remaining_angle:
                remaining_angle -= best_action
            actions.remove(best_action)
            
            if best_action is not None:
                return best_action
            else:
                return "best_action: N"
            
    ###################################################################################################
    # 걸어갈 때, 틀어질 경우를 대비해서 다시 위치 잡는 함수
    @classmethod
    def correct_position(self):
        # 공을 못 찾았을 때 반환하는 값
        ball_x_angle = ["N", "N", "N"]

        xTput_x_center = BallxCenterMeasurer(img_width=640, img_height=480)
        ball_x_angle = xTput_x_center.process()

        # 걸어가면서 틀어진 각도 맞추는 로직
        while ball_x_angle[0] != "C":
            print("걸어가면서 틀어진 각도 맞추기")

        while ball_x_angle[0] != "C":
            if ball_x_angle[0] == "L" or ball_x_angle[0] == "R":
                if ball_x_angle[0] == "L":
                    self.robo._motion.set_head_small("LEFT", 1)
                    time.sleep(0.1)

                if ball_x_angle[0] == "R":
                    self.robo._motion.set_head_small("RIGHT", 1)
                    time.sleep(0.1)

        # 현재 머리 각도가 플러스면 오른쪽으로 턴해야 함
        while self.robo._motion.x_head_angle > 0:
            self.robo._motion.x_head_angle = head_plus(60)
            self.robo._motion.x_head_angle = head_plus(45)
            self.robo._motion.x_head_angle = head_plus(20)
            self.robo._motion.x_head_angle = head_plus(10)
            self.robo._motion.x_head_angle = head_plus(5)
            self.robo._motion.x_head_angle = head_plus(3)
            self.robo._motion.x_head_angle = 0

        # 현재 머리 각도가 마이너스면 왼쪽으로 턴해야 함
        while self.robo._motion.x_head_angle < 0:
            self.robo._motion.x_head_angle = head_minus(60)
            self.robo._motion.x_head_angle = head_minus(45)
            self.robo._motion.x_head_angle = head_minus(20)
            self.robo._motion.x_head_angle = head_minus(10)
            self.robo._motion.x_head_angle = head_minus(5)
            self.robo._motion.x_head_angle = head_minus(3)
            self.robo._motion.x_head_angle = 0

        # 오른쪽으로 턴
        def head_plus(self, N):
            x_head_angle_n = self.robo._motion.x_head_angle // N
            if x_head_angle_n >= 1:
                for _ in range(x_head_angle_n):
                    self.robo._motion.turn("RIGHT", N)
                    self.robo._motion.x_head_angle -= N
            elif x_head_angle_n == 0:
                return self.robo._motion.x_head_angle
            else:
                print("여기로 오면 안 되는뎁..")
            return self.robo._motion.x_head_angle

        # 왼쪽으로 턴
        def head_minus(self, N):
            x_head_angle_n = self.robo._motion.x_head_angle // -N
            if x_head_angle_n >= 1:
                for _ in range(x_head_angle_n):
                    self.robo._motion.turn("LEFT", N)
                    self.robo._motion.x_head_angle += N
            elif x_head_angle_n == 0:
                return self.robo._motion.x_head_angle
            else:
                print("여기로 오면 안 되는뎁..")
            return self.robo._motion.x_head_angle
        
    ###################################################################################################
    # 퍼팅 후 타격지점 찾을 때, 들어온 앵글값에서 가장 가까운(최적의) 값을 찾아 턴 하는 함수
    @classmethod
    def find_best_actions(self,target_angle, way):
        # target_angle: 로봇이 퍼팅 위치 가기전 틀어야하는 각도
        # way: 공이 왼쪽에 있는지 오른쪽에 있는지 판단하는 값
        actions = [60, 45, 20, 10, 5, 3]  # 가능한 동작 리스트
        remaining_angle = target_angle
        robot_way = way

        best_actions = []

        while remaining_angle > 0 and actions:
            best_action = min(actions, key=lambda x: abs(target_angle - x))
            if best_action <= remaining_angle:
                best_actions.append(best_action)
                remaining_angle -= best_action

                if robot_way == "R":
                    self.robo._motion.turn("RIGHT", best_action)

                elif robot_way == "L":
                    self.robo._motion.turn("LEFT", best_action)

                else:
                    print("shot_way의 값이 이상함.")
                time.sleep(0.8)
            actions.remove(best_action)
                
    ###################################################################################################
    # 퍼팅 후 공 위치 찾기
    @classmethod
    def check_ball_location(self):
        print("Debug check_ball_location in Controller")
        time.sleep(0.1)

        # 구간을 나눠서 찾는다고 생각
        short_left_location = 0  # 짧은 거리 왼쪽
        short_right_location = 0  # 짧은 거리 오른쪽
        short_forward_location = 0  # 짧은 거리 정면
        long_forward_location = 0  # 긴 거리 정면
        long_left_location = 0  # 긴 거리 왼쪽
        long_right_location = 0  # 긴 거리 오른쪽

        exist_ball = FindBall().process()  # 공 찾은 값 True/False
        print("공을 찾았습니다 (T/F): ", exist_ball)

        if exist_ball == True:
            print("공이 화면에 보입니다.")
            print("공이 안 쳐진듯..")

        elif exist_ball == False:
            print("공을 찾지 못했습니다.")
            short_forward_location = 1
            if short_forward_location == 1:
                self.robo._motion.turn("LEFT", 45)
                time.sleep(0.8)
                self.robo._motion.turn("LEFT", 45)
                time.sleep(0.8)
                self.robo._motion.set_head("DOWN", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 short_forward_location에서 찾았습니다.")

                else:
                    short_left_location = 1

            if short_left_location == 1:
                print("짧은 왼쪽에 있다고 생각")

                self.robo._motion.set_head("LEFT", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 short_left_location에서 찾았습니다.")

                else:
                    short_right_location = 1

            if short_right_location == 1:
                print("짧은 오른쪽에 있다고 생각")

                self.robo._motion.set_head("RIGHT", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 short_right_location에서 찾았습니다.")

                else:
                    long_right_location = 1

            if long_right_location == 1:
                print("긴 오른쪽에 있다고 생각")

                self.robo._motion.set_head("DOWN", 80)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 long_right_location에서 찾았습니다.")

                else:
                    long_forward_location = 1

            if long_forward_location == 1:
                print("긴 가운데에 있다고 생각")

                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 long_forward_location에서 찾았습니다.")

                else:
                    long_left_location = 1

            if long_left_location == 1:
                print("긴 왼쪽에 있다고 생각")

                self.robo._motion.set_head("LEFT", 45)
                time.sleep(0.1)

                exist_ball = FindBall().process()
                print(exist_ball)

                if exist_ball == True:
                    print("공을 long_left_location에서 찾았습니다.")

                else:
                    print("어라 어딨지..?")

        else:
            print("원하는 값이 반환되지 않았습니다.")
            
#######################################################################################################################################
    @classmethod
    def go_robo(self):
        act = self.act
        robo: Robo = Robo()
        L_right = self.L_right
        L_center = self.L_center
        L_left = self.L_left
        C_right = self.C_right
        C_center = self.C_center
        C_left = self.C_left

        canPutting = self.canPutting

        ########################################################## # test
        if act == act.TEST:
            
            self.robo._motion.set_head("LEFTRIGHT_CENTER")
            time.sleep(0.5)
            self.robo._motion.walk_side("LEFT", 10)

            # 이 밑 부분은 확인을 통해서 바꿔야 함.
            self.robo._motion.turn("RIGHT", 20, 2)
            time.sleep(0.8)
            self.robo._motion.walk_side("LEFT", 3)
            time.sleep(0.5)
            self.robo._motion.turn("RIGHT", 20)
            time.sleep(0.8)
            self.robo._motion.walk_side("RIGHT")

            self.ball_feature_ball()
            time.sleep(1)
        
            exit()
        
#############################################################################
        # 모든 것의 시작점
        if act == act.START:
            print("ACT: ", act)  # Debug
            self.act = act.SEARCH_FIRST
            
#############################################################################
        elif act == act.SEARCH_FIRST:
            print("ACT: ", act)  # Debug
            time.sleep(0.5)
            
            # 티샷에서 공과 로봇의 위치를 찾는 함수(공과 로봇의 위치를 찾아서 L_right를 포함한 6개에 변수 중 하나를 1로 변경)
            self.check_ball_first()
            time.sleep(0.1)
        
            if self.L_right == 1:  # 퍼팅 판단 return 받은걸로 모션
                print("로봇: 왼쪽, 공: 오른쪽")
                self.robo._motion.walk("FORWARD", 10, 1.0)
                time.sleep(0.1)

                # 화면에 보이는 공을 화면상의 중심에 맞추기 위해, 로봇의 몸체를 좌우로 이동
                self.ball_feature_ball()
                time.sleep(0.1)

            
            elif self.L_center == 1:
                print("로봇: 왼쪽, 공: 가운데")
                self.robo._motion.walk("FORWARD", 5, 1.0)
                time.sleep(0.1)

                # 화면에 보이는 공을 화면상의 중심에 맞추기 위해, 로봇의 몸체를 좌우로 이동
                self.ball_feature_ball()
                time.sleep(0.1)

                # dist_Process = DistMeasurer() # 이 부분 왜 있을까요??
                # angle = 0
                # dist = dist_Process.display_distance(angle)
                # time.sleep(0.1)


            elif self.L_left == 1:
                print("로봇: 왼쪽, 공: 왼쪽")
                self.robo._motion.walk("FORWARD", 1)
                time.sleep(0.1)

                # 화면에 보이는 공을 화면상의 중심에 맞추기 위해, 로봇의 몸체를 좌우로 이동
                self.ball_feature_ball()
                time.sleep(0.1)


            elif self.C_center == 1:
                print("로봇: 가운데, 공: 가운데")
                self.robo._motion.walk_side("LEFT", 4) # 공을 발로 차는걸 예방하기 위해서 왼쪽으로 먼저 이동.
                time.sleep(0.5)
                self.robo._motion.turn("RIGHT", 20, 4) # 90도 회전
                time.sleep(0.8)
                self.robo._motion.walk_side("LEFT", 2)
                time.sleep(0.5)
                

                self.ball_feature_ball()
                time.sleep(1)


            elif self.C_right == 1:
                print("로봇: 가운데, 공: 오른쪽")
                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.5)
                self.robo._motion.walk_side("RIGHT", 4)

                # 이 밑 부분은 확인을 통해서 바꿔야 함. (C_left랑 똑같이 하면 될듯..?)
                self.robo._motion.turn("RIGHT", 20, 2)
                time.sleep(0.8)
                self.robo._motion.walk_side("LEFT", 3)
                time.sleep(0.5)
                self.robo._motion.turn("RIGHT", 20) 
                time.sleep(0.8)
                self.robo._motion.turn("RIGHT", 10)
                time.sleep(0.8)

                self.ball_feature_ball()
                time.sleep(1)


            elif self.C_left == 1:
                print("로봇: 가운데, 공: 왼쪽")

                self.robo._motion.set_head("LEFTRIGHT_CENTER")
                time.sleep(0.5)
                self.robo._motion.walk_side("LEFT", 10)

                # 이 밑 부분은 확인을 통해서 바꿔야 함.
                self.robo._motion.turn("RIGHT", 20, 2)
                time.sleep(0.8)
                self.robo._motion.walk_side("LEFT", 3)
                time.sleep(0.5)
                self.robo._motion.turn("RIGHT", 20)
                time.sleep(0.8)
                self.robo._motion.walk_side("RIGHT")

                self.ball_feature_ball()
                time.sleep(1)


            else:
                print("원하는 값이 안 옴")
                time.sleep(1)

            # +======================== 공을 화면의 y축 기준으로 중심에 맞추는 부분(우진이가 추가) ================================+
            ballycenter = BallyCenterMeasurer(img_width=640, img_height=480)
            ball_y_angle = ["N"]  # 공을 못 찾았을 때 반환하는 값
            correctAngle = 0
            putting_angle = 30
            putting_angle_error = 2
            dist_Process = DistMeasurer()

            while correctAngle != 1:
                # 이미 x축 기준으로 센터이므로, y축 기준으로 어디에 있는지 판별
                ball_y_angle = ballycenter.process()
                time.sleep(0.2)
                if ball_y_angle[0] == "C":
                    print("ball_y_angle: ", ball_y_angle[0])
                    print("중앙에 왔습니다.")
                    correctAngle = 1
                    break

                elif ball_y_angle[0] == "D" or ball_y_angle[0] == "U":
                    
                    # 아래로 1도씩 움직이기
                    recent_will_angle = 3
                    while True:
                        self.ball_feature_ball()
                        before_ball_y_angle = copy.copy(ball_y_angle[0])
                        ball_y_angle = ballycenter.process()
                        time.sleep(0.2)
                        print("ball_y: ", ball_y_angle[0])

                        if before_ball_y_angle != ball_y_angle[0]:  # 이전에 고개를 돌렸던 값과 현재 고개를 돌릴 값이 일치하면 3도 말고 1도씩만 돌리게 만듬
                            recent_will_angle = 1

                        if ball_y_angle[0] == "U":
                            self.robo._motion.set_head_small("UP", recent_will_angle)
                            time.sleep(0.1)

                        elif ball_y_angle[0] == "D":
                            self.robo._motion.set_head_small("DOWN", recent_will_angle)
                            time.sleep(0.1)
                        
                        elif ball_y_angle[0] == "C":
                            correctAngle = 1
                            print("중앙에 왔습니다.")
                        
                            # 공 센터 맞추면 해당 각도 저장
                            ball_angle = self.robo._motion.y_head_angle
                            print("공 찾아서 각도 저장함")

                            # dist = dist_Process.display_distance(abs(ball_angle - 11.6))
                            robot_ball_angle = ball_angle - 11.6

                            # print("dist:",dist)
                            print("robot_ball_angle", robot_ball_angle)
                            print("======================")
                            time.sleep(0.1)

                            if robot_ball_angle > (putting_angle - putting_angle_error) and robot_ball_angle < (putting_angle + putting_angle_error):
                                print("퍼팅하겠습니다.")
                                break

                            elif robot_ball_angle < (putting_angle - putting_angle_error):
                                print("뒤로 가겠습니다.")
                                self.robo._motion.walk("BACKWARD", 1)

                            elif robot_ball_angle > (putting_angle + putting_angle_error):
                                print("앞으로 가겠습니다.")
                                self.robo._motion.walk("FORWARD", 1)

                            else:
                                print("T샷 C_left 오류")
            time.sleep(0.1)
            self.robo._motion.hit_the_ball("LEFT")
            # +================================== 여기까지 추가 ================================================+
            time.sleep(0.1)
            self.robo._motion.turn("LEFT", 45, 4, 0.5)   # 티샷 끝나고 깃발 찾기 위해 턴
            print("왼쪽으로 90도 회전")

            self.act = act.SEARCH_FLAG
                
#############################################################################
        elif act == act.SEARCH_FLAG:
            print("Act:", act)  # Debug

            minimum_distball = 20

            self.robo._motion.set_head("DOWN", 90)

            # ACT: SEARCH_BALL
            print("Act: SEARCH_BALL")  # Debug
            time.sleep(0.1)
            
            while True:
                ballxcenter = BallxCenterMeasurer(img_width=640, img_height=480)
                if ballxcenter.process[0] == 'N':
                    self.check_ball_distance()

                time.sleep(0.2)

                # ball_angle = self.robo._motion.x_head_angle
                # angle = abs(self.robo._motion.y_head_angle - 11.6)  # angle 값 수정
                distball = DistMeasurer().display_distance(angle) # 공 거리값

                if distball > minimum_distball:
                    self.robo._motion.walk("FORWARD", 3, 1.0)
                    continue
                else:
                    break
                
            print("ball distance: ", end="")
            print(distball)

            time.sleep(0.2)

            # self.ball_feature_ball()
            
#############################################################################
            print("Act: SEARCH_PUTTING_LOCATION")  # Debug

            # 공의 거리 구할 때 여기를 exit하면 공의 거리를 출력하고 멈춤
            # exit()

            if ball_angle >= flag_angle:   # ball angle이 더 크면 오른쪽
                real_angle = ball_angle - flag_angle  
                shot_way = "R" # 공이 오른쪽에 있으니 오른쪽으로
            else:  # ball angle이 더 작으면 왼쪽
                real_angle = flag_angle - ball_angle  
                shot_way = "L" # 공이 왼쪽에 있으니 왼쪽으로

            print("Real angle: ", end="")  # 값 확인
            print(real_angle)
            print("distflag: ",distflag)
            
            self.check_flag()   # 깃발 찾기
            time.sleep(0.1)
            self.check_flag_distance() # 깃발 센터 맞추기
            time.sleep(0.1)
            self.putting_robot_turn() # 깃발이랑 로봇 몸이 일직선이 되게 만들기

            solver = HitPointer(distflag, distball, real_angle, 7)
            hit_dist, hit_angle, hit_will_anlge, ball_is_flag_back, flag_ball_dis = solver.solve()
            print("가야하는 거리: ", hit_dist)
            print("돌아야하는 각도", hit_angle)
            print("공앞에서 돌아야하는 각도", hit_will_anlge)
            print("공이 깃발 뒤에 있는지 없는지 (T/F): ", ball_is_flag_back)
            print("공과 깃발 사이의 거리(cm): ", flag_ball_dis)

            hit_angle = int(hit_angle)
            self.find_best_actions(hit_angle, shot_way)

            hit_dist = int(hit_dist)
            will_goto_ball = hit_dist // 4
            self.robo._motion.walk("FORWARD", will_goto_ball, 1.0)  # 퍼팅 지점까지 걸어가기

            if ball_is_flag_back == False: # 공이 깃발 뒤에 있을 떄
                if shot_way == "R": # 깃발 뒤에 있으면 치는 방향이 바뀌기 때문에 
                    shot_way = "L" # shot_way를 L로 
                    print("shot way를 R에서 L로 변경합니다.")

                else:
                    shot_way = "R"
                    print("shot_way를 L에서 R로 변경합니다.")

                self.find_best_actions(hit_will_anlge, shot_way) # hit_will_angle로 몇도 돌아야 하는지, shot_way로 어느 방향으로 돌아야하는지
            else:
                self.find_best_actions(hit_will_anlge, shot_way)

            time.sleep(0.1)
            print("퍼팅 위치까지 왔습니다.")
            print("퍼팅해주세요")    

            if flag_ball_dis <= 60:
                self.robo._motion.hit_the_ball("LEFT",short=True) # 짧게 치기
            else:
                self.robo._motion.hit_the_ball("LEFT") # 길게 치기
            time.sleep(6)
            
            
            # 홀컵과 공의 거리의 차를 구해서 홀인 체크 파트로 넘어가는 부분
            if abs(flag_ball_dis) <= 30:
                self.act = act.CHECK
            else:
                self.act = act.SEARCH_BALL
                
#############################################################################
        elif act == act.CHECK:  # 홀인했는지 확인
            print("Act:", act)  # Debug

            self.robo._motion.turn("LEFT", 45)
            time.sleep(0.1)
            self.robo._motion.turn("LEFT", 45)
            time.sleep(0.1)

            self.robo._motion.set_head("LEFTRIGHT_CENTER")
            time.sleep(0.2)
            self.robo._motion.set_head("DOWN", 45)
            time.sleep(0.1)

            self.check_flag_distance() # 깃발 거리 angle 구하기
            time.sleep(0.2)

            goal_detector = GoalDetect(img_width=640, img_height=480)
            is_goal = goal_detector.process() # 골이 들어갔는지 판단
            print("홀인 유무 (T/F): ", is_goal)

            if is_goal == True:
                self.act = act.EXIT
            else:
                self.act = act.SEARCH_BALL
                
#############################################################################
        elif act == act.EXIT:
            print("Act:", act)  # Debug

            self.robo._motion.ceremony("goal")   # 세레머니
            time.sleep(1)
            
            exit()
            
#############################################################################
        else:
            print("!!!!!!!!여기로 빠지면 큰일!!!!!!!!")

        return False