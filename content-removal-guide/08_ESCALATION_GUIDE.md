# Phase 5: Escalation for Unresponsive Platforms

If a platform ignores your DMCA notice and follow-up, there are several escalation paths. Work through them in order.

---

## Escalation Ladder

```
Step 1: Follow-up email (7 days after initial notice)
    ↓ No response after 7 more days
Step 2: File with hosting provider
    ↓ No response after 7 more days
Step 3: File with CDN / Cloudflare
    ↓ No response or site still up
Step 4: File with domain registrar
    ↓ Content still accessible
Step 5: Search engine de-indexing (if not done already)
    ↓ Content still accessible in Russia
Step 6: Roskomnadzor complaint (Russia-specific)
    ↓ Need broader legal action
Step 7: Professional removal service or lawyer
```

---

## Step 1: Follow-Up Email

Use the follow-up template from `04_DMCA_TEMPLATE.md` (Appendix B). Send 7 days after the original notice.

---

## Step 2: File with the Hosting Provider

The hosting provider is the company whose servers actually store the website's files. They have their own DMCA obligations.

### How to Find the Hosting Provider

1. Go to https://who.is/ or https://whois.domaintools.com/
2. Enter the domain name (e.g., `example-tube.com`)
3. Look for:
   - **Hosting Company** or **IP Address** — you can then look up the IP at https://ipinfo.io/
   - **Name Server** records — these sometimes indicate the host (e.g., `ns1.hostinger.com` means Hostinger)
4. If the site uses Cloudflare (name servers like `*.ns.cloudflare.com`), see Step 3 first to find the real host

### Major Hosting Provider Abuse Contacts

| Provider | Abuse Email | Abuse Form |
|---|---|---|
| Cloudflare | abuse@cloudflare.com | https://abuse.cloudflare.com/ |
| Amazon AWS | abuse@amazonaws.com | https://support.aws.amazon.com/#/contacts/report-abuse |
| Google Cloud | gc-abuse@google.com | https://support.google.com/code/contact/cloud_platform_report |
| Microsoft Azure | cert@microsoft.com | https://msrc.microsoft.com/report/abuse |
| OVH | abuse@ovh.net | https://www.ovh.com/abuse/ |
| Hetzner | abuse@hetzner.com | https://abuse.hetzner.com/ |
| DigitalOcean | abuse@digitalocean.com | https://www.digitalocean.com/company/contact/#abuse |
| Hostinger | abuse@hostinger.com | Via support ticket |
| GoDaddy | abuse@godaddy.com | https://supportcenter.godaddy.com/AbuseReport |
| Namecheap | abuse@namecheap.com | https://www.namecheap.com/support/abuse.aspx |

Send the same DMCA notice to the hosting provider, adding a note that the site operator has been unresponsive.

---

## Step 3: File with Cloudflare (if applicable)

Many sites use Cloudflare as a CDN/proxy, which hides their real hosting provider.

1. Go to: https://abuse.cloudflare.com/
2. Select "DMCA / Copyright" or "CSAM / Intimate Images"
3. Submit the infringing URLs and your DMCA notice
4. **Key benefit**: Cloudflare's response will often reveal the **real hosting provider's IP address** — use that to file directly with the host
5. Cloudflare itself does not host content and generally will not remove it, but they will forward your complaint and disclose the real host

---

## Step 4: File with the Domain Registrar

The domain registrar is the company where the site registered its domain name.

1. Find the registrar via WHOIS (see Step 2)
2. Most registrars have abuse policies that allow domain suspension for repeated DMCA violations
3. Send your DMCA notice to the registrar's abuse email
4. This is a **nuclear option** — the registrar may suspend the entire domain

---

## Step 5: Search Engine De-indexing

If you haven't already filed for de-indexing (see `06_SEARCH_ENGINE_DELISTING.md`), do so now. Even if the content remains on the source site, removing it from search results makes it effectively invisible to most people.

---

## Step 6: Roskomnadzor (Russian Internet Regulator)

Since the client is a Russian citizen, Roskomnadzor provides additional enforcement options under Russian law.

### What Roskomnadzor Can Do

- Order Russian ISPs to **block access** to specific URLs or entire domains within Russia
- Fine Russian companies that fail to comply with data removal requests
- Add sites to the **Unified Register of Prohibited Sites** (единый реестр)

### How to File

1. Go to: https://rkn.gov.ru/
2. Navigate to the complaint form (Обращение граждан)
3. Or file online at: https://eais.rkn.gov.ru/ (Unified Information System)
4. Select the appropriate complaint type:
   - **Personal data violation** (нарушение обработки персональных данных) — under Federal Law 152-FZ
   - **Copyright violation** — under Part IV of the Civil Code of the Russian Federation
5. Provide:
   - Your identity information
   - The URLs of the infringing content
   - Proof that the content depicts you and was shared without consent
   - Copies of any DMCA notices you've already sent (showing the site is non-compliant)

### Russian Legal Framework

- **Federal Law 152-FZ** ("On Personal Data"): You can demand deletion of personal data (which includes your image and likeness) from any data processor. Non-compliance is actionable through Roskomnadzor.
- **Civil Code, Part IV** (Copyright): Unauthorized recording and distribution of a live performance infringes the performer's exclusive rights (Articles 1317-1318).
- **Federal Law 149-FZ** ("On Information"): Provides mechanisms for blocking access to illegal content.

### Limitations

- Roskomnadzor can only enforce blocking **within Russia** — the content remains accessible from other countries
- The process can take **weeks to months**
- Most effective when combined with DMCA takedowns targeting the source content internationally

---

## Step 7: Professional Services and Legal Counsel

If the above steps are insufficient, or if the volume of content is overwhelming:

### Content Removal Services

These companies specialize in adult content takedowns:

| Service | Website | Pricing Model |
|---|---|---|
| DMCA.com | https://www.dmca.com/ | Per-takedown and subscription monitoring |
| Rulta | https://rulta.com/ | Subscription-based takedown and monitoring |
| Cam Model Protection | https://cammodelprotection.com/ | Monthly subscription tailored for cam performers |
| BrandItSafe | https://branditsafe.com/ | Custom pricing |
| Copyscape / DMCA Defender | https://www.dmca.com/Toolkit/DMCA-Defender.aspx | Monitoring + automated takedowns |

### When to Hire a Lawyer

Consider a lawyer if:

- A platform files a **DMCA counter-notice** (you have 14 days to file a lawsuit or the content goes back up)
- Content appears on sites in **jurisdictions with weak copyright enforcement**
- You want to pursue **monetary damages** against the uploader
- The volume of infringement is large enough to justify legal costs

### Finding the Right Lawyer

- Look for attorneys specializing in **internet law**, **intellectual property**, or **cyber civil rights**
- Organizations that may provide referrals or pro bono help:
  - **Cyber Civil Rights Initiative (CCRI)**: https://cybercivilrights.org/ — crisis helpline and legal referrals
  - **Without My Consent** (now part of CCRI)
  - **Electronic Frontier Foundation (EFF)**: https://www.eff.org/ — may provide guidance
- For Russian-specific legal matters, seek a lawyer familiar with both Russian IP law and international internet law

---

## Escalation Timeline Summary

| Day | Action |
|---|---|
| Day 0 | Send initial DMCA notice to site |
| Day 7 | Send follow-up if no response |
| Day 14 | File with hosting provider and CDN |
| Day 14 | File for search engine de-indexing (parallel) |
| Day 21 | File with domain registrar |
| Day 21 | File with Roskomnadzor (parallel) |
| Day 30+ | Engage professional removal service or lawyer |
