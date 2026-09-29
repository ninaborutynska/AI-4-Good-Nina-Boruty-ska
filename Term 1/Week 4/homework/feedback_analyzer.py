# Community Feedback Analyzer - Week 4 big individual assignment (AI for Good)
# Reads a file of citizen feedback, cleans + splits + counts the text,
# and writes a report to feedback_report.txt (and prints it).
# Run it with: python feedback_analyzer.py
# Or on another file: python feedback_analyzer.py other_file.txt
import re
import sys

INPUT_FILE = "community_feedback.txt"
REPORT_FILE = "feedback_report.txt"

STOPWORDS = ["the", "a", "an", "and", "or", "but", "is", "are", "was", "be", "it", "its",
             "to", "of", "in", "on", "at", "for", "with", "from", "by", "after", "up",
             "i", "we", "my", "me", "you", "your", "our", "there", "that", "this",
             "no", "not", "very", "too", "much", "more", "only", "every", "all", "at",
             "please", "thank", "who", "do", "can", "cannot", "get", "near", "way", "still",
             "least", "now", "helped", "lot", "people"]
URGENT_WORDS = ["unsafe", "broken", "alert", "danger", "dangerous"]
POSITIVE_WORDS = ["great", "lovely", "nice", "thank", "love", "friendly", "helped", "nicer", "free"]
NEGATIVE_WORDS = ["broken", "unsafe", "dark", "danger", "bad", "noise", "slow", "full", "short", "fast"]


def read_responses(filename):
    """Read the file line by line; skip empty lines; return a list of responses."""
    responses = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            responses.append(line)
    return responses


def has_letter_or_digit(word):
    """True if the word has at least one letter or number (so '&' or '-' are not counted as words)."""
    for character in word:
        if character.isalnum():
            return True
    return False


def clean_words(response):
    """Lowercase a response, split it into words and strip punctuation from every word."""
    words = []
    for word in response.lower().split():
        word = word.strip(".,!?:;\"'()")
        if has_letter_or_digit(word):
            words.append(word)
    return words


def count_words(responses):
    """Bag of words: how often each meaningful word appears (stopwords and numbers skipped)."""
    counts = {}
    for response in responses:
        for word in clean_words(response):
            if word in STOPWORDS or word.isdigit():
                continue
            counts[word] = counts.get(word, 0) + 1
    return counts


def top_keywords(counts, how_many):
    """Find the most frequent words, one at a time, with the comparison-variable pattern."""
    remaining = dict(counts)          # a copy, so the original counts stay complete
    top = []
    for i in range(how_many):
        best_word = ""
        best_count = 0
        for word, count in remaining.items():
            if count > best_count:
                best_word = word
                best_count = count
        if best_word == "":
            break                     # fewer words than how_many
        top.append((best_word, best_count))
        del remaining[best_word]
    return top


def find_urgent(responses):
    """Return every response that contains one of the urgent words."""
    urgent = []
    for response in responses:
        words = clean_words(response)
        for urgent_word in URGENT_WORDS:
            if urgent_word in words:
                urgent.append(response)
                break                 # one urgent word is enough
    return urgent


def sentiment(responses):
    """Bonus: count positive and negative words and return (positive, negative, mood)."""
    positive = 0
    negative = 0
    for response in responses:
        for word in clean_words(response):
            if word in POSITIVE_WORDS:
                positive = positive + 1
            elif word in NEGATIVE_WORDS:
                negative = negative + 1
    if positive > negative:
        mood = "mostly positive"
    elif negative > positive:
        mood = "mostly negative"
    else:
        mood = "mixed"
    return positive, negative, mood


def find_numbers(responses):
    """Bonus: pull out every number people mentioned, with the response it came from."""
    found = []
    for response in responses:
        numbers = re.findall(r"\d+(?:[.,]\d+)*", response)   # 18,000 stays one number
        if len(numbers) > 0:
            found.append(", ".join(numbers) + "  <- " + response)
    return found


def build_report(responses, filename):
    """Put the whole report together as a list of lines."""
    total_words = 0
    for response in responses:
        total_words = total_words + len(clean_words(response))
    average = round(total_words / len(responses), 1)

    counts = count_words(responses)
    urgent = find_urgent(responses)
    positive, negative, mood = sentiment(responses)
    numbers = find_numbers(responses)

    report = []
    report.append("=== Community Feedback Report ===")
    report.append("File analysed: " + filename)
    report.append("Responses analysed: " + str(len(responses)))
    report.append("Average words per response: " + str(average))
    report.append("")
    report.append("Top 5 keywords:")
    number = 1
    for word, count in top_keywords(counts, 5):
        report.append("  " + str(number) + ". " + word + " (" + str(count) + "x)")
        number = number + 1
    report.append("")
    report.append("Urgent responses: " + str(len(urgent)))
    for response in urgent:
        report.append("  ! " + response)
    report.append("")
    report.append("Mood: " + mood + " (" + str(positive) + " positive words, " + str(negative) + " negative words)")
    report.append("")
    report.append("Numbers mentioned:")
    if len(numbers) == 0:
        report.append("  none")
    for line in numbers:
        report.append("  " + line)
    return report


def write_report(report, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for line in report:
            f.write(line + "\n")


def search(responses):
    """Bonus: let the user search for a word until they press Enter."""
    while True:
        word = input("Search for a word (Enter to stop): ").strip().lower()
        if word == "":
            break
        matches = 0
        for response in responses:
            if word in clean_words(response):
                matches = matches + 1
        print(str(matches) + " of " + str(len(responses)) + " responses mention '" + word + "'.")


if __name__ == "__main__":
    filename = INPUT_FILE
    report_file = REPORT_FILE
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        report_file = filename.replace(".txt", "") + "_report.txt"

    responses = read_responses(filename)
    report = build_report(responses, filename)
    write_report(report, report_file)
    for line in report:
        print(line)
    print("")
    print("Report saved to " + report_file)
    print("")
    search(responses)
