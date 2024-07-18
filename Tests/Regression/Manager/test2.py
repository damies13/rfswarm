import easyocr
import cv2
import numpy as np

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu = True)

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def perform_ocr(image_path, target_sentence):
    preprocessed_image = preprocess_image(image_path)
    results = reader.readtext(preprocessed_image)
    print(results)
    target_words = target_sentence.split()
    probabilities = []
    last_word_index = 0
    for target_word in target_words:
        word_found = False
        i = 0
        for (bbox, text, prob) in results:
            i += 1
            print(text)
            if target_word.lower() in text.lower() and i >= last_word_index:
                last_word_index = i
                probabilities.append(prob)
                word_found = True
                break
        if not word_found:
            probabilities.append(0)  # If word not found, add a probability of 0

    # Calculate the mean probability
    print(probabilities)
    len_sum = [len(word) for word in target_words]
    mean_probabilities = 0
    for i in range(0, len(probabilities)):
        mean_probability = (probabilities[i] * len_sum[i])
        print("Wage:",len(target_words[i]), "Probability:", mean_probability)
        mean_probabilities += mean_probability
    mean_probabilities = mean_probabilities / sum(len_sum)
    
    return probabilities, mean_probabilities

image_path = 'X:/Programy/Robot_framework/rfswarm/rfswarm_fork/active_window_screenshot.png'
target_sentence = "Index 1 has no Robots Index 1 Ramp Up is < 10 sec Index 1 Run is < 10 sec Index 1 has no Script Index 1 has no Test"

word_probabilities, mean_probability = perform_ocr(image_path, target_sentence)

print("Word Probabilities:", word_probabilities)
print("Mean Probability:", mean_probability)
