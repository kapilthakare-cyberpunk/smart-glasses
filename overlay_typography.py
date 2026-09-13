#!/usr/bin/env python3
"""
Overlay typography and vector icons on the Meta AI glasses image.
Creates a sophisticated feature-callout overlay with 4 features.

Features:
  1. Hands-free capture       — microphone icon
  2. Ask your AI glasses      — Meta AI blue ring
  3. Tune in without tuning   — speaker / audio waves
  4. Power through your day   — battery outline

Layout: 2×2 grid of circular icon badges with typography labels,
positioned in the lower portion of the image over a dark vignette backdrop.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import shutil
import os
import math

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_IMAGE = "/Users/kapilthakare/Projects/smart-glasses/meta-ai-glasses - 1.jpeg"
OUTPUT_IMAGE = "/Users/kapilthakare/Projects/smart-glasses/meta-ai-glasses-featured.jpg"
ICONS_DIR = "/Users/kapilthakare/Projects/smart-glasses/assets/icons"

# ── Colour palette ────────────────────────────────────────────────────────
META_BLUE   = (0, 128, 255)     # #0080FF
META_RED    = (228, 64, 80)     # #E44050
DARK_NAVY   = (15, 23, 42)      # #0F172A
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
BADGE_BG    = (255, 255, 255)
BADGE_BORDER = (229, 231, 235)  # #E5E7EB
BACKDROP_BG = (10, 10, 15, 200)  # near-black, ~78 % opacity
TEXT_SHADOW = (0, 0, 0, 160)

# ── Font configuration ────────────────────────────────────────────────────
FONT_PATH = "/System/Library/Fonts/Avenir Next.ttc"
# index 0 = Bold, index 2 = DemiBold, index 5 = Medium, index 7 = Regular

font_bold_30 = ImageFont.truetype(FONT_PATH, 30, index=0)   # feature titles (1 line)
font_bold_24 = ImageFont.truetype(FONT_PATH, 24, index=0)   # feature titles (2-line)
font_medium_18 = ImageFont.truetype(FONT_PATH, 18, index=5)  # sub-label
font_regular_16 = ImageFont.truetype(FONT_PATH, 16, index=7)  # body

# ── Feature data ──────────────────────────────────────────────────────────
features = [
    {"title": "Hands-free capture",        "icon": "microphone"},
    {"title": "Ask your AI glasses anything", "icon": "meta-ai-ring"},
    {"title": "Tune in without tuning out", "icon": "speaker"},
    {"title": "Power through your day",    "icon": "battery"},
]

# ── Layout constants ──────────────────────────────────────────────────────
BADGE_DIAMETER = 72      # px
ICON_SIZE = 50           # px (rendered icon shrunk to this)
TEXT_GAP = 20            # px gap between badge bottom and text
LINE_HEIGHT = 32         # px per text line

# ── Text wrapping helper ──────────────────────────────────────────────────

def measure_text(draw, text, font):
    """Return (width, height, top_offset) for *text* drawn with *font*."""
    bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
    return bbox[2] - bbox[0], bbox[3] - bbox[1], -bbox[1]  # width, height, ascender

def wrap_text(draw, text, font, max_width):
    """Word-wrap *text* so each line fits within *max_width* pixels."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        trial = f"{current} {w}".strip()
        w_px, _, _ = measure_text(draw, trial, font)
        if w_px <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# ── Main compositing ────────────────────────────────────────────────────────

def main():
    # 1 ── Copy the base image ───────────────────────────────────────────────
    shutil.copy2(BASE_IMAGE, OUTPUT_IMAGE)
    print(f"[1/5] Copied  {BASE_IMAGE}  →  {OUTPUT_IMAGE}")

    # 2 ── Load base image ───────────────────────────────────────────────────
    base = Image.open(OUTPUT_IMAGE).convert("RGBA")
    W, H = base.size
    print(f"[2/5] Base image  {W}×{H}")

    # 3 ── Compute positions (2×2 grid in lower-third) ────────────────────
    col1_x = int(W * 0.26)   # ~464
    col2_x = int(W * 0.74)   # ~1320
    row1_y = int(H * 0.63)   # ~703
    row2_y = int(H * 0.79)   # ~881

    positions = [
        (col1_x, row1_y),   # Hands-free capture
        (col2_x, row1_y),   # Ask your AI glasses
        (col1_x, row2_y),   # Tune in without tuning out
        (col2_x, row2_y),   # Power through your day
    ]

    # 4 ── Create overlay canvas ───────────────────────────────────────────
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 4a ── Bottom vignette gradient for contrast ──────────────────────────
    vignetti_top = int(H * 0.56)   # ~625
    vignetti_bottom = H
    vignetti_height = vignetti_bottom - vignetti_top
    steps = 60
    for i in range(steps + 1):
        y = vignetti_top + int(i * vignetti_height / steps)
        # Ease-in alpha: starts at 0, ends at full
        progress = (i / steps) ** 1.5
        alpha = int(70 * progress)
        next_y = vignetti_top + int((i + 1) * vignetti_height / steps)
        if y != next_y:
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # 4b ── Backdrop rounded rectangle behind the 2×2 grid ─────────────────
    backdrop_pad_x = 50
    backdrop_pad_y = 30
    # Estimate total height needed: badges + text + sub-labels
    max_text_lines = 2 * LINE_HEIGHT + 12 + 24  # 2 lines + gap + sub-label
    bx1 = col1_x - BADGE_DIAMETER // 2 - backdrop_pad_x
    by1 = row1_y - BADGE_DIAMETER // 2 - backdrop_pad_y
    bx2 = col2_x + BADGE_DIAMETER // 2 + backdrop_pad_x
    by2 = row2_y + BADGE_DIAMETER // 2 + TEXT_GAP + max_text_lines + backdrop_pad_y
    draw.rounded_rectangle(
        [bx1, by1, bx2, by2],
        radius=24,
        fill=BACKDROP_BG,
    )
    # Subtle inner shadow (top edge darker)
    for i in range(12):
        y = by1 + i
        a = int(40 * (1 - i / 12))
        draw.line([(bx1, y), (bx2, y)], fill=(0, 0, 0, a))

    # 4c ── Blurred outer glow behind backdrop (sophisticated depth) ──────
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_pad = 12
    glow_rect = [bx1 - glow_pad, by1 - glow_pad, bx2 + glow_pad, by2 + glow_pad]
    glow_draw.rounded_rectangle(glow_rect, radius=28, fill=(0, 100, 255, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    overlay.alpha_composite(glow, (0, 0))

    # 5 ── Draw badges, icons, and text ────────────────────────────────────
    for i, feat in enumerate(features):
        cx, cy = positions[i]
        title = feat["title"]
        icon_file = f"{ICONS_DIR}/{feat['icon']}.png"

        # 5a ── Drop shadow for badge (offset, blurred) ───────────────────
        shadow_ellipse = [
            cx - BADGE_DIAMETER // 2,
            cy - BADGE_DIAMETER // 2 + 3,
            cx + BADGE_DIAMETER // 2,
            cy + BADGE_DIAMETER // 2 + 3,
        ]
        # Draw shadow as a separate pass for blur
        shadow_img = Image.new("RGBA", (BADGE_DIAMETER + 10, BADGE_DIAMETER + 10), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        sx = BADGE_DIAMETER // 2 + 5
        sy = BADGE_DIAMETER // 2 + 5
        shadow_draw.ellipse(
            [sx - BADGE_DIAMETER // 2, sy - BADGE_DIAMETER // 2,
             sx + BADGE_DIAMETER // 2, sy + BADGE_DIAMETER // 2],
            fill=(0, 0, 0, 70),
        )
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(3))
        overlay.paste(shadow_img, (int(cx - BADGE_DIAMETER // 2 - 5), int(cy - BADGE_DIAMETER // 2 - 5 + 3)), shadow_img)

        # 5b ── Badge background (white circle) ─────────────────────────────
        badge_ellipse = [
            cx - BADGE_DIAMETER // 2, cy - BADGE_DIAMETER // 2,
            cx + BADGE_DIAMETER // 2, cy + BADGE_DIAMETER // 2,
        ]
        draw.ellipse(badge_ellipse, fill=BADGE_BG)
        draw.ellipse(badge_ellipse, outline=BADGE_BORDER, width=1)

        # 5c ── Icon ───────────────────────────────────────────────────────
        icon_img = Image.open(icon_file).convert("RGBA")
        icon_img = icon_img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
        icon_pos = (cx - ICON_SIZE // 2, cy - ICON_SIZE // 2)
        overlay.paste(icon_img, icon_pos, icon_img)

        # 5d ── Typography label ───────────────────────────────────────────
        # Column width = half the distance between the two column centres,
        # minus a safety margin so text never touches the backdrop edge.
        col_width = (col2_x - col1_x) // 2 - 40

        # Choose font: use 30px if the full title fits on one line, else 24px
        font = font_bold_30
        w_full, _, _ = measure_text(draw, title, font)
        if w_full > col_width:
            font = font_bold_24
            w_full, _, _ = measure_text(draw, title, font)

        lines = wrap_text(draw, title, font, col_width)
        # If wrapping was needed and we have more than 2 lines, shrink font
        if len(lines) > 2:
            font = font_bold_24
            lines = wrap_text(draw, title, font, col_width)

        text_start_y = cy + BADGE_DIAMETER // 2 + TEXT_GAP
        for line in lines:
            tw, th, asc = measure_text(draw, line, font)
            tx = cx - tw // 2
            ty = text_start_y + asc
            # Text shadow for readability on the photo
            draw.text((tx + 1, ty + 1), line, font=font, fill=(0, 0, 0, 140), anchor="lt")
            # Actual text
            draw.text((tx, ty), line, font=font, fill=WHITE, anchor="lt")
            text_start_y += LINE_HEIGHT

        # 5e ── Sub-label (icon description in small text) ──────────────────
        sub_labels = {
            "microphone": "Voice command",
            "meta-ai-ring": "AI assistant",
            "speaker": "Open-ear audio",
            "battery": "All-day power",
        }
        sub = sub_labels.get(feat["icon"], "")
        if sub:
            sw, sh, sasc = measure_text(draw, sub, font_regular_16)
            sx_pos = cx - sw // 2
            sy_pos = text_start_y + sasc
            # Text shadow
            draw.text((sx_pos + 1, sy_pos + 1), sub, font=font_regular_16,
                      fill=(0, 0, 0, 120), anchor="lt")
            draw.text((sx_pos, sy_pos), sub, font=font_regular_16,
                      fill=(191, 191, 191), anchor="lt")

    # 6 ── Optional: Meta AI accent stripe ─────────────────────────────────
    # Subtle blue gradient line above the feature grid
    accent_y = int(H * 0.60)
    for i in range(3):
        w = W - 40 - i * 40
        x = 20 + i * 20
        alpha = 60 - i * 15
        draw.line([(x, accent_y), (x + w, accent_y)], fill=(*META_BLUE[:3], alpha), width=4)

    # ── Composite and save ────────────────────────────────────────────────
    result = Image.alpha_composite(base, overlay).convert("RGB")
    # Sharpen slightly for crisp typography
    result = result.filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=2))
    result.save(OUTPUT_IMAGE, "JPEG", quality=95, optimize=True)
    file_size = os.path.getsize(OUTPUT_IMAGE) / 1024
    print(f"[5/5] Saved  {OUTPUT_IMAGE}  ({file_size:.0f} KB)")
    print(f"\nFeatures overlaid:")
    for feat in features:
        print(f"  • {feat['title']}  ←  {feat['icon']}")


if __name__ == "__main__":
    main()
