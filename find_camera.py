
import cv2

for index in range(10):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if cap.isOpened():
        ok, frame = cap.read()

        if ok:
            print(f"Camera index {index}: WORKING")
            print("Resolution:", frame.shape[1], "x", frame.shape[0])

            cv2.imshow(f"Camera index {index}", frame)
            cv2.waitKey(1500)
            cv2.destroyAllWindows()
        else:
            print(f"Camera index {index}: opened, but no frame")

    cap.release()

cv2.destroyAllWindows()
