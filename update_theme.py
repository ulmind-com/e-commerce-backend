import re

file_path = r"c:\projects\ecommerce_platform\frontend\src\pages\Checkout.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace colors
content = content.replace("bg-[#2874f0]", "bg-primary")
content = content.replace("text-[#2874f0]", "text-primary")
content = content.replace("border-[#2874f0]", "border-primary")
content = content.replace("accent-[#2874f0]", "accent-primary")
content = content.replace("bg-[#fb641b]", "bg-primary") # Or amber-500, but primary is safer
content = content.replace("hover:bg-blue-600", "hover:bg-primary-600")
content = content.replace("bg-blue-50/30", "bg-primary/5")
content = content.replace("bg-blue-50/50", "bg-primary/10")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Colors updated successfully.")
