# beehiiv sender branding (Baz: do FIRST)

Findings (Oct 23, 2026): usethissi.com DNS is on Vercel. MX = mx1/mx2.forwardemail.net (Forward Email free plan),
TXT `forward-email=info:bazfurry@gmail.com`. So **info@usethissi.com already exists** and forwards. No new mailbox, no cost.
It is already the public contact address on the site and kit.

Browser steps (needs a person/browser session on beehiiv as usethissi):
1. Settings > Publication (General): Publication name "UseThisSI"; Logo / thumbnail: upload `static/brand/usethissi-logo-512.png`
   (512x512 upscaled from the 192px site icon; replace with a crisper master if one exists).
2. Settings > Emails (Email settings): "From"/Sender name = `UseThisSI`; Reply-to email = `info@usethissi.com` (verify via the
   link beehiiv emails to that address; it arrives through the forward).
3. Send a test email to yourself; confirm From shows "UseThisSI", the logo shows in the header, and Reply goes to info@usethissi.com.

Note: replies still land in Baz's Gmail via the forward, but the personal address is no longer exposed. To stop that,
change the TXT to forward to a different inbox (Vercel DNS, free) — needs Baz's choice of destination.
A custom sending domain (send from @usethissi.com) is a paid beehiiv feature; not needed for this fix.
