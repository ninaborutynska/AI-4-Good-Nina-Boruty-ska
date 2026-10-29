# BinWatch: which bin should the crew clear first?

**SDG 15: Life on Land** | AI for Good, Hackathon 7 | Cameron Ruiter and Nina Borutyńska
**Try it here:** [binwatch.streamlit.app](https://binwatch.streamlit.app)

**What it does.** You upload photos of the underground rubbish containers in The Hague. Our Roboflow model (trained on photos we took ourselves) looks for 4 things around the bin: closed bags (`bag`), bags that gulls tore open (`torn_bag`), loose rubbish (`loose_litter`) and other stuff people dumped, like cardboard or planks (`dumped_item`). Then the app tells you which bins need to be cleared first.

**The problem.** In The Hague people often leave their rubbish bags next to the container instead of in it. Gulls rip the bags open and the rubbish ends up all over the street, in parks and in the canals. The city even gives out free extra strong bags because gulls peck through normal ones [1]. In 2025 illegal dumping of bulky waste went up to 11.2 million kg, and there were more bags left next to bins too [2]. The containers have sensors, but they only measure what's inside the bin, not what's next to it.

**Who it is for.** The team at the municipality that plans where the waste crews go. Residents see the bags next to the bins and can send in a photo. On a busy day there are a lot of these reports and the crews can't go everywhere at once. BinWatch checks all the photos and puts them in order, so the crew goes to the worst bins first.
**Not for:** enforcement officers (handhavers) who want to give fines, or anyone who wants to keep an eye on a street or the people living there. The model only sees rubbish, not who put it there.

**Why SDG 15.** When gulls tear the bags open, plastic and food waste blows into green areas. Animals eat it or get stuck in it, and the gulls get used to living off our rubbish. If the worst bins get cleared first, the rubbish has less time to spread. It's also linked to SDG 14, because rubbish in the canals can end up in the sea.

**How it works.**
1. You upload one or more photos, or take one with your phone in the app (Streamlit).
2. Every photo goes to our Roboflow model. It draws a box around everything it finds and gives it one of the 4 labels. Without this step the app can't do anything. A slider hides boxes the model isn't sure about (0.40 by default).
3. The app turns the labels into a priority: 🔴 **Clear first** (a torn bag or loose litter, so the rubbish is already spreading), 🟡 **Clear on next round** (closed bags or dumped items next to the bin), ⚪ **Clean** (nothing found).
4. You see each photo with the boxes, how many of each thing it found, and the priority. With more photos you also get a **Clear-up order**, worst bin at the top.

Why not something simpler? The sensors can't see next to the bin, and driving a fixed route means also stopping at bins that are already clean.

**Results.** On the Roboflow test set: mAP@50 89.6%, precision 88.5%, recall 86.4%. The hardest class is `loose_litter`: it found 6 of 9, because small scattered pieces are hard to see. The test images come from the same videos as the training images, so on a new street the score will be lower.

**Run it yourself.**
```sh
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # Windows: copy .streamlit\secrets.toml.example .streamlit\secrets.toml
streamlit run app.py                                          # then put your own Roboflow API key in secrets.toml
```

**Ethical reflection.** Our data card, the limits of the model, what can go wrong and who takes the photos are in [`ETHICAL_REFLECTION.md`](ETHICAL_REFLECTION.md).

**Who did what.** Cameron and Nina filmed the videos. Cameron checked the labels, trained the model and built and put the app online. Nina wrote the README, the ethical reflection and the slides. We both used Claude (Anthropic): Cameron for the labelling, the app code and the data card, Nina for the texts and slides.

**Sources.** [1] Gemeente Den Haag, [Meeuwenoverlast beperken](https://www.denhaag.nl/nl/natuur-en-milieu/meeuwenoverlast-beperken). [2] Waste Action Plan progress report 2025, via [The Hague Online](https://thehagueonline.com/the-hague-sees-sharp-rise-in-illegal-bulky-waste-and-intensifies-waste-management-in-2026/) (24-04-2026).
