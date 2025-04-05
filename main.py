import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token from @BotFather
TOKEN = "7848941699:AAHl9huHbUgfCeZ9-Crl1_0xpJgG8SrbIPw"

# Admin IDs - list of admin Telegram IDs
ADMIN_IDS = [
    123456789,  # Replace with your main admin ID
]

# Store redemption codes with additional info
redemption_codes = {
    # "code": {"added_by": admin_id, "added_on": timestamp, "used_by": None, "type": "type"}
}

# Initialize some demo codes
def init_demo_codes():
    # Reward types
    reward_types = [
        "Premium Skin",
        "Legendary Weapon",
        "1000 Coins",
        "Character Bundle",
        "Battle Pass",
        "Rare Emote",
        "Vehicle Skin",
        "Special Avatar",
        "500 Diamonds",
        "Mystery Box"
    ]
    
    # Code prefixes
    prefixes = ["GAME", "HERO", "ITEM", "GIFT", "RARE", "EPIC", "COIN", "SKIN", "PASS", "BOX"]
    
    demo_codes = {}
    
    # Generate 200 unique codes
    for i in range(200):
        # Create unique code format
        prefix = prefixes[i % len(prefixes)]
        number = f"{i+1:03d}"  # Format number as 3 digits (001, 002, etc.)
        random_chars = "".join([chr(ord('A') + (i*3 + j) % 26) for j in range(4)])
        
        code = f"{prefix}{number}-{random_chars}-{number[::-1]}"
        reward_type = reward_types[i % len(reward_types)]
        
        demo_codes[code] = {
            "added_by": ADMIN_IDS[0],
            "added_on": 0,
            "used_by": None,
            "type": reward_type
        }
    
    # Add some special codes
    special_codes = {
        "SUPER-RARE-2024": {
            "added_by": ADMIN_IDS[0],
            "added_on": 0,
            "used_by": None,
            "type": "Ultra Rare Bundle"
        },
        "VIP-PASS-2024": {
            "added_by": ADMIN_IDS[0],
            "added_on": 0,
            "used_by": None,
            "type": "VIP Season Pass"
        },
        "DIAMOND-PACK-24": {
            "added_by": ADMIN_IDS[0],
            "added_on": 0,
            "used_by": None,
            "type": "2000 Diamonds"
        }
    }
    
    demo_codes.update(special_codes)
    redemption_codes.update(demo_codes)

async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to add admins.")
        return
        
    try:
        new_admin_id = int(context.args[0])
        if new_admin_id in ADMIN_IDS:
            await update.message.reply_text("⚠️ This user is already an admin.")
            return
            
        ADMIN_IDS.append(new_admin_id)
        await update.message.reply_text(f"✅ Added new admin with ID: {new_admin_id}")
    except (ValueError, IndexError):
        await update.message.reply_text("⚠️ Please provide a valid admin ID.\nFormat: /addadmin 123456789")

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to remove admins.")
        return
        
    try:
        admin_id = int(context.args[0])
        if admin_id not in ADMIN_IDS:
            await update.message.reply_text("⚠️ This user is not an admin.")
            return
            
        ADMIN_IDS.remove(admin_id)
        await update.message.reply_text(f"✅ Removed admin with ID: {admin_id}")
    except (ValueError, IndexError):
        await update.message.reply_text("⚠️ Please provide a valid admin ID.\nFormat: /removeadmin 123456789")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    
    # Check if this is user's first visit
    is_first_visit = user_id not in context.user_data.get('visited', set())
    if 'visited' not in context.user_data:
        context.user_data['visited'] = set()
    context.user_data['visited'].add(user_id)
    
    # Create welcome message with user info
    welcome_message = (
        f"🌟 *Welcome to Premium Game Rewards!* 🌟\n\n"
        f"👤 *User Profile*\n"
        f"├ Name: {user.first_name}\n"
        f"├ ID: `{user_id}`\n"
        f"└ Username: @{user.username if user.username else 'Not set'}\n\n"
    )
    
    if is_first_visit:
        welcome_message += (
            "🎉 *Welcome Bonus Activated!*\n"
            "You're eligible for special rewards.\n\n"
        )
    
    welcome_message += (
        "🎮 *Available Features:*\n"
        "├ Get Exclusive Game Codes\n"
        "├ Premium In-Game Items\n"
        "├ Special Character Skins\n"
        "├ Rare Weapons & Equipment\n"
        "└ Limited Time Rewards\n\n"
        "🎁 *Current Rewards Include:*\n"
        "├ Ultra Rare Bundles\n"
        "├ Premium Character Skins\n"
        "├ Legendary Weapons\n"
        "├ In-Game Currency\n"
        "└ Special Event Items\n\n"
        "🔥 *Daily Updates:*\n"
        "New codes and rewards added regularly!\n\n"
        "Select an option below to continue:"
    )
    
    # Create keyboard with beautiful emojis
    keyboard = [
        [
            InlineKeyboardButton("🎯 Get Code Now", callback_data="get_code"),
            InlineKeyboardButton("🎁 View Rewards", callback_data="show_rewards")
        ],
        [
            InlineKeyboardButton("📊 My History", callback_data="my_history"),
            InlineKeyboardButton("🎮 Game Guide", callback_data="how_to_use")
        ],
        [
            InlineKeyboardButton("💎 Premium Rewards", callback_data="premium_rewards"),
            InlineKeyboardButton("❓ Support", callback_data="support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send user's profile photo if available
    try:
        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        if photos.photos:
            await update.message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=welcome_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                welcome_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    except:
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def show_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Get unique reward types
    reward_types = set(info["type"] for info in redemption_codes.values())
    available_rewards = "\n".join(f"• {reward}" for reward in sorted(reward_types))
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🎁 Available Rewards:\n\n"
        f"{available_rewards}\n\n"
        "Click 'Get Redemption Code' to receive your reward!",
        reply_markup=reply_markup
    )

async def my_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Find codes used by this user
    user_codes = {code: info for code, info in redemption_codes.items() if info['used_by'] == user_id}
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if user_codes:
        message = "📊 Your Redemption History:\n\n"
        for code, info in user_codes.items():
            message += f"🎮 Code: {code}\n"
            message += f"🎁 Reward: {info['type']}\n"
            message += "───────────────\n"
    else:
        message = "📊 Your Redemption History:\n\n"
        message += "You haven't used any codes yet!\n"
        message += "Click 'Get Redemption Code' to get started."
    
    await query.message.reply_text(message, reply_markup=reply_markup)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("📱 Contact Support", url="https://t.me/YourSupportUsername")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "❓ Need Help?\n\n"
        "Common Issues:\n"
        "• Make sure to copy the full code\n"
        "• Each code can only be used once\n"
        "• Codes are case-sensitive\n\n"
        "Still having problems?\n"
        "Contact our support team!",
        reply_markup=reply_markup
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await start(query, context)

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text(
        "📌 How to Use the Bot:\n\n"
        "1. Click 'Get Redemption Code'\n"
        "2. Copy your code\n"
        "3. Use it in your game\n\n"
        "⚠️ Each code can only be used once!"
    )

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    available_codes = [code for code, info in redemption_codes.items() if not info['used_by']]
    if available_codes:
        code = available_codes[0]
        reward_type = redemption_codes[code]['type']
        redemption_codes[code]['used_by'] = user_id
        await query.message.reply_text(
            "🎉 Here's your redemption code:\n\n"
            f"🎮 Code: `{code}`\n"
            f"🎁 Reward: {reward_type}\n\n"
            "✅ Copy the code above\n"
            "⚠️ This code can only be used once!\n"
            "📝 Instructions:\n"
            "1. Open your game\n"
            "2. Go to redeem code section\n"
            "3. Enter this code\n"
            "4. Enjoy your reward!",
            parse_mode='Markdown'
        )
    else:
        await query.message.reply_text("😔 Sorry, no redemption codes available at the moment.")

async def add_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    try:
        # Format: /addcode CODE TYPE
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "⚠️ Please provide both code and type.\n"
                "Format: /addcode YOUR_CODE REWARD_TYPE\n"
                "Example: /addcode GAME123-ABCD-EFGH Premium Skin"
            )
            return
            
        code = args[0]
        reward_type = " ".join(args[1:])
        
        if code in redemption_codes:
            await update.message.reply_text("⚠️ This code already exists!")
            return
            
        redemption_codes[code] = {
            "added_by": user_id,
            "added_on": update.message.date.timestamp(),
            "used_by": None,
            "type": reward_type
        }
        
        await update.message.reply_text(
            f"✅ Code added successfully!\n\n"
            f"📝 Code: `{code}`\n"
            f"🎁 Type: {reward_type}\n"
            f"📊 Total codes available: {len([c for c in redemption_codes.values() if not c['used_by']])}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Error adding code. Please try again.")

async def list_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
        
    if redemption_codes:
        available_codes = [code for code, info in redemption_codes.items() if not info['used_by']]
        used_codes = [code for code, info in redemption_codes.items() if info['used_by']]
        
        message = f"📋 Redemption Codes Status:\n\n"
        
        if available_codes:
            message += "✅ Available Codes:\n"
            for code in available_codes:
                info = redemption_codes[code]
                message += f"• {code}\n  └ Type: {info['type']}\n  └ Added by: {info['added_by']}\n\n"
        
        if used_codes:
            message += "\n❌ Used Codes:\n"
            for code in used_codes:
                info = redemption_codes[code]
                message += f"• {code}\n  └ Type: {info['type']}\n  └ Used by: {info['used_by']}\n\n"
        
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("📋 No redemption codes available.")

async def premium_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    message = (
        "💎 *Premium Rewards Section* 💎\n\n"
        "*Special Items Available:*\n"
        "🏆 Ultra Rare Bundle (Limited)\n"
        "👑 VIP Season Pass 2024\n"
        "💰 2000 Diamonds Pack\n"
        "🎭 Exclusive Character Skins\n"
        "⚔️ Mythic Weapons\n\n"
        "*How to Get:*\n"
        "1. Click 'Get Code Now'\n"
        "2. Receive your unique code\n"
        "3. Redeem in-game\n"
        "4. Enjoy your rewards!\n\n"
        "⚡️ *Note:* Premium codes are limited!"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

def main():
    # Initialize demo codes
    init_demo_codes()
    
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("removeadmin", remove_admin))
    application.add_handler(CommandHandler("addcode", add_code))
    application.add_handler(CommandHandler("listcodes", list_codes))
    application.add_handler(CallbackQueryHandler(get_code, pattern="get_code"))
    application.add_handler(CallbackQueryHandler(how_to_use, pattern="how_to_use"))
    application.add_handler(CallbackQueryHandler(show_rewards, pattern="show_rewards"))
    application.add_handler(CallbackQueryHandler(my_history, pattern="my_history"))
    application.add_handler(CallbackQueryHandler(support, pattern="support"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="back_to_menu"))
    application.add_handler(CallbackQueryHandler(premium_rewards, pattern="premium_rewards"))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main() 
