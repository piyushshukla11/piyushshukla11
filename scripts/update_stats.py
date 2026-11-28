#!/usr/bin/env python3
"""
Automated GitHub Profile Stats Updater
Fetches real-time GitHub metrics and updates assets/stats/pixel_github_stats.png
"""

import os
import re
import sys
import json
import urllib.request
import numpy as np
from PIL import Image

USERNAME = "piyushshukla11"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
STATS_IMG_PATH = os.path.join(REPO_ROOT, "assets", "stats", "pixel_github_stats.png")

# --- COLOR DEFINITIONS ---
BG_LEFT = np.array([10, 15, 26, 252], dtype=np.uint8)
BG_BOX = np.array([15, 23, 42, 255], dtype=np.uint8)

COLOR_GREEN = np.array([74, 222, 128, 255], dtype=np.uint8)
COLOR_CYAN = np.array([56, 189, 248, 255], dtype=np.uint8)
COLOR_PINK = np.array([244, 114, 182, 255], dtype=np.uint8)
COLOR_LIGHTBLUE = np.array([147, 197, 253, 255], dtype=np.uint8)
COLOR_ORANGE = np.array([251, 146, 60, 255], dtype=np.uint8)
COLOR_PURPLE = np.array([168, 85, 247, 255], dtype=np.uint8)
COLOR_SUBTEXT = np.array([254, 240, 138, 255], dtype=np.uint8)

# --- 19-ROW BITMAP FONT FOR LEFT STATS ---
# Height 19 rows, defined with '#' and ' '
GLYPH_DEFS = {
    '0': [
        "      #######      ",
        "      #######      ",
        "      #######      ",
        "   ##      #####   ",
        "   ##      #####   ",
        "   ##      #####   ",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "   #####      ##   ",
        "   #####      ##   ",
        "      #######      ",
        "      #######      ",
    ],
    '1': [
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "   #######      ",
        "   #######      ",
        "   #######      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "################",
        "################",
    ],
    '2': [
        "   #############   ",
        "   #############   ",
        "   #############   ",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "           ########",
        "           ########",
        "           ########",
        "      ##########   ",
        "      ##########   ",
        "      ########     ",
        "   ##########      ",
        "   ##########      ",
        "   #####           ",
        "########           ",
        "########           ",
        "###################",
        "###################",
    ],
    '3': [
        "   ################",
        "   ################",
        "   ################",
        "           #####   ",
        "           #####   ",
        "           #####   ",
        "         ####      ",
        "         ####      ",
        "         ####      ",
        "      ##########   ",
        "      ##########   ",
        "              #####",
        "              #####",
        "              #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "   #############   ",
        "   #############   ",
    ],
    '4': [
        "         #######   ",
        "         #######   ",
        "         #######   ",
        "      ##########   ",
        "      ##########   ",
        "      ##########   ",
        "   #####   #####   ",
        "   #####   #####   ",
        "   ###     #####   ",
        "#####      #####   ",
        "#####      #####   ",
        "######     ######  ",
        "###################",
        "###################",
        "           #####   ",
        "           #####   ",
        "           #####   ",
        "           #####   ",
        "           #####   ",
    ],
    '5': [
        "################   ",
        "################   ",
        "################   ",
        "#####              ",
        "#####              ",
        "#####              ",
        "################   ",
        "################   ",
        "###################",
        "              #####",
        "              #####",
        "              #####",
        "              #####",
        "              #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "   #############   ",
        "   #############   ",
    ],
    '6': [
        "      ##########   ",
        "      ##########   ",
        "      ##########   ",
        "   #####           ",
        "   #####           ",
        "   #####           ",
        "#####              ",
        "#####              ",
        "#####              ",
        "################   ",
        "################   ",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "   #############   ",
        "   #############   ",
    ],
    '7': [
        "###################",
        "###################",
        "###################",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "           #####   ",
        "           #####   ",
        "           #####   ",
        "        ######     ",
        "        ######     ",
        "      ########     ",
        "      #####        ",
        "      #####        ",
        "      #####        ",
        "      #####        ",
        "      #####        ",
        "      #####        ",
        "      #####        ",
    ],
    '8': [
        "      ##########   ",
        "      ##########   ",
        "      ##########   ",
        "   #####         ##",
        "   #####         ##",
        "   #####         ##",
        "   ########      ##",
        "   ########      ##",
        "   ########      ##",
        "      ##########   ",
        "      ##########   ",
        "   ################",
        "   ##       #######",
        "   ##       #######",
        "   ##       #######",
        "   ##         #####",
        "   ##         #####",
        "################   ",
        "################   ",
    ],
    '9': [
        "   #############   ",
        "   #############   ",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "#####         #####",
        "   ################",
        "   ################",
        "              #####",
        "              #####",
        "              #####",
        "           #####   ",
        "           #####   ",
        "           #####   ",
        "   ##########      ",
        "   ##########      ",
        "   ##########      ",
    ],
    '+': [
        "                ",
        "                ",
        "                ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "     ######     ",
        "################",
        "################",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "      ####      ",
        "                ",
        "                ",
    ],
    '(': [
        "     #####",
        "     #####",
        "     #####",
        "   ####   ",
        "   ####   ",
        "   ####   ",
        "#####     ",
        "#####     ",
        "#####     ",
        "#####     ",
        "#####     ",
        "#####     ",
        "#####     ",
        "#####     ",
        "#####     ",
        "   ####   ",
        "   ####   ",
        "     #####",
        "     #####",
    ],
    ')': [
        "#####     ",
        "#####     ",
        "#####     ",
        "   #####  ",
        "   #####  ",
        "   #####  ",
        "      ####",
        "      ####",
        "      ####",
        "      ####",
        "      ####",
        "      ####",
        "      ####",
        "      ####",
        "      ####",
        "   #####  ",
        "   #####  ",
        "#####     ",
        "#####     ",
    ],
    '-': [
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "################",
        "################",
        "################",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    ' ': [
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
        "           ",
    ]
}

GLYPHS = {k: np.array([[c == '#' for c in row] for row in rows], dtype=bool) for k, rows in GLYPH_DEFS.items()}

# --- BIG DIGITS FOR 'XX DAYS' (42x40) ---
def make_big_digit(d):
    grid = np.zeros((42, 40), dtype=bool)
    if d in (0, 2, 3, 5, 6, 7, 8, 9):
        grid[0:6, 4:34] = True # top
    if d in (2, 3, 4, 5, 6, 8, 9):
        grid[18:24, 4:34] = True # mid
    if d in (0, 2, 3, 5, 6, 8, 9):
        grid[36:42, 4:34] = True # bot
    if d in (0, 4, 5, 6, 8, 9):
        grid[6:18, 0:10] = True # upper left
    if d in (0, 2, 3, 4, 7, 8, 9):
        grid[6:18, 28:40] = True # upper right
    if d in (0, 2, 6, 8):
        grid[24:36, 0:10] = True # lower left
    if d in (0, 3, 4, 5, 6, 7, 8, 9):
        grid[24:36, 28:40] = True # lower right
    if d == 1:
        grid[0:6, 4:18] = True
        grid[6:36, 14:26] = True
        grid[36:42, 4:36] = True
    return grid

# --- SMALL 14-ROW FONT FOR SUBTEXT ---
def make_small_digit(d):
    grid = np.zeros((14, 14), dtype=bool)
    if d in (0, 2, 3, 5, 6, 7, 8, 9):
        grid[0:2, 2:12] = True
    if d in (2, 3, 4, 5, 6, 8, 9):
        grid[6:8, 2:12] = True
    if d in (0, 2, 3, 5, 6, 8, 9):
        grid[12:14, 2:12] = True
    if d in (0, 4, 5, 6, 8, 9):
        grid[2:6, 0:4] = True
    if d in (0, 1, 2, 3, 4, 7, 8, 9):
        grid[2:6, 10:14] = True
    if d in (0, 2, 6, 8):
        grid[8:12, 0:4] = True
    if d in (0, 1, 3, 4, 5, 6, 7, 8, 9):
        grid[8:12, 10:14] = True
    if d == 1:
        grid[0:2, 4:10] = True
        grid[2:12, 6:10] = True
        grid[12:14, 2:14] = True
    return grid

# Helper to paste glyph
def paste_glyph(target, y, x, glyph, color, bg):
    h, w = glyph.shape
    for r in range(h):
        for c in range(w):
            if glyph[r, c]:
                target[y+r, x+c] = color
            elif bg is not None:
                target[y+r, x+c] = bg

# --- DATA FETCHING ---
def fetch_json(url, token=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Warning fetching {url}: {e}")
        return None

def fetch_streak_stats(username):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://streak-stats.demolab.com/?user={username}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            svg = resp.read().decode("utf-8")
            texts = [t.strip() for t in re.findall(r"<text[^>]*>([^<]+)</text>", svg) if t.strip()]
            if len(texts) >= 8:
                contribs = int(texts[0].replace(",", ""))
                streak = int(texts[5].replace(",", ""))
                dates = texts[4].upper()
                longest = int(texts[6].replace(",", ""))
                return {
                    "contributions": contribs,
                    "streak": streak,
                    "streak_dates": dates,
                    "longest_streak": longest
                }
    except Exception as e:
        print(f"Warning fetching streak stats: {e}")
    return None

def main():
    token = os.environ.get("GITHUB_TOKEN")

    print(f"Fetching GitHub stats for @{USERNAME}...")
    user_data = fetch_json(f"https://api.github.com/users/{USERNAME}", token)
    repos_count = user_data.get("public_repos", 19) if user_data else 19

    prs_data = fetch_json(f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr", token)
    prs_count = prs_data.get("total_count", 44) if prs_data else 44

    issues_data = fetch_json(f"https://api.github.com/search/issues?q=author:{USERNAME}+type:issue", token)
    issues_count = issues_data.get("total_count", 3) if issues_data else 3

    streak_info = fetch_streak_stats(USERNAME)
    if not streak_info:
        print("Using fallback streak defaults")
        streak_info = {
            "contributions": 478,
            "streak": 18,
            "streak_dates": "NOV 11 - NOV 28",
            "longest_streak": 18
        }

    contributions = streak_info["contributions"]
    current_streak = streak_info["streak"]
    streak_dates = streak_info["streak_dates"]
    longest_streak = streak_info["longest_streak"]

    print("--- Stats Collected ---")
    print(f"  Contributions:  {contributions}")
    print(f"  Repositories:   {repos_count}")
    print(f"  Pull Requests:  {prs_count}")
    print(f"  Total Issues:   {issues_count}")
    print(f"  Current Streak: {current_streak} ({streak_dates})")
    print(f"  Longest Streak: {longest_streak}")

    # Load image
    if not os.path.exists(STATS_IMG_PATH):
        print(f"Error: {STATS_IMG_PATH} not found!")
        sys.exit(1)

    im = Image.open(STATS_IMG_PATH).convert("RGBA")
    arr = np.array(im)

    # 1. TOTAL COMMITS: f"{contributions}+"
    commits_str = f"{contributions}+"
    arr[158:177, 70:200] = BG_LEFT
    curr_x = 70
    for char in commits_str:
        if char in GLYPHS:
            g = GLYPHS[char]
            paste_glyph(arr, 158, curr_x, g, COLOR_GREEN, BG_LEFT)
            curr_x += g.shape[1] + (3 if char == '1' else 6)

    # 2. REPOSITORIES: f"{repos_count}"
    repos_str = str(repos_count)
    arr[258:277, 70:150] = BG_LEFT
    curr_x = 73 if repos_str.startswith('1') else 70
    for char in repos_str:
        if char in GLYPHS:
            g = GLYPHS[char]
            paste_glyph(arr, 258, curr_x, g, COLOR_CYAN, BG_LEFT)
            curr_x += g.shape[1] + (3 if char == '1' else 6)

    # 3. PULL REQUESTS: f"{prs_count}"
    prs_str = str(prs_count)
    arr[358:377, 70:150] = BG_LEFT
    curr_x = 73 if prs_str.startswith('1') else 70
    for char in prs_str:
        if char in GLYPHS:
            g = GLYPHS[char]
            paste_glyph(arr, 358, curr_x, g, COLOR_PINK, BG_LEFT)
            curr_x += g.shape[1] + (3 if char == '1' else 6)

    # 4. TOTAL ISSUES: f"{issues_count}"
    issues_str = str(issues_count)
    arr[458:477, 70:150] = BG_LEFT
    curr_x = 73 if issues_str.startswith('1') else 70
    for char in issues_str:
        if char in GLYPHS:
            g = GLYPHS[char]
            paste_glyph(arr, 458, curr_x, g, np.array([234, 179, 8, 255], dtype=np.uint8), BG_LEFT)
            curr_x += g.shape[1] + (3 if char == '1' else 6)

    # 5. CONTRIBUTIONS: f"{contributions} (2025-26)"
    contrib_str = f"{contributions} (2025-26)"
    arr[558:577, 70:360] = BG_LEFT
    curr_x = 70
    for char in contrib_str:
        if char in GLYPHS:
            g = GLYPHS[char]
            paste_glyph(arr, 558, curr_x, g, COLOR_LIGHTBLUE, BG_LEFT)
            curr_x += g.shape[1] + (3 if char == '1' else (12 if char == ' ' else 6))

    # 6. BIG STREAK: ORANGE (CURRENT STREAK) & PURPLE (LONGEST STREAK)
    # Clear both digit regions (x: 915..1015)
    arr[185:227, 915:1015] = BG_BOX
    arr[370:412, 915:1015] = BG_BOX

    # Current streak digits
    c_str = str(current_streak)
    if len(c_str) == 1:
        c_str = f"0{c_str}"
    d1 = int(c_str[-2])
    d2 = int(c_str[-1])
    paste_glyph(arr, 185, 922, make_big_digit(d1), COLOR_ORANGE, BG_BOX)
    paste_glyph(arr, 185, 965, make_big_digit(d2), COLOR_ORANGE, BG_BOX)

    # Longest streak digits
    l_str = str(longest_streak)
    if len(l_str) == 1:
        l_str = f"0{l_str}"
    ld1 = int(l_str[-2])
    ld2 = int(l_str[-1])
    paste_glyph(arr, 370, 922, make_big_digit(ld1), COLOR_PURPLE, BG_BOX)
    paste_glyph(arr, 370, 965, make_big_digit(ld2), COLOR_PURPLE, BG_BOX)

    # 7. SUBTEXT DATE UPDATE (e.g. "NOV 28")
    # In streak_dates, e.g. "NOV 11 - NOV 28"
    parts = streak_dates.split("-")
    if len(parts) == 2:
        end_part = parts[1].strip() # e.g. "NOV 28"
        # Extract last 2 digits
        end_digits = re.findall(r"\d+", end_part)
        if end_digits:
            day_num = end_digits[-1]
            if len(day_num) == 1:
                day_num = f"0{day_num}"
            s_d1 = int(day_num[0])
            s_d2 = int(day_num[1])
            # Clear 2 digits in subtext (x: 1122..1156, y: 245..259)
            arr[245:259, 1122:1158] = BG_BOX
            paste_glyph(arr, 245, 1124, make_small_digit(s_d1), COLOR_SUBTEXT, BG_BOX)
            paste_glyph(arr, 245, 1141, make_small_digit(s_d2), COLOR_SUBTEXT, BG_BOX)

    # Save output
    out_im = Image.fromarray(arr)
    out_im.save(STATS_IMG_PATH)
    print(f"Successfully updated {STATS_IMG_PATH}")

if __name__ == "__main__":
    main()
