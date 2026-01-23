import importlib
import sys
import os
import re
import ast
from typing import List, Dict

class ShotgunDataManager:
    def __init__(self):
        try:
            from sg_register import login_to_shotgun
            self.sg = login_to_shotgun()
        except ImportError:
            self.sg = None
            print("Warning: sg_register not found.")

        try:
            from env import env_config
            self.env = env_config
        except ImportError:
            self.env = None

        self._load_env_vars()

    def _load_env_vars(self):
        if self.env:
            try:
                self.HAL_PROJECT_SGID = int(self.env.HAL_PROJECT_SGID or 0)
                self.HAL_PROJECT = self.env.HAL_PROJECT or ""
                self.HAL_USER_LOGIN = self.env.HAL_USER_LOGIN or os.environ.get('USERNAME', 'unknown')
            except:
                self.HAL_PROJECT_SGID = 0
                self.HAL_PROJECT = ""
        else:
            self.HAL_PROJECT_SGID = 0
            self.HAL_PROJECT = ""

    def get_active_projects(self) -> List[Dict]:
        if not self.sg: return []
        try:
            return self.sg.find("Project", [["sg_status", "is", "Active"]], ["name", "id", "code"])
        except: return []

    def set_project_context(self, project_id: int, project_name: str):
        self.HAL_PROJECT_SGID = int(project_id)
        self.HAL_PROJECT = project_name
        print(f"Context Switched: {project_name} ({project_id})")

    def extract_filename_from_url(self, url: str) -> str:
        if not url: return "No Image"
        match = re.search(r'filename%3D%22([^%]+?)%22', url)
        if match:
            return re.sub(r'[^a-zA-Z0-9_-]', '_', match.group(1).split('.')[0])
        return "Unparsable URL"

    def _clean_shotgun_thumbnail_name(self, filename):
        return re.sub(r'(_t(?:_\d+)?)$', '', filename)

    def _categorize_version(self, version_data: Dict):
        entity_type = version_data.get("entity", {}).get("type", "")
        code = version_data.get("code", "").lower()
        if entity_type == "Asset":
            match = re.search(r'(mdl|shd|rig|txt|cgfx-setup|cncpt|assy)', code)
            version_data["category"] = match.group(1) if match else "asset_unknown"
        elif entity_type == "Shot":
            match = re.search(r'(anim|cgfx|comp|layout|lgt|mm|matp|paint|roto|assy)', code)
            version_data["category"] = match.group(1) if match else "shot_unknown"

    def _get_version_number(self, version_code: str) -> int:
        match = re.search(r'_v(\d+)', version_code)
        return int(match.group(1)) if match else 0

    def _get_category_abbreviation(self, category_name: str) -> str:
        return {'characters':'chr', 'environments':'env', 'props':'prp', 'vehicles':'veh', 'cgfx':'cgfx'}.get(category_name.lower(), '')

    def find_files(self, tab_context: str = "", entity_type: str = "") -> List[Dict]:
        if not self.HAL_PROJECT_SGID: return []
        
        # Base Filters
        filters = [
            ["project", "is", {"type": "Project", "id": self.HAL_PROJECT_SGID}],
            ["sg_path_to_geometry", "is_not", None]
        ]

        # --- UPDATED FIELDS TO FETCH DESCRIPTION ---
        fields = [
            "id", "code", "content", "sg_path_to_geometry", "image", "entity",
            "entity.Shot.sg_sequence",
            "entity.Asset.sg_asset_type",
            "created_at",
            "user",
            "description",              # Description on the Version itself
            "entity.Asset.description", # Description on the linked Asset (Common for Assets)
            "entity.Shot.description"   # Description on the linked Shot
        ]

        if tab_context and entity_type:
            try:
                parts = tab_context.split('/')
                if len(parts) == 2:
                    type_part, category_part = parts
                    code_filters = []
                    if entity_type == "Asset":
                        filters.append(["entity", "type_is", "Asset"])
                        abbr = self._get_category_abbreviation(category_part)
                        if abbr: code_filters.append(["code", "contains", abbr])
                        code_filters.append(["code", "contains", type_part])
                    elif entity_type == "Shot":
                        filters.append(["entity", "type_is", "Shot"])
                        seq = self.sg.find_one("Sequence", [["project", "is", {"type": "Project", "id": self.HAL_PROJECT_SGID}], ["code", "is", category_part]], ["id"])
                        if seq: filters.append(["entity.Shot.sg_sequence", "is", seq])
                        code_filters.append(["code", "contains", type_part])

                    if len(code_filters) == 1: filters.append(code_filters[0])
                    elif len(code_filters) > 1: filters.append({"filter_operator": "and", "conditions": code_filters, "filters": code_filters})
            except: pass

        try:
            versions = self.sg.find("Version", filters, fields)
        except Exception as e:
            print(f"Shotgun Query Failed: {e}")
            return []

        for version in versions:
            geo = version.get('sg_path_to_geometry')
            if isinstance(geo, str):
                try: version['sg_path_to_geometry'] = ast.literal_eval(geo) if geo.strip() else []
                except: version['sg_path_to_geometry'] = [geo.strip()]
            elif geo is None: version['sg_path_to_geometry'] = []
            if not isinstance(version['sg_path_to_geometry'], list): version['sg_path_to_geometry'] = [version['sg_path_to_geometry']]

        latest = {}
        for v in versions:
            self._categorize_version(v)
            ent = v.get("entity", {})
            key = (ent.get("type"), ent.get("id"), v.get("category"))
            curr = self._get_version_number(v.get("code", ""))
            exist = self._get_version_number(latest.get(key, {}).get("code", ""))
            if key not in latest or curr > exist: latest[key] = v

        results = list(latest.values())
        for v in results:
            v["image"] = self._clean_shotgun_thumbnail_name(self.extract_filename_from_url(v.get("image", "")))

        return results