## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

The Week 1 workshop notebook "Python Basics & Flow Control". It had three learning waves: using Python as a calculator (`+ - * / // % **`), variables and data types (string, integer, float, Boolean, converting with `int()` / `str()`, `input()`), and making decisions with comparisons and `if` / `elif` / `else`. The big individual assignment was **Green or Not?**, a CO2 budget calculator that asks about flights, driving and diet, calculates the yearly CO2 and says if you are under or over the sustainable budget of 2500 kg. The notebook ended with setting up this GitHub portfolio.

**What did I hand in?**

- [`Week1_Workshop_Student.ipynb`](homework/Week1_Workshop_Student.ipynb) - the full workshop notebook with all code cells run and all written questions answered (including the reflections on the income risk classifier and on using the CO2 calculator for a climate tax).
- [`green_or_not.py`](homework/green_or_not.py) - the Green or Not? assignment as a separate Python script, so it can be run on its own: `python green_or_not.py`

Example run of Green or Not?: 2 flights, 3000 km driving, eats meat daily -> `You emit 2890 kg CO2 per year. That is slightly over budget.`

**What did I find difficult, and how did I solve it?**

The most confusing part for me was that `input()` always gives back a string. At first I did not understand why multiplying the answer by 7 did not give a number. After converting it with `int()` or `float()` it worked. I also had to get used to the difference between `=` and `==`, and to the fact that indentation in Python really matters for which lines belong to an `if`. Running small cells and reading the error messages helped me find the mistakes.

**Use of AI tools:** I used Claude (AI assistant) to check my answers, explain parts I did not understand, and help me fix small things in the code (for example making "Yes" and "yes" both work in Green or Not?). I read and ran all the code myself and can explain every line.

### Checklist
- [x] My workshop / homework files are in `homework/`
- [x] Everything runs without errors, or I explained what does not and why

---

ReadMe for Hackathon 1 
Project title: Reloop 
 
My pair partner: Jalie Vermeegen 
 
Tool we had to use: Lovable or Bolt.new (We used Bolt.new) 
 
SDG we had to address: 
Reloop supports SDG 4 – Quality Education, especially the goal of making education more accessible and equitable. Because Reloop is free to use and requires no account, payment, or subscription, it provides an additional learning resource without creating a financial barrier. This makes mathematics practice accessible to a wider group of users regardless of their background. 
 
What problem does it solve, and for whom? 
Mathematics is considered a difficult subject by many secondary-school students, and students may struggle to judge whether they truly understand a topic or what their current mathematical level is. Many existing practice tools are either require an account/subscription, or do not give students a quick way to test themselves at a level that matches their ability. A simple, level-based quiz was chosen over a full course or tutoring platform because it lets students test themselves instantly without committing to a longer learning path. This is especially relevant after COVID-19: according to the OECD PISA 2022 results, the average mathematics score of 15-year-olds across OECD countries fell by almost 15 points between 2018 and 2022 [1]. 

Reloop is therefore primarily intended for secondary-school students who want additional mathematics practice and a simple way to test their skills. Furthermore this tool can be used by anyone else who just want to practice maths, but at the end of the day this is mostly focussed towards secondary-school students. It's not intended for younger children who need step-by-step teaching, or for students who don't read English well. 
 
[1] https://www.oecd.org/en/data/dashboards/pisa-education-and-skills.html 

What did you build? 
Reloop is a free mathematics quiz website made with AI that has three difficulty levels: Beginner, Intermediate and Advanced, users can select a quiz from one of the 3 levels, pick one of the three topics provided per level and go through the quizzes. Once they complete a quiz they receive a score and see which questions they answered incorrectly, allowing them to identify areas that may require more practice.  The website requires no account, payment or subscription and has a simple interface so users can start practising almost immediately. 
 
Link to the live thing (if any): 
[ReL∞p — Math Quiz ](https://reloop-math-fro-mch2.bolt.host/)
 
How do I run it? 
[Use the link: ReL∞p — Math Quiz ](https://reloop-math-fro-mch2.bolt.host/)
 
Who did what? Be honest about the split of work between you and your partner. We both worked on the website itself through Bolt.new and the presentation. Then Jalie did the README and I did the Ethical Reflection. 


Ethical Reflection 

This ethical reflection looks at the product built during the first hackathon of the minor AI for Good. The website is a math quiz for high-school students, with three levels to practice. 

The app assumes a lot about its users. It needs a device and stable internet, so it excludes students without one. Everything is in English, which excludes students who don't read it well. Open answers are checked by matching the expected text, so a correct answer written differently might be marked wrong, and there's no support for screen readers, high contrast, or other accessibility needs. Students also pick their own level, assuming they can judge it accurately, and there's no help if they get stuck, just guessing or waiting for the result. 

The tool could also be misused. Since the results page shows the correct answer for every wrong one, a student could type random answers just to collect the answer key instead of actually practicing, giving a false sense of understanding and possibly turning it into a homework cheat sheet. Showing a level like "Beginner" to a teacher could also make a student feel bad over just one quiz, and once AI is added, a wrong explanation could teach students something incorrect if they trust it blindly. To reduce these risks, we could accept more answer formats, add simpler language or translation, delay showing the correct answer behind an extra step, and make clear this tool is for practice, not grading. 
 
 

---

## 4. Reflection

What is the most important thing I learned this week? 

The biggest thing I've noticed while building the website with AI is that I can never rely on AI in 100% especially if it's something that is supposed to help others. Like in here we have a math quiezzes that should help students learn or remind them about math exercises. And at first when we made the website with the first prompt it didn't really come up as we wanted, it didn't make some stuff that we asked for so we had to double check everything and it took long time. I think AI is a huge helper for these kind of things but human should still keep an eye on it and supervision is necessary. 

Where does this connect to "AI for good" 

For me, AI for good is about using AI in the right purpose. This assignment showed me a good perspective of what to focus on when making a product for others. I know that AI can be extremely helpful in a case like this but the essential part is to be aware of how to apply it to get our desired result.
