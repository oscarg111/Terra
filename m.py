import cv2
from pyzbar.pyzbar import decode


# Function to decode barcodes from frames
def scan_barcodes(frame):
    barcodes = decode(frame)
    for barcode in barcodes:
        # Extract the barcode data and draw a rectangle around it
        barcode_data = barcode.data.decode('utf-8')
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the barcode data
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_data, (x, y - 10), font, 0.9, (0, 255, 0), 1)

    return frame


# Open a video capture object (0 is the default camera)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # Call the function to scan barcodes in the frame
    frame = scan_barcodes(frame)

    # Display the frame
    cv2.imshow('Barcode Scanner', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
