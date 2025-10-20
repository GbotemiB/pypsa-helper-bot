# Getting Started with Azure - Quick Guide

## 🎯 Current Status

✅ Azure CLI installed (version 2.78.0)  
❌ No Azure subscription found  
❌ Need to sign up for Azure

---

## 📝 Next Steps

### Option 1: Azure for Students (No Credit Card Required!) 🎓

**Best if you have a .edu email address**

1. **Go to:** https://azure.microsoft.com/free/students/

2. **Click "Start Free"**

3. **Sign in** with your Microsoft account (gbotemibolarinwa@gmail.com or create new)

4. **Verify student status**:
   - Option A: Use .edu email address
   - Option B: Upload student ID
   - Option C: Verify through your institution

5. **Get benefits:**
   - $100 Azure credit (renews annually while student)
   - No credit card required
   - Access to free services

6. **After signup, return and run:**
   ```bash
   /opt/homebrew/bin/az login
   ```

---

### Option 2: Azure Free Trial (Requires Credit Card) 💳

**If you don't have a .edu email**

1. **Go to:** https://azure.microsoft.com/free/

2. **Click "Start free"**

3. **Sign in** with your Microsoft account

4. **Provide credit card** (for identity verification only - won't be charged)

5. **Complete verification**

6. **Get benefits:**
   - $200 credit for 30 days
   - 12 months of popular free services
   - Always-free services

7. **After signup, return and run:**
   ```bash
   /opt/homebrew/bin/az login
   ```

---

## ✅ After You Sign Up

Once you have an Azure subscription:

### 1. Login to Azure CLI
```bash
/opt/homebrew/bin/az login
```

This will open your browser for authentication.

### 2. Verify subscription
```bash
/opt/homebrew/bin/az account list --output table
```

You should see your subscription listed.

### 3. Follow the full setup guide
Open and follow: `docs/AZURE_SETUP.md`

---

## 🔧 Add Azure CLI to your PATH (Optional but Recommended)

To use `az` instead of `/opt/homebrew/bin/az`:

```bash
# Add to your ~/.zshrc
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Now you can use just 'az'
az --version
```

---

## 💰 Cost Comparison

| Option | Credit | Duration | Credit Card? | Best For |
|--------|--------|----------|--------------|----------|
| **Azure for Students** | $100 | Renews annually | ❌ No | Students with .edu email |
| **Azure Free Trial** | $200 | 30 days | ✅ Yes | Anyone with credit card |

**For this bot:** Costs ~$67/month, so:
- Students: ~1.5 months free
- Free trial: ~3 months free

---

## 🎓 Student Verification Tips

### If using .edu email:
- Use your official school email
- Check spam for verification email
- May take a few hours to verify

### If uploading student ID:
- Take clear photo of current student ID
- Make sure name and expiration date visible
- Upload in JPEG or PNG format

### If institution verification fails:
- Try different .edu email if you have multiple
- Contact Azure support via chat
- Consider regular free trial instead

---

## 🚨 Troubleshooting

### "No subscriptions found"
**Solution:** You haven't signed up for Azure yet. Follow Option 1 or 2 above.

### "Multi-factor authentication required"
**Solution:** Complete MFA setup at https://account.microsoft.com/security

### "Credit card required"
**Solutions:**
1. Use Azure for Students (no CC needed)
2. Ask family member to use their CC
3. Use prepaid virtual card (some work)
4. Consider alternative: Railway.app (no CC needed)

### "Student verification failed"
**Solutions:**
1. Try with different .edu email
2. Upload clear student ID photo
3. Wait 24-48 hours and try again
4. Contact Azure support
5. Use regular free trial with CC

---

## 🔄 Alternative Platforms (If Azure Doesn't Work)

If you can't get Azure working, consider these alternatives:

### 1. Railway.app (Easiest!)
- **Cost:** $5 free credit/month
- **Credit card:** Not required
- **Setup:** 10 minutes
- **Good for:** Student projects
- **Link:** https://railway.app

### 2. Render.com
- **Cost:** 750 free hours/month
- **Credit card:** Not required
- **Caveat:** Sleeps after inactivity (not ideal for Discord bots)
- **Link:** https://render.com

### 3. Google Cloud Run
- **Cost:** $300 credit for 90 days
- **Credit card:** Required
- **Good for:** Pay-per-use (cheap for Discord bots)
- **Link:** https://cloud.google.com/run

### 4. Self-hosting (100% Free!)
- **Cost:** $0 (just electricity)
- **Requirements:** Computer that stays on 24/7
- **Good for:** Learning, full control
- **Setup:** Just run `python src/bot.py`

---

## 📚 Next Steps After Signup

1. ✅ Complete Azure signup
2. ✅ Login via `az login`
3. ✅ Verify subscription
4. 📖 Follow `docs/AZURE_SETUP.md` for full deployment
5. 🚀 Deploy your bot!

---

## ❓ Questions?

- **Azure Student Help:** https://aka.ms/AzureStudentSupport
- **Azure Free Trial Help:** https://azure.microsoft.com/support/
- **Repository Issues:** https://github.com/GbotemiB/pypsa-helper-bot/issues

---

**Ready to sign up?** Choose your option above and get started! 🎉
