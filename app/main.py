from app.ui import build_ui, THEME, CSS

def main() -> None:
    """Entry point script for launching the application."""
    demo = build_ui()
    demo.launch(theme=THEME, css=CSS, footer_links=[])

if __name__ == "__main__":
    main()
