# Term 1 - Week 4: Strings, Text & Files

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

The Week 4 workshop notebook "Strings, Text & Files". Wave 1 was about string methods: `strip()`, `lower()`, `replace()`, `split()` and the `in` operator (clean one piece of citizen feedback). Wave 2 was about turning text into numbers with a "bag of words": counting words with the counting pattern and skipping stopwords (which words come up most?). Wave 3 was about reading and writing files with `with open(...)` (read feedback from a file, flag the urgent lines, write a report). The big individual assignment was the **Community Feedback Analyzer**, a tool that reads a file of citizen feedback, cleans and counts the words, and writes a report. The homework was to finish the analyzer and run it on a piece of real public text: what does it reveal, and what does it miss?

**What did I hand in?**

- [`Week4_Workshop_Student.ipynb`](homework/Week4_Workshop_Student.ipynb) - the full workshop notebook with Exercises 1-3 run, the Community Feedback Analyzer and both reflections ("whose feedback is in the file?" and "who decides what is urgent?"). The second cell gives fictional answers to `input()`, so the whole notebook runs from top to bottom.
- [`feedback_analyzer.py`](homework/feedback_analyzer.py) - the analyzer as a separate script: `python feedback_analyzer.py` (or `python feedback_analyzer.py other_file.txt` for another file). It reports the number of responses, the average number of words, the top 5 keywords, the urgent responses, and as a bonus a mood score, the numbers people mentioned and a word search.
- [`community_feedback.txt`](homework/community_feedback.txt) and [`feedback_report.txt`](homework/feedback_report.txt) - 19 fictional citizen responses and the report the analyzer wrote about them.
- [`real_text_analysis.md`](homework/real_text_analysis.md) - the homework: my analyzer on 50 real UK Parliament petitions ([`uk_petitions.txt`](homework/uk_petitions.txt), report in [`uk_petitions_report.txt`](homework/uk_petitions_report.txt)), and what it reveals and misses.

Example: on the fictional feedback the analyzer finds 19 responses, 12.4 words on average, top keywords bike, street, great, broken, lights, and 5 urgent responses. On the real petitions it only marks 1 of 50 as urgent, which shows that my word lists only work for the kind of text I made them for.

**What did I find difficult, and how did I solve it?**

The parts I needed the most explanation for were: why `"Bike!"` and `"bike"` are different words until you clean them, how a loop inside a loop goes over every word of every response, and why the `with` block is safer than just `open()`. Finding the top 5 keywords without `sorted()` was also tricky; I did it by finding the biggest one, removing it and repeating. I asked Claude to explain these step by step and tested the analyzer on different files to see what happens.

**Use of AI tools:** I used Claude (an AI assistant) a lot for this week's homework. It helped me with most of the code and the written answers. At the same time I used it as a tutor: whenever I did not understand something, I asked it to explain it step by step, and I learned a lot that way. I went through all the code and ran it myself to understand what each part does.

### Checklist
- [x] My workshop / homework files are in `homework/`
- [x] Everything runs without errors, or I explained what does not and why

---

## 2. Hackathon prototype -> [`hackathon/`](hackathon/)

> Your tool and your SDG for this hackathon are announced at the **start of Friday's class**.
> Write them down here once you know them.

**Project title:**

**My pair partner:**

**Tool we had to use:**

**SDG we had to address:**

**What problem does it solve, and for whom?**
_Name a real, specific user. "Everyone" is not a user._

**What did you build?**
_Two or three sentences. What can a user actually do with it?_

**Link to the live thing (if any):**
_Deployed URL, workflow export, video demo - whatever proves it works._

**How do I run it?**
_Short instructions so someone else can start it._

**Who did what?**
_Be honest about the split of work between you and your partner._

**Ethical reflection - what are the risks of your tool? Who could it harm?**
_Every hackathon requires this. One honest paragraph beats three vague ones._

### Checklist
- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [ ] The prototype actually runs, and I wrote down how to run it
- [ ] Ethical reflection written above

---

## 3. Presentation -> [`presentation/`](presentation/)

*Only fill this in for the week your group was selected to present. You need at least **one** of these across the whole term.*

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

---

## 4. Reflection

**What is the most important thing I learned this week?**

I learned that a computer can't really read text, it can only count words. Before counting, you have to clean the text, otherwise "Bike!" and "bike" are two different words.

**Where does this connect to "AI for Good"?**

My analyzer only hears the people who wrote something down, and it only sees the words I told it to look for. That made me think about how easy it is for AI to miss people who were never in the data.
