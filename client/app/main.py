import asyncio
import click

from app.utils import async_register, async_find_matches, async_chat


@click.group()
def cli():
    """Dating App CLI Client"""
    pass

@cli.command()
@click.option("--user-id", prompt="Enter Your User ID", help="Your unique User ID")
@click.option("--name", prompt="Enter Your Name", help="Your name")
@click.option("--description", prompt="Describe Yourself", help="A brief description about yourself")
def register(user_id: str, name: str, description: str):
    asyncio.run(async_register(user_id, name, description))


@cli.command()
@click.option("--user-id", prompt="Enter Your User ID", help="Your User ID")
@click.option("--preferences", prompt="Enter Your Match Preferences", help="Description of your ideal match")
def chat(user_id: str, preferences: str):
    """Find matches and start a chat session with a matched user"""
    click.echo("Finding your matches...")
    match_info = asyncio.run(async_find_matches(user_id, preferences))
    if match_info:
        asyncio.run(async_chat(match_info["chat_id"], user_id))
    else:
        click.echo("No match found. Try adjusting your preferences and try again.")

if __name__ == '__main__':
    cli()