import sys, os, unittest
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
import newsletter_guard as g

GOOD = """Subject: OpenAI's new API answers yes-or-no for a dime
Preheader: OpenAI launched an API for fast yes-or-no calls, and Claude is now GA on Google Cloud.

---

Five minutes, only what matters if you build things.

## The big one
### OpenAI Decisions API: cheap, fast yes-or-no calls (Oct 22)
**What happened:** OpenAI made the Decisions API generally available for bounded questions in one request.
**The catch:** It only returns bounded answers, so it cannot write text or explain itself in prose at all.
**How to try it:** Rewrite one filter as a yes-or-no question and run 50 real examples through both.
[Read the source](https://openai.com/index/decisions-api/)
"""

class T(unittest.TestCase):
    def test_good(self):
        self.assertEqual(g.guard_paste(GOOD), [])
    def test_empty(self):
        e = g.guard_paste("Subject: Hook first here\nPreheader: " + "x"*50 + "\n\n---\n\n")
        self.assertTrue(any("empty" in x for x in e))
    def test_no_big_one(self):
        e = g.guard_paste(GOOD.replace("## The big one", "## Something"))
        self.assertTrue(any("The big one" in x for x in e))
    def test_plus_subject(self):
        e = g.guard_paste(GOOD.replace("Subject: OpenAI's new API answers yes-or-no for a dime", "Subject: OpenAI ships X, plus Mistral Y"))
        self.assertTrue(any("plus" in x for x in e))
    def test_no_preview(self):
        e = g.guard_paste(GOOD.replace("Preheader:", "Nope:"))
        self.assertTrue(any("preview" in x for x in e))
    def test_bare_url(self):
        e = g.guard_paste(GOOD + "\nSee https://example.com/x\n")
        self.assertTrue(any("bare" in x for x in e))
    def test_missing_catch(self):
        e = g.guard_paste(GOOD.replace("**The catch:**", "**Note:**"))
        self.assertTrue(any("The catch" in x for x in e))
    def test_rendered(self):
        ok = "<p>The big one</p>" + "<p>" + "word "*60 + '<a href="https://a.com">Source</a></p>'
        e = []; g.check_rendered(ok, e); self.assertEqual(e, [])
        for bad in ["<p>## The big one</p>", "<p>**What happened**</p>", "<p>https://openai.com</p>"]:
            e = []; g.check_rendered(ok + bad, e); self.assertTrue(e, bad)
        e = []; g.check_rendered("<p></p>", e); self.assertTrue(any("empty" in x for x in e))
    def test_send_slot(self):
        AZ = g.AZ
        s = g.next_send_slot(datetime(2026,10,23,6,0,tzinfo=AZ)); self.assertEqual((s.day,s.hour,s.minute),(23,7,15))
        s = g.next_send_slot(datetime(2026,10,20,16,42,tzinfo=AZ)); self.assertEqual((s.day,s.hour,s.minute),(21,7,15))
        s = g.next_send_slot(datetime(2026,10,23,9,0,tzinfo=AZ)); self.assertEqual((s.day,s.hour),(26,7))  # Fri late -> Mon

if __name__ == "__main__":
    unittest.main()
