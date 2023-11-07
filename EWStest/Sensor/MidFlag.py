import numpy as np
import cv2

class ShapeRecognition:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path, cv2.CAP_V4L)
        if not self.cap.isOpened():
            raise ValueError(f"Video at {video_path} cannot be opened")
        self.green_boxes = []
        self.flags = []  # List to store recognized flags
        self.arrows = []  # List to store recognized arrows
        self.farthest_flag_box = None

    def process_frame(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 녹색 범위 정의
        low_green = np.array([57, 78, 61])
        high_green = np.array([89, 255, 255])
        green_mask = cv2.inRange(hsv_frame, low_green, high_green)
        result_frame = cv2.bitwise_and(frame, frame, mask=green_mask)
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.green_boxes = [cv2.boundingRect(contour) for contour in contours]

        # 노랑색 범위 정의
        low_yellow = np.array([0, 16, 144])
        high_yellow = np.array([43, 184, 255])
        yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

        # For each green box, detect yellow shapes within it
        for green_box in self.green_boxes:
            x, y, w, h = green_box
            green_roi = frame[y:y+h, x:x+w]
            yellow_roi_mask = yellow_mask[y:y+h, x:x+w]
            yellow_contours, _ = cv2.findContours(yellow_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            flag_detected = False  # Flag detection flag

            for cnt in yellow_contours:
                approx = cv2.approxPolyDP(cnt, 0.03 * cv2.arcLength(cnt, True), True)
                if len(approx) == 6:
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(green_roi, [box], 0, (0, 255, 0), 2)
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        cv2.putText(frame, 'ARROW', (x+cx, y+cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        self.arrows.append((cx, cy, "ARROW"))
                else:
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(green_roi, [box], 0, (0, 255, 0), 2)
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        cv2.putText(frame, 'FLAG', (x+cx, y+cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        self.flags.append((cx, cy, "FLAG"))
                        flag_detected = True

            # If a flag is detected, mark it and add it to the list
            if flag_detected:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Calculate the distance of the center of the flag box from the bottom center of the camera frame
                camera_center = (frame.shape[1] // 2, frame.shape[0])
                flag_center = (x + cx, y + cy)
                distance = abs(flag_center[1] - camera_center[1])

                # If this flag is farther than the previously detected farthest flag, update it
                if self.farthest_flag_box is None or distance > self.farthest_flag_box[3]:
                    self.farthest_flag_box = (cx, cy, "FLAG", distance)

        # After processing all green boxes, update the rest of the FLAG boxes to ARROW
        for i, box in enumerate(self.flags):
            if box[1] == "FLAG" and box != self.farthest_flag_box:
                self.flags[i] = (box[0], box[1], "ARROW")

        return frame

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab a frame")
                break

            frame = self.process_frame(frame)

            # Display the original frame
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 0  # Use 0 for webcam
    shape_recognition = ShapeRecognition(video_path)
    shape_recognition.run()
