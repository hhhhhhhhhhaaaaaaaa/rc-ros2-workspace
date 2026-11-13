import rclpy
from rclpy.node import Node
from rc_msgs.msg import YoloOutputArray, YoloOutput
from ultralytics import YOLO
import cv2





class PiblisherNode(Node):
    def __init__(self, name):
        super().__init__(name) 
        self.cap=cv2.VideoCapture(0)
        self.model= YOLO('/home/jjh/models/best.pt')   
        self.pub=self.create_publisher(YoloOutputArray, "position_data", 10)
        self.timer = self.create_timer(0.1,self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        display=frame.copy()
        results = self.model(frame,verbose=False,conf=0.6,classes=[1])
        result = results[0]
        if len(result.boxes) > 0:
            box = result.boxes[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            roi = frame[y1:y2, x1:x2]
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            red1 = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
            red2 = cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
            green = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
            blue = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
            yellow = cv2.inRange(hsv, (20, 50, 50), (30, 255, 255))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = red1 | red2 | green | blue | yellow
            mask2 = green
            mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel)
            contours2, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            yolo_cx, yolo_cy = map(int, box.xywh[0][:2])
            yolo_conf = float(box.conf[0])
            msg1 = YoloOutputArray()
            msg0 = YoloOutput()
            msg0.center_x = float(yolo_cx)
            msg0.center_y = float(yolo_cy)
            msg0.confidence = yolo_conf
            msg1.header.stamp = self.get_clock().now().to_msg()
            msg1.header.frame_id = "camera"
            msg1.yolo_array.append(msg0)
            self.pub.publish(msg1)
            self.get_logger().info(f'Detected: x={yolo_cx}, y={yolo_cy}, conf={yolo_conf:.2f}')
        else:
            self.get_logger().info('No target detected')
            empty_msg = YoloOutputArray()
            empty_msg.header.stamp = self.get_clock().now().to_msg()
            empty_msg.header.frame_id = "camera"
            self.pub.publish(empty_msg)
        annotated = result.plot()
        if len(result.boxes) > 0:
            box = result.boxes[0]
            yolo_cx, yolo_cy = map(int, box.xywh[0][:2])
            cv2.circle(annotated, (yolo_cx, yolo_cy), 5, (255,0,0), -1)
            cv2.putText(annotated, f'YOLO:{yolo_cx},{yolo_cy}', (yolo_cx+10, yolo_cy-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
            if contours2:
                valid_contours = [c for c in contours2 if len(c) >= 3]
                if valid_contours:
                    shifted_contours = [c + [x1, y1] for c in valid_contours]
                    cv2.drawContours(display, shifted_contours, -1, (0,0,255), 2)
        cv2.imshow('mask', display)
        cv2.imshow('yolo', annotated)
        cv2.waitKey(1)
        
def main(args=None):
    rclpy.init(args=args)
    node = PiblisherNode('yolo_publisher')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()