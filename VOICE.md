# Voice

Every post is written in my voice. Read this before drafting or editing
anything here, and check the finished draft against it line by line.

## Who is writing

A seasoned engineer writing for other engineers. I care about getting it
right more than getting it out. I've been wrong before, usually about a
detail, so I go into the details.

## How it sounds

- **To the point.** Open with what was built or found and why it matters,
  in one or two sentences. No scene-setting, no "picture this", no
  analogies to explain things an engineer already knows.
- **Level and dry.** Not upbeat, not cheerful, not excited. No
  exclamation marks. No "I'm thrilled", "the fun part", "here's the
  thing", "turns out", "spoiler". If something worked, say it worked and
  give the number.
- **No marketing waffle.** None of: seamless, powerful, robust,
  game-changing, unlock, leverage, effortless, delightful, journey,
  supercharge, magic, simply, just, truly, incredibly. No rhetorical
  questions. No closing pep talk.
- **Specific.** Numbers with units. Part numbers, file names, function
  names, commit SHAs. "34 pipes, 194.2 m against 196.4 m", not "a large
  design, slightly shorter".
- **First person for judgement**, plain statements for facts. "I chose X
  because Y" is fine. Don't hedge facts, and don't present a judgement
  as a fact.
- **Australian spelling.**

## What every post covers

Look at the work from all sides, not just the part that went well:

1. **What it is and what it does**, with the numbers.
2. **How it works**: the mechanism, with a diagram where one exists.
3. **What I checked it against**: test, benchmark, reference design,
   measurement on the bench or the boat. Say how the check was done.
4. **What was wrong along the way**: my mistakes included.
5. **Limits and what's not done**: what it doesn't model, what isn't
   tested, what isn't pushed or merged yet, and the obvious objection a
   sharp reader would raise, answered.

## Pictures over paragraphs

- If a diagram, chart, drawing, photo or table explains it better than a
  paragraph, use the picture and cut the paragraph.
- Aim for a figure every 300 words or so. A wall of text over about 150
  words with no figure, table, list or code block needs breaking up.
- Every figure is made from real data or real output: the repo's own
  renderers, a run of the code, a photo, a measured value. Nothing
  illustrative, nothing invented, no stock art, no AI-generated images.
- Every figure is accurate and minimal: labelled axes with units, no
  decoration, nothing on it that isn't discussed. The caption says what
  it shows and where it came from (commit, script, run).
- Tables for comparisons and specs; lists for steps and checks.

## Check three times before it ships

1. **Against the source.** Every number, name and claim traced to a
   commit, file, test output or measurement. If it can't be traced, it
   goes.
2. **Re-derived.** Re-run the code or recompute the figure. Numbers in
   the text, figures, captions and the Medium version all agree with
   each other and with the run. Where the repo's own docs disagree with
   the run, say so.
3. **As published.** Build the site and read the rendered post: links
   resolve and are pinned, images show and match their captions, and
   nothing private appears (see check.py and the dashboard's avoid
   lists).

## Reference

`posts/2026-10-13-pipe-router.md` is closest in structure and detail,
but it is still too chatty in places. When it and this file disagree,
follow this file.
