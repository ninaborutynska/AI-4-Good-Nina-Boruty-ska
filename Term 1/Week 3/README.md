# Term 1 - Week 3: Lists & Dictionaries

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

The Week 3 workshop notebook "Lists & Dictionaries". Wave 1 was about lists: indexes (starting at 0, `-1` for the last item), `append()`, `insert()`, `remove()`, `sort()` and the `in` operator (Food Bank Inventory). Wave 2 was about analysing list data with `sum()`, `len()`, `min()` and `max()` (Wage Gap Analyzer: a 12.0% pay gap in the sample). Wave 3 was about dictionaries: `[]` vs `.get()`, looping with `.items()` and the district that is missing from the data (City Services Map, with a reflection on Ypenburg). The big individual assignment was the **Food Bank Manager**, a menu-driven program for food bank volunteers. The homework was: get an API key and finish Exercise 4 (my first API call), run `ask.py` in Cursor, polish the Food Bank Manager, and find a public dataset about my city and check who is missing from it.

**What did I hand in?**

- [`Week3_Workshop_Student.ipynb`](homework/Week3_Workshop_Student.ipynb) - the full workshop notebook with Exercises 1-3 run, the Food Bank Manager with the bonus (families served and shortage list), the reflections (Ypenburg and "what rule is fair?") and Exercise 4 (the Gemini API: `ask()`, a list of questions, a dictionary of answers). The second cell gives fictional answers to `input()`, so the whole notebook runs from top to bottom.
- [`foodbank.py`](homework/foodbank.py) - the Food Bank Manager as a separate script: `python foodbank.py`
- [`ask.py`](homework/ask.py) - my `ask()` function as a script for Cursor's terminal. The key is asked with `getpass` and is never saved in the file.
- [`dataset_detective.md`](homework/dataset_detective.md) - the dataset detective: population per district of The Hague (where I live) and who is missing from it.

Exercise 4 and `ask.py` are written but not run here, because the API key must stay private. I used the Gemini API for real in Hackathon 3 (LabBridge, see [`hackathon/`](hackathon/)).

Example run of the Food Bank Manager with fictional input: after 4 packages -> `LOW STOCK: cooking oil (4 left)`; a donation of `Rice ` (with a capital and a space) is added to `rice`; a wrong quantity (`abc`) and a wrong menu choice (`9`) are refused; report -> `Total items in stock: 80`, `Lowest stock: cooking oil (4)`, `Families served this session: 4`.

**What did I find difficult, and how did I solve it?**

The parts I needed the most explanation for were: why Python starts counting at 0, why `services['Ypenburg']` crashes but `services.get('Ypenburg', 0)` does not, and how the counting pattern `inventory[item] = inventory.get(item, 0) + qty` works both for a new item and for an existing one. In the Food Bank Manager, it took me a while to see why `continue` is needed to skip items that are at 0. I asked Claude to explain these step by step and ran the code with different inputs to see what happens.

**Use of AI tools:** I used Claude (an AI assistant) a lot for this week's homework. It helped me with most of the code and the written answers. At the same time I used it as a tutor: whenever I did not understand something, I asked it to explain it step by step, and I learned a lot that way. I went through all the code and ran it myself to understand what each part does.

### Checklist
- [x] My workshop / homework files are in `homework/`
- [x] Everything runs without errors, or I explained what does not and why

---

## 2. Hackathon prototype -> [`hackathon/`](hackathon/)

**Project title:** LabBridge: Equal Access Health Literacy

**My pair partner:** Sofiia Tiahun

**Tool we had to use:** Gemini API or Claude API, called from Python (we used the Gemini API)

**SDG we had to address:** SDG 10 - Reduced Inequalities

**What problem does it solve, and for whom?**
Lab reports are written for doctors, not patients. About 1 in 4 adults in the Netherlands (24.5%) has trouble understanding health information (Pharos/Nivel), and about 21-28% skip a specialist visit because of the cost or the "own risk" (Nivel/Zorgwijzer). LabBridge is for patients who get a lab report and can't easily understand it - especially people with limited health literacy, older adults and non-native speakers - and who can't quickly or affordably see a doctor to explain it. It is not for doctors and it is not a diagnosis.

**What did you build?**
A web app where the user pastes their lab results (or picks a sample report) and clicks "Translate & Explain". Gemini turns it into a plain-language guide: a short summary, an explanation of each result, questions to ask the doctor and low-cost care options. Dangerous values are checked with fixed rules first and always trigger an emergency warning.

**Link to the live thing (if any):**
Code, README, slides, screenshots and ethical reflection are in [`hackathon/labbridge/`](hackathon/labbridge/). Screenshots of the working app: [input](hackathon/labbridge/screenshots/labbridge_input.png), [output](hackathon/labbridge/screenshots/labbridge_output.png).

**How do I run it?**
In `hackathon/labbridge/`: copy `.env.example` to `.env` and add your own Gemini API key, run `python3 app.py`, then open http://localhost:8080 in the browser. Full instructions are in the [LabBridge README](hackathon/labbridge/README.md).

**Who did what?**
Sofiia mainly built the app. We came up with the concept together. I made the presentation in Canva, wrote the ethical reflection and put everything together on GitHub.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
The biggest risk is that a patient reads the AI explanation as a diagnosis. If it misreads or downplays a dangerous result, someone may delay care they need - and our users, people with limited health literacy, are the least able to spot such an error. The AI may also explain non-English or badly formatted reports worse, which could recreate the inequality SDG 10 asks us to reduce, and lab results are sensitive data. To limit this, every answer is framed as information, not a diagnosis, and tells the user to talk to a doctor; dangerous values are checked with fixed rules before the AI and always show an emergency warning; the input format is kept simple; and reports are not stored. Next, we would test the tool with more languages and report formats and have patients and doctors review its output. Full version: [`individual ethical reflection heckathon 3.docx`](hackathon/labbridge/).

### Checklist
- [x] Prototype code (or export / workflow file) is in `hackathon/`
- [x] This week's slides are in `hackathon/`
- [x] The prototype actually runs, and I wrote down how to run it
- [x] Ethical reflection written above

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

I learned the difference between a list and a dictionary. A list keeps things in order, and a dictionary lets me find something by its name, like a phone contact. Building the Food Bank Manager helped me see how useful this is in a real program.

**Where does this connect to "AI for Good"?**

The Ypenburg exercise showed me that if a group or place is missing from the data, the program acts like it doesn't exist. The same happens with AI: it can only be fair to the people who are in its data.
