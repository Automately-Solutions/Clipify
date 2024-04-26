import re
from transformers import pipeline

# Load the summarization pipeline
summarizer = pipeline("summarization")

# Example input text with timestamps
transcript = """
00:00 The Pandora papers are the latest in a long line on P Papers that have supposedly unmasked the shady dealings of the global elite’s worldwide network of money laundering, tax evasion and corruption. You have no doubt seen the headlines, and if you are following the story closely you are likely thinking that nothing will really come of this.
00:18 It’s been five years since the Panama Papers were released the world and since then they have been followed up by the paradise papers, as well as a series of smaller leaks ultimately confirming what everybody suspected was going on anyway. Now to an outside observer it is easy to be a bit disheartened by all of this news and simply resign yourself to the fact that these schemes will just happen forever and nothing will really be done to punish the perpetrators.
00:43 This narrative would certainly be supported by the outlets publishing these stories too, because to be honest… outrage sells. But it’s not necessarily the case, and perhaps the best way to see this is to do what no stories on this issue have been willing to do, and that is to unpack how this creative international accounting actually functions.
"""

# Split the transcript into segments based on timestamps
segments = re.split(r'(\d{2}:\d{2})', transcript)
timestamps = segments[1::2]
texts = segments[2::2]

# Process each segment with the summarization model
for timestamp, text in zip(timestamps, texts):
    summarized = summarizer(text, max_length=45, min_length=5, do_sample=False)
    summary_text = summarized[0]['summary_text']
    print(f"{timestamp} {summary_text}")

