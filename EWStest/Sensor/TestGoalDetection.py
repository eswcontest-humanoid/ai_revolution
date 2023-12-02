import numpy as np
import cv2

class GoalDetect:
    def __init__(self, img_width=800, img_height=600, width=4, focal=450):
        self.dist = 0 
        self.focal = focal
        self.pixels = 30
        self.width = width

        self.img_width = img_width
        self.img_height = img_height
        self.img_width_middle = img_width // 2
        self.img_height_middle = img_height // 2

        self.kernel = np.ones((3, 3), 'uint8')
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.org = (0, 20)
        self.fontScale = 0.6
        self.color = (0, 0, 255)
        self.thickness = 2
        
        self.middle = img_width // 2
        
        # #Define object specific variables  
        # dist = 0
        # focal = 450
        # pixels = 30
        # width = 4

        # img_width = 640
        # img_height = 480
        # middle = img_width // 2

    #find the distance from then camera
    def get_dist(self, rectange_params, image, name, isMiddle):
        #find no of pixels covered
        pixels = rectange_params[1][0]

        #calculate distance
        dist = (self.img_width * self.focal)/pixels
        
        #Write n the image
        if name == 'flag':
            image = cv2.putText(image, 'flag Distance from Camera in CM :', self.org, self.font,  
            1, self.color, 2, cv2.LINE_AA)

            image = cv2.putText(image, 'flag Middle : {}'.format(isMiddle), self.org, self.font,  
            1, self.color, 2, cv2.LINE_AA)
        else:
            image = cv2.putText(image, 'ball Distance from Camera in CM :', self.org, self.font,  
            1, self.color, 2, cv2.LINE_AA)

            image = cv2.putText(image, 'flag Middle : {}'.format(isMiddle), (0,40), self.font,  
            1, self.color, 2, cv2.LINE_AA)

        image = cv2.putText(image, str(dist), (110,50), self.font,  
        self.fontScale, self.color, 1, cv2.LINE_AA)

        return image

    # box 좌표의 x축 최댓값과 최솟값을 return하는 함수
    def getMaxMin(self, box):
        min_x, max_x = self.img_width, 0

        for x, y in box:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
        return max_x, min_x

    # box 좌표의 y축 최댓값과 최솟값을 return하는 함수
    def getyMaxMin(self, box):
        min_y, max_y = self.img_height, 0

        for x, y in box:
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return max_y, min_y


    # max_x, min_x를 입력받으면 해당 물체가 중간에 있는지 return하는 함수
    def judgeMiddle(self, max_x, min_x):

        l_dist = min_x
        r_dist = self.img_width - max_x
        error_range = 30
        
        if abs(l_dist - r_dist) < error_range:
            return True
        else:
            return False
            
            
    def is_inside(flag_box, ball_box):
        for point in ball_box:
            if cv2.pointPolygonTest(flag_box, (point[0], point[1]), False) < 0:
                return False
        return True

    def process(self):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        #Extract Frames 
        # cap = cv2.VideoCapture("long.h264")

        #basic constants for opencv Functs
        kernel = np.ones((3,3),'uint8')
        font = cv2.FONT_HERSHEY_SIMPLEX 
        org = (0,20)  
        fontScale = 0.6 
        color = (0, 0, 255) 
        thickness = 2


        cv2.namedWindow('Object Dist Measure ', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Object Dist Measure ', 700,600)

        #loop to capture video frames
        while True:
            ret, img = cap.read()
            
            if not ret:
                break
            
            hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

            # window version
            # ball hsv
            low_green = np.array([35, 82, 0])
            high_green = np.array([152, 255, 141])
            green_mask = cv2.inRange(hsv_img, low_green, high_green)

            lower1 = np.array([0, 0, 43])
            upper1 = np.array([19, 183, 200])
            lower = np.array([167, 135, 8])
            upper = np.array([187, 255, 255])
            mask = cv2.inRange(hsv_img, lower, upper)
            mask += cv2.inRange(hsv_img, lower1, upper1)

            lower_flag = np.array([21, 58, 126])
            upper_flag = np.array([34, 255, 255])
            mask_flag = cv2.inRange(hsv_img, lower_flag, upper_flag)


            #Remove Extra garbage from image

            yellow_in_green = cv2.bitwise_and(yellow_mask, yellow_mask, mask=green_mask)

# 노란색 영역의 윤곽선 찾기
            #find the histogram -> 공
            cont,hei = cv2.findContours(yellow_in_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cont = sorted(cont, key = cv2.contourArea, reverse = True)[:1]
            
            b_max_x, b_min_x = 0, 0
            b_max_y, b_min_y = 0, 0
                
            if len(cont) > 0:
                ball_cnt = cont[0]
                #check for contour area
                if (cv2.contourArea(ball_cnt)>100 and cv2.contourArea(ball_cnt)<306000):

                    #Draw a rectange on the contour
                    rect = cv2.minAreaRect(ball_cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    print('ball points :', box)
                    cv2.drawContours(img, [box], -1, (255,0,0), 3)

                    b_max_x, b_min_x = self.getMaxMin(box)
                    b_max_y, b_min_y = self.getyMaxMin(box)
                    isMiddle = self.judgeMiddle(b_max_x, b_min_x)
                    
                    img = self.get_dist(rect, img, 'ball', isMiddle)

            # 깃발
            cont2,hei2 = cv2.findContours(mask_flag,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cont2 = sorted(cont2, key = cv2.contourArea, reverse = True)[:1]

            if len(cont2) > 0:
                flag_cnt = cont2[0]
                #check for contour area
                if (cv2.contourArea(flag_cnt)>100 and cv2.contourArea(flag_cnt)<306000):

                    #Draw a rectange on the contour
                    rect = cv2.minAreaRect(flag_cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    print('flag points :', box)
                    cv2.drawContours(img, [box], -1, (0,255,0), 3)

                    f_max_x, f_min_x = self.getMaxMin(box)
                    f_max_y, f_min_y = self.getyMaxMin(box)
                    isMiddle = self.judgeMiddle(f_max_x, f_min_x)
                    
                    img = self.get_dist(rect,img, 'flag', isMiddle)
                    
                    print(b_max_x, " ", b_min_x)
                    if f_min_x <= b_min_x and b_max_x <= f_max_x and f_min_y <= b_min_y and b_max_y <= f_max_y:
                        print("Goal!")
                

            cv2.imshow('Object Dist Measure ', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    goal_detect = GoalDetect()
    goal_detect.process()