#!/usr/bin/env python3
"""
Simple Python script to connect to Cursor CLI
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def find_cursor_cli():
    """Find Cursor CLI (installed as 'agent' or 'cursor-agent')"""
    # Try common paths and names
    paths_to_try = [
        "agent",  # Most common name
        "cursor-agent",  # Alternative name
        os.path.expanduser("~/.local/bin/agent"),
        os.path.expanduser("~/.local/bin/cursor-agent"),
        "/Applications/Cursor.app/Contents/Resources/app/bin/agent",
    ]
    
    for path in paths_to_try:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        except Exception:
            continue
    
    return None


def is_authenticated():
    """
    Check if authentication credentials are available
    
    Returns:
        True if API key is set, False otherwise
    """
    # Check for API key in environment variable
    return bool(os.getenv("CURSOR_API_KEY"))


def run_login(cursor_cmd):
    """
    Run the login command for Cursor CLI
    
    Args:
        cursor_cmd: Path to the cursor CLI command
    
    Returns:
        True if login appears successful, False otherwise
    """
    print(f"\n🔐 Attempting to login to Cursor CLI...")
    print(f"   Running: {cursor_cmd} login")
    print("   (This may open a browser or prompt for credentials)\n")
    
    try:
        # Run login interactively (not in background, so user can interact)
        result = subprocess.run(
            [cursor_cmd, "login"],
            timeout=120  # 2 minute timeout for login
        )
        
        if result.returncode == 0:
            print("\n✅ Login successful!")
            return True
        else:
            print("\n⚠️  Login may have failed. Please try manually:")
            print(f"   {cursor_cmd} login")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⚠️  Login timed out. Please try manually:")
        print(f"   {cursor_cmd} login")
        return False
    except Exception as e:
        print(f"\n❌ Error during login: {e}")
        print(f"   Please try manually: {cursor_cmd} login")
        return False


def connect_cursor(prompt, cwd=None, timeout=300):
    """
    Connect to Cursor CLI and send a prompt
    
    Args:
        prompt: The prompt/question to send to Cursor
        cwd: Working directory (defaults to current directory)
        timeout: Timeout in seconds (default: 300 = 5 minutes)
    
    Returns:
        Response from Cursor CLI or None if failed
    """
    cursor_cmd = find_cursor_cli()
    
    if not cursor_cmd:
        print("❌ Cursor CLI not found!")
        print("\n📝 To install Cursor CLI:")
        print("   1. Install Cursor IDE from https://cursor.sh")
        print("   2. Open Cursor → Settings → Extensions → CLI Tools")
        print("   3. Click 'Install CLI Tools'")
        print("   4. Or run: curl https://cursor.com/install -fsS | bash")
        return None
    
    # Note: We'll check authentication when we make the actual call
    # This allows users who logged in via 'agent login' to still use the script
    
    try:
        timeout_minutes = timeout // 60
        print(f"📤 Sending prompt to Cursor CLI (timeout: {timeout_minutes} min)...")
        print(f"   Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")
        
        # Call Cursor CLI with -p flag for non-interactive mode
        result = subprocess.run(
            [cursor_cmd, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or os.getcwd()
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            print("✅ Received response from Cursor CLI")
            return response
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            
            # Check for authentication errors
            if "Authentication required" in error_msg or "login" in error_msg.lower():
                print(f"❌ Authentication error:")
                print(f"   {error_msg}")
                print("\n📝 To authenticate, you can:")
                print(f"   1. Run: {cursor_cmd} login")
                print("   2. Or set: export CURSOR_API_KEY='your-api-key'")
                print("   3. Or run this script with --login flag to attempt automatic login")
                return None
            else:
                print(f"❌ Cursor CLI returned error:")
                print(f"   {error_msg[:500]}")
                return None
            
    except FileNotFoundError:
        print(f"❌ Cursor CLI command not found at: {cursor_cmd}")
        return None
    except subprocess.TimeoutExpired:
        print(f"❌ Cursor CLI timed out (>{timeout // 60} minutes)")
        return None
    except Exception as e:
        print(f"❌ Error connecting to Cursor CLI: {e}")
        return None


def main():
    """Main function - example usage"""
    parser = argparse.ArgumentParser(
        description="Connect to Cursor CLI and send prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cursor_cli_connect.py "Write a Python function"
  python cursor_cli_connect.py --login
  python cursor_cli_connect.py --login "Your prompt here"
        """
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Write a simple Python function that adds two numbers",
        help="The prompt to send to Cursor CLI"
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Attempt to login to Cursor CLI before sending prompt"
    )
    
    args = parser.parse_args()
    
    print("🔌 Cursor CLI Connection Script\n")
    
    # Check if Cursor CLI is available
    cursor_cmd = find_cursor_cli()
    if not cursor_cmd:
        print("❌ Cursor CLI not found!")
        print("\n📝 To install Cursor CLI:")
        print("   1. Install Cursor IDE from https://cursor.sh")
        print("   2. Open Cursor → Settings → Extensions → CLI Tools")
        print("   3. Click 'Install CLI Tools'")
        print("   4. Or run: curl https://cursor.com/install -fsS | bash")
        sys.exit(1)
    
    print(f"✅ Found Cursor CLI at: {cursor_cmd}")
    
    # Handle login if requested
    if args.login:
        if not run_login(cursor_cmd):
            print("\n⚠️  Continuing anyway...")
        print()  # Add spacing
    
    # Connect and get response
    response = connect_cursor(args.prompt)
    
    if response:
        print("\n" + "="*60)
        print("📥 Response from Cursor CLI:")
        print("="*60)
        print(response)
        print("="*60)
    else:
        print("\n❌ Failed to get response from Cursor CLI")
        if not args.login:
            print("\n💡 Tip: Try running with --login flag:")
            print(f"   python cursor_cli_connect.py --login \"{args.prompt}\"")
        sys.exit(1)


if __name__ == "__main__":
    main()
