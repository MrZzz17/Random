# Shopify App Setup Guide

Step-by-step instructions for installing and configuring the recommended app stack for your dropshipping store.

---

## Priority Order

Install apps in this order. Each builds on the previous.

1. **Supplier Integration** (DSers or Zendrop) — connect to product suppliers
2. **Reviews** (Judge.me) — social proof on product pages
3. **Email Marketing** (Klaviyo) — automated email flows
4. **Conversion Tools** (Vitals) — urgency, social proof, upsells
5. **Google Shopping** — product feed for Google ads

---

## 1. DSers — AliExpress Supplier Integration

**Cost:** Free (Basic) / $19.90/mo (Advanced) / $49.90/mo (Pro)
**Start with:** Free tier

### Installation

1. Go to [apps.shopify.com/dsers](https://apps.shopify.com/dsers)
2. Click "Add app" and authorize with your Shopify store
3. Create a DSers account (use store email)
4. Link your AliExpress account (you'll need one — sign up at aliexpress.com)

### Configuration

1. **Settings > Shipping:**
   - Set default shipping method to "ePacket" or "AliExpress Standard Shipping"
   - Enable "Auto select the cheapest shipping method" as a fallback
   
2. **Settings > Order:**
   - Enable "Auto sync tracking numbers to Shopify"
   - Enable "Auto update order status"
   - Set order note: leave blank (keeps supplier branding off)
   
3. **Settings > Notification:**
   - Enable email notifications for failed orders
   - Enable low-stock alerts

### Adding Products

1. Go to DSers > Find Suppliers
2. Search for your niche products
3. Click "Add to DSers" on products you want
4. Map variants (size, color) to your Shopify variants
5. Set your retail prices (use the pricing calculator)
6. Click "Push to Shopify" to publish

### Order Fulfillment

1. Customer places order on your Shopify store
2. Order appears in DSers > Open Orders
3. Click "Place Order to AliExpress" (or enable auto-ordering on paid plans)
4. Pay the supplier on AliExpress
5. Tracking number auto-syncs to Shopify when supplier ships

### Alternative: Zendrop

If you prefer faster shipping and branded packaging:

1. Go to [apps.shopify.com/zendrop](https://apps.shopify.com/zendrop)
2. Free tier: manual orders. $49/mo: auto-fulfillment + branded invoices
3. Zendrop has US warehouse options for many products (5-8 day shipping)
4. Setup is similar to DSers but with a built-in product catalog

---

## 2. Judge.me — Product Reviews

**Cost:** Free (basic) / $15/mo (Awesome plan)
**Start with:** Free tier

### Installation

1. Go to [apps.shopify.com/judgeme](https://apps.shopify.com/judgeme)
2. Click "Add app" and authorize
3. Follow the automatic setup wizard

### Configuration

1. **Display Settings:**
   - Enable "Review Widget" on product pages (auto-installed)
   - Enable "Star Rating" on collection pages
   - Enable "All Reviews" page (/pages/reviews)
   
2. **Email Settings:**
   - Enable "Review Request Email" — sends 14 days after delivery
   - Customize email template with your brand colors/logo
   - Enable photo reviews (customers upload photos with reviews)
   
3. **Widget Style:**
   - Match widget colors to your store theme
   - Set "Stars Color" to match your accent color (#E94560)
   - Enable "Verified Buyer" badge
   
4. **Import Reviews (optional):**
   - Use Judge.me's AliExpress review importer to seed initial reviews
   - Go to Judge.me > Content > Import > AliExpress
   - Paste product URL and import 10-20 reviews per product
   - Edit imported reviews for quality/relevance

---

## 3. Klaviyo — Email Marketing

**Cost:** Free up to 250 contacts / Pay-as-you-grow after
**Start with:** Free tier

### Installation

1. Go to [apps.shopify.com/klaviyo-email-marketing](https://apps.shopify.com/klaviyo-email-marketing)
2. Click "Add app" and authorize
3. Complete the onboarding wizard

### Essential Automated Flows

Set these up before launch:

#### Welcome Series (3 emails)

1. Go to Klaviyo > Flows > Create Flow > "Welcome Series"
2. Trigger: When someone subscribes to your email list
3. Email 1 (immediately): Welcome + 10% discount code
   - Subject: "Welcome! Here's 10% off your first order"
   - Include brand story, best-selling products, discount code
4. Email 2 (Day 3): Product showcase
   - Subject: "Our customers' favorites"
   - Feature top 3-4 products with lifestyle images
5. Email 3 (Day 7): Social proof
   - Subject: "See why 1,000+ customers love us"
   - Customer reviews, user photos, and CTA to shop

#### Abandoned Cart (3 emails)

1. Go to Flows > Create Flow > "Abandoned Cart"
2. Trigger: When someone starts checkout but doesn't complete
3. Email 1 (1 hour): Reminder
   - Subject: "You left something behind"
   - Show the abandoned product(s), link back to cart
4. Email 2 (24 hours): Urgency
   - Subject: "Your cart is about to expire"
   - Add scarcity ("Only X left in stock")
5. Email 3 (72 hours): Incentive
   - Subject: "Here's 10% off to complete your order"
   - Include a discount code (auto-generated in Klaviyo)

#### Post-Purchase (2 emails)

1. Trigger: When order is fulfilled
2. Email 1 (Day 3 after delivery): Check-in
   - Subject: "How's your new [product]?"
   - Ask for feedback, link to review page
3. Email 2 (Day 14): Cross-sell
   - Subject: "Based on your purchase, you'll love these"
   - Recommend related products

#### Win-Back (2 emails)

1. Trigger: Customer hasn't purchased in 30 days
2. Email 1 (Day 30): "We miss you"
   - Subject: "It's been a while — here's something special"
   - Include a 15% discount code
3. Email 2 (Day 60): Last attempt
   - Subject: "Last chance: 20% off just for you"
   - Stronger discount, urgency

### Signup Form

1. Go to Klaviyo > Signup Forms
2. Create a popup form:
   - Trigger: After 5 seconds or 30% scroll
   - Offer: "Get 10% off your first order"
   - Collect: Email only (don't ask for name yet)
   - Match colors to your store theme

---

## 4. Vitals — All-in-One Conversion Tools

**Cost:** $29.99/mo (14-day free trial)
**Install after you have a few sales**

### Installation

1. Go to [apps.shopify.com/vitals](https://apps.shopify.com/vitals)
2. Click "Add app" and authorize
3. Vitals bundles 40+ tools — only enable what you need

### Recommended Features to Enable

1. **Sales Pop (Social Proof)**
   - Shows "Someone in [city] just purchased [product]" popups
   - Settings: Show every 30 seconds, bottom-left position, auto-hide after 5s
   
2. **Urgency / Countdown Timer**
   - Add to product pages alongside or instead of the custom Liquid snippet
   - Set 24-hour rotating timer
   
3. **Stock Scarcity**
   - Show "Only X left in stock" on product pages
   - Set range: 3-15 units
   
4. **Trust Badges**
   - Add payment trust badges below the Add to Cart button
   - Select: Visa, Mastercard, PayPal, Secure Checkout
   
5. **Sticky Add to Cart**
   - Persistent add-to-cart bar when scrolling down product pages
   - Shows product image, price, and button
   
6. **Currency Converter**
   - Auto-detect visitor's country and show local currency
   - Essential if selling internationally
   
7. **Size Chart (if applicable)**
   - Add to apparel/wearable products

### Features to Skip Initially

- Wheel of Fortune popup (can feel spammy)
- Bundle products (wait until you have data on what sells together)
- Wishlist (nice-to-have, not essential at launch)

---

## 5. Google & YouTube Channel

**Cost:** Free
**Install in Week 3-4**

### Installation

1. Go to [apps.shopify.com/google](https://apps.shopify.com/google)
2. Click "Add app" and authorize
3. Connect your Google account

### Configuration

1. **Google Merchant Center:**
   - Create a Merchant Center account if you don't have one
   - Verify and claim your website domain
   - Connect Shopify product feed (auto-syncs)
   
2. **Product Feed:**
   - All active products auto-sync to Google Merchant Center
   - Ensure each product has: title, description, price, availability, and at least one image
   - Fix any disapproved products (common issues: missing GTIN, unclear images)
   
3. **Google Ads:**
   - Link Google Ads account to Merchant Center
   - Create Smart Shopping campaign or Performance Max campaign
   - Start with $15-20/day budget
   - Target: USA (or your primary market)

---

## 6. Optional Apps (Add Later)

### Once You're Profitable

| App | Cost | Purpose | When to Add |
|-----|------|---------|-------------|
| PageFly / GemPages | $24-29/mo | Custom landing pages for ads | When running multiple ad campaigns |
| AfterShip | Free-$11/mo | Branded tracking page | When getting 50+ orders/month |
| Smile.io | Free-$49/mo | Loyalty/rewards program | When you have repeat customers |
| Tidio | Free-$19/mo | Live chat with AI | When customer inquiries exceed 10/day |
| TikTok Channel | Free | Sync products to TikTok Shop | When TikTok ads are working |
| ReConvert | Free-$7.99/mo | Post-purchase upsells | When optimizing for AOV |

---

## App Budget Summary

### Month 1 (Launch)

| App | Plan | Cost |
|-----|------|------|
| DSers | Free | $0 |
| Judge.me | Free | $0 |
| Klaviyo | Free (<250 contacts) | $0 |
| Google Channel | Free | $0 |
| **Total** | | **$0/mo** |

### Month 2-3 (Growing)

| App | Plan | Cost |
|-----|------|------|
| DSers | Advanced | $19.90 |
| Judge.me | Free | $0 |
| Klaviyo | Free | $0 |
| Vitals | Standard | $29.99 |
| Google Channel | Free | $0 |
| **Total** | | **$49.89/mo** |

### Month 4+ (Scaling)

| App | Plan | Cost |
|-----|------|------|
| DSers | Pro | $49.90 |
| Judge.me | Awesome | $15.00 |
| Klaviyo | Paid tier | $20-45 |
| Vitals | Standard | $29.99 |
| Google Channel | Free | $0 |
| PageFly | Pay-as-you-go | $24.00 |
| **Total** | | **$138-163/mo** |

Only upgrade when the revenue justifies it. A good rule of thumb: app costs should never exceed 5% of monthly revenue.
