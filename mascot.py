"""mascot.py - Tara the Turtle, ShopImpact's friendly guide (inline SVG)."""

# Mouth shapes for each mood (never sad or guilt-inducing, just curious/cheerful)
_MOUTHS = {
    "happy": '<path d="M 112 78 Q 124 90 136 78" stroke="#2F3E36" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "cheer": '<path d="M 110 76 Q 124 98 138 76 Z" fill="#E88D8D" stroke="#2F3E36" stroke-width="3"/>',
    "think": '<path d="M 114 82 L 134 82" stroke="#2F3E36" stroke-width="3" stroke-linecap="round"/>',
}


def tara_svg(mood="happy", size=150):
    mouth = _MOUTHS.get(mood, _MOUTHS["happy"])
    sparkle = ""
    if mood == "cheer":
        sparkle = ('<text x="150" y="30" font-size="22">\u2728</text>'
                   '<text x="20" y="40" font-size="18">\u2728</text>')
    return f"""
<svg viewBox="0 0 180 150" width="{size}" height="{size * 150 // 180}" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="90" cy="138" rx="62" ry="7" fill="#000" opacity=".08"/>
  <ellipse cx="52" cy="122" rx="14" ry="10" fill="#8FB98F"/>
  <ellipse cx="128" cy="122" rx="14" ry="10" fill="#8FB98F"/>
  <ellipse cx="90" cy="95" rx="62" ry="42" fill="#6FA878" stroke="#3F6B4F" stroke-width="4"/>
  <path d="M 62 95 L 76 72 L 104 72 L 118 95 L 104 118 L 76 118 Z" fill="#A8D3AE" stroke="#3F6B4F" stroke-width="3"/>
  <circle cx="40" cy="92" r="6" fill="#A8D3AE" opacity=".8"/>
  <circle cx="140" cy="92" r="6" fill="#A8D3AE" opacity=".8"/>
  <circle cx="124" cy="62" r="24" fill="#8FB98F" stroke="#3F6B4F" stroke-width="4"/>
  <circle cx="116" cy="56" r="5" fill="#fff"/><circle cx="117" cy="57" r="2.6" fill="#2F3E36"/>
  <circle cx="134" cy="56" r="5" fill="#fff"/><circle cx="135" cy="57" r="2.6" fill="#2F3E36"/>
  <circle cx="108" cy="70" r="4" fill="#F2B6A8" opacity=".8"/>
  <circle cx="140" cy="70" r="4" fill="#F2B6A8" opacity=".8"/>
  {mouth}
  <path d="M 112 40 Q 124 22 136 40" stroke="#3F6B4F" stroke-width="3" fill="none"/>
  <ellipse cx="124" cy="30" rx="9" ry="5" fill="#BFE3C0" stroke="#3F6B4F" stroke-width="2"/>
  {sparkle}
</svg>"""
