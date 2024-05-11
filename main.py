#PyPI API endpoint for package namesimport random
import re
import httpx
from telethon import TelegramClient, events
from telethon.tl.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize the Telethon client
api_id = 12590615
api_hash = '048a88c8c193063ab850327dbbc25ca5'
bot_token = '6504739506:AAFNV-cdh4aVBRMCHbw1JgV5x7jwC4MCc1s'
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# Define the PyPI API endpoint for package names
PYPI_API_PACKAGES_URL = "https://pypi.org/simple/"

# Define a command handler for getting information about a random package
@client.on(events.NewMessage(pattern='/random_package'))
async def get_random_package_info(event):
    async with httpx.AsyncClient() as client_httpx:
        # Make a request to the PyPI API to get a list of packages
        response = await client_httpx.get(PYPI_API_PACKAGES_URL)
        if response.status_code == 200:
            # Parse the response to extract package names
            package_names = re.findall(r'<a href="[^"]+">([^<]+)</a>', response.text)

            # Select a random package from the list of package names
            package_name = random.choice(package_names)

            # Make a request to the PyPI API to get information about the package
            response = await client_httpx.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                # Parse the response to get package information
                package_info = response.json()["info"]
                version = package_info["version"]
                summary = package_info["summary"]
                homepage = package_info["home_page"]
                dependencies = package_info.get("requires_dist", [])
                download_count = package_info.get("downloads", {}).get("last_month", 0)
                license = package_info.get("license", "Unknown")
                author = package_info.get("author", "Unknown")
                release_date = package_info.get("release_date", "Unknown")
                project_urls = package_info.get("project_urls", {})

                # Generate the PyPI URL for the package
                pypi_url = f"https://pypi.org/project/{package_name}/"

                # Create a reply message with the package information and a button
                reply_message = (
                    f"📦 **Package:** {package_name}\n"
                    f"📌 **Version:** {version}\n"
                    f"📄 **Summary:** {summary}\n"
                    f"🔗 **Homepage:** {homepage}\n"
                    f"🔗 **Dependencies:** {', '.join(dependencies)}\n"
                    f"⬇️ **Download Count (Last Month):** {download_count}\n"
                    f"📝 **License:** {license}\n"
                    f"👤 **Author:** {author}\n"
                    f"📅 **Release Date:** {release_date}\n"
                )

                # Add project URLs to the message
                if project_urls:
                    for key, value in project_urls.items():
                        reply_message += f"🔗 **{key.capitalize()} URL:** {value}\n"

                # Add a button to direct the user to the PyPI page for the package
                await event.respond(
                    reply_message,
                    parse_mode="markdown",
                    buttons=[[InlineKeyboardButton("View on PyPI", url=pypi_url)]],
                )
            else:
                # Inform the user that the package was not found
                await event.respond("Package not found.")
        else:
            # Inform the user that the list of packages could not be fetched
            await event.respond("Failed to fetch the list of packages.")

# Run the client
client.run_until_disconnected()
