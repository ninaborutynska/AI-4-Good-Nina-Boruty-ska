# Term 1 - Week 3: Lists & Dictionaries

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

**What did I hand in?**
_List the files, or link to them. Notebook exports, screenshots, scripts._

**What did I find difficult, and how did I solve it?**

### Checklist
- [ ] My workshop / homework files are in `homework/`
- [ ] Everything runs without errors, or I explained what does not and why

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

**Where does this connect to "AI for Good"?**
_One concrete link to ethics, sustainability or social impact._
