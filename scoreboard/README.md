# UseThisSI Scoreboard (Google Sheet 13vsJlhRDT1PG8zXQEcRcjC1dMlPRW-0-3fQUTc3wTRg)

Built to match the operating charter (../ops/CHARTER.md). Tabs: **Dashboard**, **Weekly Scorecard**, **Experiment Log**, **Daily Log**, **Guide**, calc (helper).
Dashboard sections: North Star & Goals (incl. required vs actual subs/day + red BEHIND flag), Freshness & Accuracy, Directory Engagement,
Growth, Money, Product Quality, Brand & Reach, Charts.

Nightly (8 PM PT):
1. Append ONE row to ../metrics.csv in this exact order (33 columns; blank = not live yet; quote fields containing commas):
   date,subscribers,net_new_subs,referrals,top_signup_source,site_visitors,google_indexed_pages,search_clicks,affiliate_clicks,affiliate_revenue,sponsor_inquiries,sponsor_revenue,x_followers,x_impressions,x_engagements,x_mentions_replies,open_rate,click_rate,tools_listed,notes,tools_checked_7d,tools_checked_30d,stale_tools_flagged,price_updates,corrections_made,avg_fix_hours,outbound_clicks,top_use_case,top_tool_clicks,affiliate_programs_approved,affiliate_programs_pending,unsub_rate,briefs_sent
   - date YYYY-MM-DD (PT); one row per date (re-running a day: replace that row, don't add a 2nd)
   - stocks (end-of-day totals): subscribers, google_indexed_pages, x_followers, tools_listed, affiliate_programs_approved, affiliate_programs_pending
   - flows (that day only): net_new_subs, referrals, site_visitors (= unique visitors), search_clicks, affiliate_clicks, affiliate_revenue,
     sponsor_inquiries, sponsor_revenue, x_impressions, x_engagements, x_mentions_replies, price_updates, corrections_made, outbound_clicks, briefs_sent
   - rates: open_rate/click_rate/unsub_rate of the issue sent that day as "45%" (blank if no send); real readers only
   - avg_fix_hours: average hours from noticing to fixing today's corrections (blank if unknown)
   - top_use_case / top_tool_clicks: the use case / tool with the most outbound clicks today (text)
   - briefs_sent: briefs sent today (1 on a normal weekday, 0 on a missed weekday, blank on weekends)
   - revenue in USD, plain number (12.50)
   - AUTO, leave blank: tools_checked_7d, tools_checked_30d, stale_tools_flagged. build_sheet.py fills them for the latest row from
     ../data.csv `last_checked` (per unique tool; oldest date across its rows; blank = never verified = stale; stale = blank or older than 30 days)
     and writes them back to metrics.csv. Freshness % on the Dashboard = these counts / tools_listed.
2. Freshness: when a tool is re-verified on its official page, set its `last_checked` in ../data.csv to that date (YYYY-MM-DD).
   Never set a date for a tool that wasn't actually checked. The site shows the per-tool date (blank shows "no recorded check yet").
3. python3 scoreboard/build_sheet.py   (validates headers, field counts, dates, numbers, duplicate dates/weeks, experiment decisions,
   data.csv last_checked format; exits non-zero on error)
4. Drive connector user-Google-drive -> update_file_content with the args in scoreboard/upload_args.json
   (fileId above, contentMimeType application/vnd.ms-excel, textContent "$file:/workspace/usethissi/scoreboard/scoreboard.xml").
   Same file id/URL every time. Do NOT upload metrics.csv as text/csv: that would wipe the dashboard.
5. Optional check: DownloadFile the sheet (xlsx) and confirm 'Daily Log' has len(csv rows)+1 rows and no #REF!/#VALUE!/#NAME?/#ERROR! cells.

Weekly (at the weekly review): add ONE row to ../ops/weekly.csv
   week_start,shipped,biggest_mover,next_action,blockers
   (week_start = Monday YYYY-MM-DD; next_action = the single highest-leverage next action; blockers = blockers or escalations for Baz)
Every experiment: add ONE row to ../ops/experiments.csv
   date,test,metric,result,decision
   (decision = keep | kill | iterate; blank = still running). Both tabs are rebuilt from these CSVs, newest first.

The Dashboard tab is 100% formulas reading Daily Log (via the helper tab "calc"), so only data changes nightly.
calc layout: v1 columns (date..notes) spill into calc A:T, v2 columns (tools_checked_7d..briefs_sent) into calc BA:BM; calc columns
26/52/78 (Z/AZ/BZ) are never referenced (importer quirk). Required vs actual subs/day uses the next unmet subscriber goal (25 by launch+7,
300 by launch+1 month, 10,000 by launch+1 year) and the 7-day average of net_new_subs.
Backups: backup-before-redesign-2026-10-15.xlsx, backup-before-v2-2026-10-15.xlsx (sheet before the charter columns);
old CSV schema: metrics.v1-backup-2026-10-15.csv.
- Subscriber counts must exclude owner addresses bazfurry@gmail.com and bazfurry@mail.grokbot.com (and any other owner test addresses), and so must open, click and unsubscribe rates where possible.
