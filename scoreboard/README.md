# UseThisSI Scoreboard (Google Sheet 13vsJlhRDT1PG8zXQEcRcjC1dMlPRW-0-3fQUTc3wTRg)

Nightly (8 PM PT):
1. Append ONE row to ../metrics.csv in this exact order (blank = not live yet; quote notes containing commas):
   date,subscribers,net_new_subs,referrals,top_signup_source,site_visitors,google_indexed_pages,search_clicks,affiliate_clicks,affiliate_revenue,sponsor_inquiries,sponsor_revenue,x_followers,x_impressions,x_engagements,x_mentions_replies,open_rate,click_rate,tools_listed,notes
   - date YYYY-MM-DD (PT); one row per date (re-running a day: replace that row, don't add a 2nd)
   - stocks (end-of-day totals): subscribers, google_indexed_pages, x_followers, tools_listed
   - flows (that day only): net_new_subs, referrals, site_visitors, search_clicks, affiliate_clicks, affiliate_revenue, sponsor_inquiries, sponsor_revenue, x_impressions, x_engagements, x_mentions_replies
   - rates: open_rate/click_rate of the issue sent that day as "45%" (blank if no send)
   - revenue in USD, plain number (12.50)
2. python3 scoreboard/build_sheet.py   (validates header, field count, duplicate dates; exits non-zero on error)
3. Drive connector user-Google-drive -> update_file_content with the args in scoreboard/upload_args.json
   (fileId above, contentMimeType application/vnd.ms-excel, textContent "$file:/workspace/usethissi/scoreboard/scoreboard.xml").
   Same file id/URL every time. Do NOT upload metrics.csv as text/csv: that would wipe the dashboard.
4. Optional check: DownloadFile the sheet (xlsx) and confirm 'Daily Log' has len(csv rows)+1 rows.

The Dashboard tab is 100% formulas reading Daily Log (via the helper tab "calc"), so only data changes nightly.
Backup of the pre-redesign sheet: backup-before-redesign-2026-10-15.xlsx; old CSV schema: metrics.v1-backup-2026-10-15.csv.
- Subscriber counts must exclude owner addresses bazfurry@gmail.com and bazfurry@mail.grokbot.com (and any other owner test addresses), and so must open and click rates where possible.
