# Term 1 - Week 2: Loops & Functions

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

**Project title:** CareFlow: Automating Medication Support

**My pair partner:** Amien el Azzouzi

**Tool we had to use:** n8n

**SDG we had to address:** SDG 3 - Good Health and Well-being

**What problem does it solve, and for whom?**
Many older adults (65+) forget to take their medication, and that can affect their health. CareFlow supports people who need help remembering medication and staying on top of their wellbeing - mainly aimed at people aged 65 and older, but anyone needing support with medication or health could use it.

**What did you build?**
CareFlow is a simple app that reminds users to take their medication two to three times a day and asks them to rate how they're feeling (1-5) at each check-in. An AI classification node reads the response and sorts it as normal, needs attention, or urgent. If there's no response, it sends a follow-up reminder; if there's still no response, or the check-in is urgent, it alerts the user's emergency contact and, with permission, their doctor (huisarts). Everything is saved in a monthly overview sent to the user and their emergency contacts. There's also a help button for direct emergencies.

**Link to the live thing (if any):**
Demo video and the three n8n workflow exports (CareFlow Reminders, CareFlow Monthly Analysis, CareFlow Website) are in [`hackathon/project/`](hackathon/project/), along with the presentation slides.

**How do I run it?**
Visit the CareFlow website and create an account. After registering, complete the questionnaire with personal, medical and emergency contact information. Once done, you start receiving check-ins, medication reminders and other support automatically.

**Who did what?**
Amien mainly built the product (the n8n workflows); we came up with the concept together. I made the full presentation in Canva.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
CareFlow deals with health, so any mistake or delay in a notification could have more serious consequences than a non-health-related automation - for example if the system is down, reminders might not arrive, or the AI could misclassify a message as worrying. CareFlow should be trusted for things like medication reminders, daily check-ins, or spotting patterns in responses, but not for making medical decisions on its own. For the average person it's still useful - sending reminders, tracking how users feel, and involving others when necessary - but it isn't foolproof and should be used as a support system alongside humans, professionals or a local doctor, not as a replacement.

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
