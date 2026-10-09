# Term 1 - Week 6: Language Models

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

This week was about language models. The workshop notebook has three parts: word embeddings (every word is a list of numbers), RNN and LSTM (reading word by word and remembering), and transformers (a word gets its meaning from the words around it). The big assignment was to test a ready-made sentiment model: choose a context, write at least 12 test sentences, label them myself first, run the model, look at the mistakes, do a bias test and write my opinion at the end.

**What did I hand in?**

- [`Week6_Workshop_Student.ipynb`](homework/Week6_Workshop_Student.ipynb) - the workshop notebook with the exercises from sections 1-3 and the big assignment in section 4.

My context was a health clinic that wants to use the model to read feedback from patients. The model gave the same label as me for 6 of 13 sentences. It said that all four Polish sentences were negative, and it was 94 to 100 % sure even when it was wrong. In the bias test, after "The surgeon said that" the word "he" was about six times more likely than "she".

**What did I find difficult, and how did I solve it?**

The topic was hard for me at the start, especially the difference between an RNN and an LSTM. It helped me to think about it like this: an RNN is a reader without notes and an LSTM is a reader with a notebook. It was also hard to explain why the model made a mistake, and not only that it made one.

**Use of AI tools:** I used Claude to run the code, to help me write the texts and to explain the parts I didn't understand. I chose the context, labelled the sentences and made the predictions myself, and I read the whole notebook.

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

**Where does this connect to "AI for Good"?**
_One concrete link to ethics, sustainability or social impact._
