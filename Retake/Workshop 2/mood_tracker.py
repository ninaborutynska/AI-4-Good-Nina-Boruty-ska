# Mood Tracker - a mental health check-in bot (Week 2 big individual assignment)
# Uses fictional mood scores. This program does not diagnose anything.

GOOD_DAY = 6  # a score of 6 or more counts as a "good day" for the streak


# --- Step 1: ask for a score until it is a number from 1 to 10 ---
def get_valid_score(day):
    while True:
        score = int(input('Day ' + str(day) + ' - how was your mood (1-10)? '))
        if 1 <= score <= 10:
            return score
        print('Please enter a number from 1 to 10.')


# --- Step 2: the average of the week ---
def calculate_average(total, days):
    return total / days


# --- Step 3: a personalised message for every possible average ---
def give_feedback(average):
    if average >= 8:
        return 'A great week! Notice what helped, so you can do more of it.'
    elif average >= 6:
        return 'A good week overall. Keep the habits that work for you.'
    elif average >= 4:
        return 'A steady week. Small things (sleep, a walk, a friend) can nudge it up.'
    else:
        return 'A hard week. Please talk to someone you trust, or contact your GP or a helpline.'


# --- Step 4: the main loop (7 days) ---
total = 0
best_day = 0
best_score = 0
hardest_day = 0
hardest_score = 11

current_streak = 0
longest_streak = 0

for day in range(1, 8):
    score = get_valid_score(day)
    print('Day ' + str(day) + ' : ' + '#' * score + ' (' + str(score) + ')')
    total = total + score

    # when two days have the same score, the first one is kept (> and <, not >= and <=)
    if score > best_score:
        best_score = score
        best_day = day
    if score < hardest_score:
        hardest_score = score
        hardest_day = day

    # bonus: streak of good days in a row
    if score >= GOOD_DAY:
        current_streak = current_streak + 1
        if current_streak > longest_streak:
            longest_streak = current_streak
    else:
        current_streak = 0

# --- Step 5: print the summary ---
average = calculate_average(total, 7)

print()
print('--- Your Week in Review ---')
print('Average mood:  ' + str(round(average, 1)))
print('Best day:      day ' + str(best_day) + ' (' + str(best_score) + '/10)')
print('Hardest day:   day ' + str(hardest_day) + ' (' + str(hardest_score) + '/10)')
print('Longest streak of good days (6+): ' + str(longest_streak))
print(give_feedback(average))
