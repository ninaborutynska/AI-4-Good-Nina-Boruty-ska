# Running my analyzer on real public text

**The text:** 50 open petitions from the UK Parliament petitions website ([petition.parliament.uk](https://petition.parliament.uk)), downloaded on 29 September 2026 from its public open data (`petitions.json`, published under the Open Government Licence). Each line in [`uk_petitions.txt`](uk_petitions.txt) is one petition: the title and the short explanation written by the citizen who started it.

**How I ran it:** `python feedback_analyzer.py uk_petitions.txt` -> report in [`uk_petitions_report.txt`](uk_petitions_report.txt)

**What it reveals:**

- The top keywords were **government (27x), should (17x), uk (15x), public (14x), national (12x)**. This tells me that almost every petition asks the government to do something. That is true, but I knew it already.
- The numbers were the most useful part. They show what people care about: tax allowance (£18,000), maternity pay (90% for 12 weeks), pay for teaching assistants (£20,000), the state pension.
- Searching for a word works well: 4 of 50 petitions mention the NHS and 2 mention children.

**What it misses:**

- **Only 1 of 50 petitions was marked urgent**, even though many are about serious things like blood cancer transplants, benefits for people with diabetes, and maternity pay. My urgent words (unsafe, broken, alert, danger) were made for complaints about a street, not for petitions. One petition even starts with *"Introduce urgent moratorium..."*, and it was not flagged, because "urgent" is not on my list.
- **The mood score doesn't work here**: only 1 positive and 4 negative words were found. Petitions are written formally, so my simple word lists almost never match.
- **Word counts lose the meaning.** "Should" is the 2nd most common word, but it says nothing about the topic. And 50 different topics each get only a few words, so no single topic stands out.
- **Who is not in this data at all:** only people who know about the website, can write in formal English and have time to start a petition. Their problems end up here; the problems of people who don't write petitions don't.

**What I learned:** a tool built for one kind of text (short complaints about a neighbourhood) does not automatically work for another kind (petitions). The word lists are my own choices, and they decide what the tool can "see".
