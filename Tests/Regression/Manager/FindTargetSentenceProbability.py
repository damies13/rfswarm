import cv2
import difflib
import pytesseract


def preprocess_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    return thresh

def normalize_spaces(text):
    normalized_text = ''
    in_space = False
    for char in text:
        if char.isspace():
            if not in_space:
                normalized_text += ' '
                in_space = True
        else:
            normalized_text += char
            in_space = False

    return normalized_text.strip()

def find_best_subsequence(recognized_text, target_sentence):
    recognized_text = normalize_spaces(recognized_text)
    if len(recognized_text) < len(target_sentence):
        return find_best_subsequence(target_sentence, recognized_text)
    target_length = len(target_sentence)
    best_similarity = 0
    best_subsequence = ""

    for i in range(len(recognized_text) - target_length + 1):
        subsequence = recognized_text[i:i + target_length]
        similarity = difflib.SequenceMatcher(None, target_sentence, subsequence).ratio() #Levenshtein Distance
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_subsequence = subsequence

    if len(best_subsequence) == 0:
        best_similarity = 0

    return best_subsequence, best_similarity

def find_target_sentence_similarity(image_path, target_sentence):
    preprocessed_image = preprocess_image(image_path)
    recognized_text = pytesseract.image_to_string(preprocessed_image)

    best_subsequence, best_similarity = find_best_subsequence(recognized_text.lower(), target_sentence.lower())

    return best_subsequence, best_similarity

# if __name__ == "__main__":
#     image_path = ''
#     target_sentence = "Index 1 has no Robots"
#     best_subsequence, best_similarity = find_target_sentence_similarity(image_path, target_sentence)

#     print(f"Best Matching Subsequence: '{best_subsequence}'")
#     print(f"Similarity to Target Sentence: {best_similarity:.2f}")
