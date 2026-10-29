# BinWatch: data card and ethical reflection

## Data card

| | |
|---|---|
| **What** | Photos of underground rubbish containers in The Hague and the area around them |
| **How** | 7 videos we filmed ourselves with our phones in October 2026, in daylight only: 5 on 27 October, plus 2 extra for torn bags and closed bags. We took 3–4 frames per second and removed blurry and near-duplicate frames. |
| **Labels** | `bag`, `torn_bag`, `loose_litter`, `dumped_item`, boxes in Roboflow, labelled with help from Claude and checked by Cameron. Photos of clean bins are kept with no boxes, so the model also learns "nothing to do". |
| **Size** | 300 images. Split: 211 train / 60 valid / 29 test. |
| **Privacy** | 21 frames with a readable number plate were removed. |

**Limits:** only a few streets in one city, only daylight (we have no night photos, so we don't know how it works in the dark), only autumn (gulls are worst in spring and summer), and WhatsApp made the videos less sharp. The biggest one: our test images come from the same videos as our training images, so the real-world score will be lower than Roboflow shows (mAP@50 89.6%). `torn_bag` got 9 out of 9 in the test, but that's only 9 examples, so we can't be sure it's that good.

## Where it can go wrong

- **It sees damage, not the cause.** A bag torn by a rat looks the same as one torn by a gull, so it can't be used to count gull damage.
- **It misses things.** With small litter (`loose_litter` is the weakest class: it found 6 of 9, and in our own test at 0.40 it missed a lot of small pieces), or when a bag is just outside the photo. Then a dirty bin gets "Clean" and has to wait, which is the worst mistake it can make. A wrong "Clear first" only costs a short trip. So BinWatch should help decide the order of the route, not replace it.

## Who takes the photos

We decided that residents will report a bin with a photo. We left out a camera on the collection truck (filming streets every day is too close to surveillance), the crew itself (if they're already at the bin they can just clear it) and enforcement officers (they give fines, and BinWatch is not for that).

Our choice has risks too:
- **Some neighbourhoods report more than others**, so quiet areas could get less help. → BinWatch only sets the order of reported bins; the normal route stays the same for everyone.
- **Photos can show neighbours, house numbers or number plates.** → Blur them automatically and delete the photo once the bin is cleared.
- **Someone could use it to get a neighbour in trouble.** → The app only shows the bin and the rubbish, never who left it, and results are never used for fines.

## What we did and what's next

**Done:** removed 21 frames with number plates, added clean-bin photos, and the app says it's only a hint for route planning, never proof for fines.
**Next:** test on photos of bins we never filmed, automatic blurring, more torn bags, film in spring and summer, film at night too.
