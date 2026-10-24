import json
import pathlib
from typing import Any, List


class MemoryManager:

    def __init__(self, filename: str = "recipe_history.json"):
        # Määritetään polku 2 kansiota ylemmäs / data / filename
        self.data_dir = (
            pathlib.Path(__file__).resolve().parent.parent.parent / "data"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / filename

    def load_memory(self) -> List[dict]:
        """Lataa aiemmat reseptit/muistin JSON-tiedostosta."""
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []

        try:
            content = self.file_path.read_text(encoding="utf-8")
            data = json.loads(content)
            return data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, Exception) as e:
            print(f"Virhe muistia ladattaessa: {e}")
            return []

    def save_to_memory(self, item: dict):
        """Lisää uuden reseptin/muistisoluun ja tallentaa sen."""
        memory_data = self.load_memory()
        memory_data.append(item)

        self.file_path.write_text(
            json.dumps(memory_data, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_recent_summary(self, limit: int = 3) -> str:
        """Palauttaa tiivistelmän viimeisimmistä resepteistä promptiin lisättäväksi."""
        history = self.load_memory()
        if not history:
            return "Ei aiempaa historiaa."

        # Otetaan viimeiset N reseptiä
        recent = history[-limit:]
        summaries = []
        for idx, item in enumerate(recent, 1):
            msg = item.get("message", "Resepti")
            ingredients = ", ".join(item.get("ingredients", [])[:3])
            summaries.append(f"{idx}. {msg} (Raaka-aineita: {ingredients}...)")

        return "\n".join(summaries)

    def save_to_cookbook(self, recipe_data: dict, filename: str = "saved_cookbook.json"):
        """Tallentaa reseptin erilliseen Cookbook-tiedostoon."""
        cookbook_path = self.data_dir / filename
        
        saved_list = []
        if cookbook_path.exists() and cookbook_path.stat().st_size > 0:
            try:
                content = cookbook_path.read_text(encoding="utf-8")
                data = json.loads(content)
                saved_list = data if isinstance(data, list) else [data]
            except (json.JSONDecodeError, Exception):
                saved_list = []
                
        if recipe_data not in saved_list:
            saved_list.append(recipe_data)
            cookbook_path.write_text(
                json.dumps(saved_list, indent=4, ensure_ascii=False),
                encoding="utf-8"
            )
            return True
        return False

    def load_cookbook(self, filename: str = "saved_cookbook.json") -> List[dict]:
        """Lataa tallennetut reseptit Cookbook-tiedostosta."""
        cookbook_path = self.data_dir / filename
        if not cookbook_path.exists() or cookbook_path.stat().st_size == 0:
            return []
        try:
            content = cookbook_path.read_text(encoding="utf-8")
            data = json.loads(content)
            return data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, Exception):
            return []

    def save_cookbook_all(self, recipes: List[dict], filename: str = "saved_cookbook.json"):
        """Tallentaa koko Cookbook-listan kerralla tiedostoon (käytetään esim. poistossa)."""
        cookbook_path = self.data_dir / filename
        try:
            cookbook_path.write_text(
                json.dumps(recipes, indent=4, ensure_ascii=False),
                encoding="utf-8"
            )
            return True
        except Exception as e:
            print(f"Virhe cookbookia tallennettaessa: {e}")
            return False