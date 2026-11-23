import os, json, random, re, urllib.parse, urllib.request
from datetime import datetime, timedelta
from datetime import datetime, timezone

TOPICS = [
    ("The Exam Panic","A student discovers the exam is today, not tomorrow."),
    ("The Last Pizza Slice","Two friends invent increasingly silly plans to get the last slice."),
    ("The Invisible Homework","A student claims homework vanished, but the dog is innocent."),
    ("Noob vs Pro","A beginner challenges a boastful gamer and wins by accident."),
    ("The Tiny Superhero","A tiny hero saves the day using an unexpectedly ordinary skill."),
    ("The Alarm Clock War","A sleepy person battles an alarm clock that keeps coming back."),
    ("The Borrowed Charger","Two friends negotiate over one phone charger like world leaders."),
    ("The Haunted Sandwich","A sandwich keeps disappearing whenever the characters look away.")
]

def get_topic():
    key = os.getenv("YT_API_KEY")
    if key:
        # Search recent popular English comedy/animation videos as a lightweight trend signal.
        queries = ["stickman animation comedy", "funny cartoon shorts", "school comedy shorts"]
        candidates = []
        for q in queries:
            url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode({
                "part":"snippet", "type":"video", "order":"viewCount", "publishedAfter":(datetime.utcnow()-timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "maxResults":10, "q":q, "key":key
            })
            try:
                with urllib.request.urlopen(url, timeout=15) as r:
                    data=json.loads(r.read().decode())
                for item in data.get("items", []):
                    title=item["snippet"]["title"]
                    if title and len(title)<100:
                        candidates.append(title)
            except Exception:
                pass
        if candidates:
            title=random.choice(candidates)
            return "Trend-inspired idea: " + title[:75]
    return random.choice(TOPICS)[0]

def make_story(topic, length):
    # Original, deterministic scene structure; trend titles are inspiration only, never copied scripts.
    short = length == "short"
    if "Pizza" in topic or "pizza" in topic.lower():
        beats = [
          ("A","I found the last pizza slice!"),
          ("B","Not so fast. I saw it first."),
          ("A","Let's settle this with rock, paper, scissors."),
          ("B","Fine. One, two, three!"),
          ("A","I choose... pizza."),
          ("B","That's not a move!"),
          ("A","It is when I'm hungry.")
        ]
    elif "Exam" in topic or "exam" in topic.lower():
        beats = [
          ("A","Relax. The exam is tomorrow."),
          ("B","Look at the calendar. It's today!"),
          ("A","Then I have one minute to study."),
          ("B","What subject?"),
          ("A","How to stay calm."),
          ("B","And did you study that?"),
          ("A","No. I'm panicking.")
        ]
    else:
        beats = [
          ("A",f"Today, I will become famous for: {topic.lower()}."),
          ("B","That sounds suspiciously like a bad idea."),
          ("A","Trust me. I have a plan."),
          ("B","Does the plan include thinking?"),
          ("A","I was hoping to skip that part."),
          ("B","What could possibly go wrong?"),
          ("A","Please don't ask questions you know the answer to.")
        ]
    if not short:
        beats = beats + [
          ("B","Wait. We forgot the most important thing."),
          ("A","What?"),
          ("B","A dramatic slow-motion entrance!"),
          ("A","I can't. My budget is zero."),
          ("B","Then walk dramatically for free."),
          ("A","You are a genius."),
          ("B","I know. I charge by the compliment."),
          ("A","What happens if our plan fails?"),
          ("B","We call it a rehearsal."),
          ("A","And if the rehearsal fails?"),
          ("B","We call it modern art."),
          ("A","I think we're making this up as we go."),
          ("B","That's called creativity."),
          ("A","Can creativity buy us lunch?"),
          ("B","Only if we put it on the menu."),
          ("A","Let's try the plan one last time."),
          ("B","Ready. Three, two, one!"),
          ("A","Wait, I forgot what we're doing."),
          ("B","Perfect. Nobody can accuse us of copying anyone.")
        ]
    return beats

def main():
    topic=get_topic()
    os.makedirs("output", exist_ok=True)
    for kind in ("short","long"):
        beats=make_story(topic,kind)
        payload={"topic":topic,"kind":kind,"beats":beats,"created":datetime.now(timezone.utc).isoformat()}
        with open(f"output/{kind}_story.json","w",encoding="utf-8") as f: json.dump(payload,f,indent=2)
    print("Selected topic:",topic)
if __name__=="__main__": main()
