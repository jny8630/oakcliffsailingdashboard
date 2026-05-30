# Feedback Inbox — Airtable Setup Guide

Follow these steps this evening. Takes about 15 minutes.
At the end, you'll paste one URL into `feedback.html` and the form goes live.

---

## Step 1 — Create your Airtable account

1. Go to [airtable.com](https://airtable.com)
2. Sign up with your Google account (`jens.nachtigal@gmail.com`) — easiest for later integrations
3. Skip the onboarding wizard or click through it quickly — you'll build the base manually below

---

## Step 2 — Create the base

1. From the Airtable home screen, click **"+ Create a base"**
2. Choose **"Start from scratch"**
3. Name it: **NYC Harbor Feedback**
4. Click **Create**

---

## Step 3 — Configure the fields

You'll see a default table with some pre-filled fields. Delete or rename them to match exactly:

| Field name | Field type | Notes |
|---|---|---|
| `Description` | Long text | Required. The main submission field. |
| `Name` | Single line text | Optional. For follow-up if submitter wants. |
| `Image` | Attachment | Optional. For screenshots or photos. |
| `Status` | Single select | Options: `New`, `Reviewing`, `Implemented`, `Declined` |
| `Submitted` | Created time | Auto-filled by Airtable — do not put this in the form |

**To add a field:** Click the **+** button to the right of the last column header.

**To delete a field:** Right-click the column header → Delete field.

**For the Status field:** After creating it as Single select, click the field to add the four options listed above. Set the default to `New`.

---

## Step 4 — Create the form

1. In the left sidebar, click **"+ Add or import"** → **"Form"**
2. Airtable creates a form linked to this table
3. Name the form: **NYC Harbor — Suggest a Change**
4. In the form editor:
   - **Description** — mark as Required, set label to: *"What would you change or what's not working?"*
   - **Name** — leave optional, set label to: *"Your name (optional)"*
   - **Image** — leave optional, set label to: *"Screenshot or photo (optional)"*
   - **Remove** the `Status` and `Submitted` fields from the form — they're for your internal use only

5. Under **"After submit"** (bottom of form settings), choose **"Show a thank you message"**
   - Message: *"Thanks — Jens will review this soon."*

---

## Step 5 — Turn on email notifications

1. In the form editor, look for **"Email me when someone submits"** or go to **Automations** (left sidebar)
2. Set up: **When form submitted → Send email to jens.nachtigal@gmail.com**
3. Include the record in the email so you can see description + image without opening Airtable

---

## Step 6 — Get the embed URL

1. In the form editor, click **"Share"** (top right)
2. Copy the **Embed link** — it looks like:
   ```
   https://airtable.com/embed/shrXXXXXXXXXXXXXX
   ```
   (Not the plain share link — specifically the embed version)

---

## Step 7 — Activate the form in the dashboard

Open `feedback.html` and find this line (near the top of the `<script>` block):

```javascript
const AIRTABLE_EMBED_URL = 'PASTE_YOUR_EMBED_URL_HERE';
```

Replace `PASTE_YOUR_EMBED_URL_HERE` with your embed URL. Save the file.

The form is now live. Test it:
1. Submit a text-only entry → check your email arrives
2. Submit with an image attached → confirm image is accessible in Airtable
3. Open `index.html` → confirm the Feedback button navigates to the form

---

## What Jens sees after a submission

- **Email** arrives with the description text and image link
- **Airtable grid view** shows all submissions with Status column for tracking
- To paste into Claude Code: copy the description text, share the image file, ask Claude to evaluate

---

## Notes

- Free Airtable tier: 1,000 records, 2 GB storage — more than enough for a sailing season
- Same account will be used for the boarding school search database when that project is ready
- If the iframe doesn't load on a specific browser, `feedback.html` shows a direct link fallback
