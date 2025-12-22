import flet as ft
import requests
import json

# === AAPKA GITHUB LINK ===
GITHUB_URL = "https://raw.githubusercontent.com/kalsoomhaneef-droid/IPTV_Database/refs/heads/main/channels.json"
# =========================

def main(page: ft.Page):
    # === App Settings ===
    page.title = "IPTV Pro Ultra"
    page.theme_mode = "dark"
    page.padding = 10
    page.bgcolor = "#121212"

    # Global Variables
    all_channels = []
    current_cat = "All"

    # === 1. Data Fetch Logic ===
    def load_data():
        try:
            res = requests.get(GITHUB_URL)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, dict): return data.get("channels", [])
                elif isinstance(data, list): return data
        except: pass
        return []

    all_channels = load_data()

    # Categories Logic
    categories = ["All"] + sorted(list(set([c.get("category", "Other") for c in all_channels])))

    # === 2. Video Player ===
    def play_channel(channel):
        url = channel.get("stream_url")
        name = channel.get("name")
        ref = channel.get("referrer", "")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        if ref and len(ref) > 5: headers["Referer"] = ref

        page.views.append(
            ft.View(
                "/player",
                [
                    ft.AppBar(title=ft.Text(name), bgcolor="#000000", leading=ft.IconButton("arrow_back", on_click=lambda _: page.go("/"))),
                    ft.Container(
                        content=ft.Video(
                            expand=True, playlist_mode=False, fill_color="black", aspect_ratio=16/9, autoplay=True,
                            playlist=[ft.VideoMedia(url, http_headers=headers)]
                        ),
                        expand=True, bgcolor="black", alignment=ft.alignment.center
                    )
                ],
                padding=0, bgcolor="black"
            )
        )
        page.update()

    # === 3. Grid View (STATUS & LOGO LOGIC HERE) ===
    grid = ft.GridView(
        expand=True, runs_count=5, max_extent=150, child_aspect_ratio=0.9, spacing=10, run_spacing=10,
    )

    def update_grid(search_text=""):
        grid.controls.clear()
        
        filtered = []
        for c in all_channels:
            if current_cat != "All" and c.get("category") != current_cat: continue
            if search_text.lower() not in c.get("name", "").lower(): continue
            filtered.append(c)

        if not filtered:
            grid.controls.append(ft.Text("No Channels Found", color="red"))
        
        for ch in filtered:
            # --- STATUS COLOR LOGIC ---
            status = ch.get("status", "Unknown")
            status_color = "green" if status == "Working" else "red"
            
            # --- LOGO LOGIC ---
            logo_path = ch.get("logo", "")
            # Agar logo URL hai (http) to Image dikhao, warna Icon
            if logo_path and "http" in logo_path:
                display_icon = ft.Image(src=logo_path, width=50, height=50, fit=ft.ImageFit.CONTAIN, border_radius=5)
            else:
                display_icon = ft.Icon(name="tv", size=40, color="orange")

            # --- CARD UI ---
            card = ft.Container(
                content=ft.Column([
                    # Row: Status Dot (Top Right)
                    ft.Row(
                        [ft.Container(width=12, height=12, bgcolor=status_color, border_radius=6, border=ft.border.all(1, "white"))],
                        alignment="end" # Dot ko right side par rakho
                    ),
                    
                    # Logo Center
                    ft.Container(content=display_icon, padding=5),

                    # Name & Category
                    ft.Text(ch.get("name"), weight="bold", size=13, no_wrap=True, text_align="center"),
                    ft.Text(ch.get("category"), size=10, color="grey", no_wrap=True),
                ], 
                alignment="center", horizontal_alignment="center", spacing=5),
                
                bgcolor="#1E1E1E",
                border_radius=10,
                padding=10,
                on_click=lambda e, x=ch: play_channel(x),
                ink=True
            )
            grid.controls.append(card)
        
        page.update()

    # === 4. UI Layout (Same as before) ===
    def on_search(e): update_grid(e.control.value)
    def on_tab_change(e):
        nonlocal current_cat
        current_cat = categories[e.control.selected_index]
        update_grid()

    search_field = ft.TextField(hint_text="Search...", prefix_icon="search", border_radius=20, bgcolor="#2C2C2C", on_change=on_search, height=40, text_size=14, content_padding=10)

    my_tabs = [ft.Tab(text=cat) for cat in categories]
    tabs_control = ft.Tabs(selected_index=0, animation_duration=300, tabs=my_tabs, on_change=on_tab_change, scrollable=True)

    page.views.append(
        ft.View(
            "/",
            [
                ft.AppBar(title=ft.Text("IPTV Pro", weight="bold"), bgcolor="#1f6aa5", center_title=True, actions=[ft.IconButton("refresh", on_click=lambda _: page.go("/"))]),
                ft.Container(search_field, padding=ft.padding.only(left=10, right=10, top=10)),
                tabs_control,
                ft.Container(grid, expand=True, padding=10)
            ],
            bgcolor="#121212"
        )
    )

    def view_pop(view): page.views.pop(); top_view = page.views[-1]; page.go(top_view.route)
    page.on_route_change = lambda _: page.update(); page.on_view_pop = view_pop
    
    update_grid()
    page.go("/")

ft.app(target=main)