def generate_slug(name: str) -> str:
        return name.strip().lower().replace(" ", "-")