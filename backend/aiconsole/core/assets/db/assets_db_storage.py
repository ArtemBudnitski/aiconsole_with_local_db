import logging
from pathlib import Path
from typing import Optional, List

from aiconsole.core.assets.types import Asset
from aiconsole.core.assets.assets_storage import AssetsStorage
from aiconsole.core.db.operations import DatabaseOperations

_log = logging.getLogger(__name__)

class AssetsDBStorage(AssetsStorage):
    def __init__(self, project_path: Optional[Path] = None):
        self._project_path = project_path
        self._project_id = str(project_path) if project_path else None

    def change_project(self, project_path: Optional[Path] = None):
        self._project_path = project_path
        self._project_id = str(project_path) if project_path else None

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        return DatabaseOperations.get_asset(asset_id, self._project_id)

    def get_assets(self, asset_type: str) -> List[Asset]:
        # Get all assets of a specific type for the current project
        assets = []
        for asset in DatabaseOperations.get_all_assets(self._project_id):
            if asset.type == asset_type:
                assets.append(asset)
        return assets

    def save_asset(self, asset: Asset):
        DatabaseOperations.save_asset(asset)

    def delete_asset(self, asset_id: str):
        DatabaseOperations.delete_asset(asset_id, self._project_id)

    def get_asset_files(self, asset_id: str) -> List[str]:
        return DatabaseOperations.get_asset_files(asset_id)

    def save_asset_file(self, asset_id: str, file_path: str):
        DatabaseOperations.save_asset_file(asset_id, file_path) 