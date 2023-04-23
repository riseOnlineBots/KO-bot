import cv2
from easyocr import Reader


def cleanup_text(text):
    # Strips out non-ASCII text, so we can draw the text on the image
    # using OpenCV.
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def process(image, debug=False):
    texts = []
    reader = Reader(['en'], gpu=True, verbose=False)

    results = reader.readtext(image)

    if debug:
        cv2.imshow('Display', image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyAllWindows()

    for (bbox, text, prob) in results:
        # Displays the OCR'd text and associated probability.
        text = cleanup_text(text)
        texts.append(text)

        if debug:
            print("[INFO] {:.4f}: {}".format(prob, text))

            # Unpacks the bounding box.
            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]), int(tl[1]))
            tr = (int(tr[0]), int(tr[1]))
            br = (int(br[0]), int(br[1]))
            bl = (int(bl[0]), int(bl[1]))
            # Cleanups the text and draw the box surrounding the text along
            # with the OCR'd text itself.
            processed_image = image
            cv2.rectangle(processed_image, tl, br, (0, 255, 0), 2)
            cv2.putText(processed_image, text, (tl[0], tl[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # cv2.imshow('Output', processed_image)

    return texts
