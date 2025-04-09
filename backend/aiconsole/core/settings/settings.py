# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from functools import lru_cache
from pathlib import Path

from aiconsole.core.settings.settings_notifications import SettingsNotifications
from aiconsole.core.settings.utils.merge_settings_data import merge_settings_data
from aiconsole.core.storage.db_storage import create_storage
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData

_log = logging.getLogger(__name__)

class Settings:
    _storage = None
    _settings_notifications: SettingsNotifications | None = None

    def configure(self, project_path: Path | None = None):
        self.destroy()
        self._storage = create_storage(project_path)
        self._settings_notifications = SettingsNotifications()
        _log.info("Settings configured with database storage")

    def destroy(self):
        self._storage = None
        self._settings_notifications = None

    @property
    def unified_settings(self) -> SettingsData:
        if not self._storage or not self._settings_notifications:
            raise ValueError("Settings not configured")

        # Get all settings from database
        settings_data = SettingsData()
        
        # Merge with any existing settings
        return merge_settings_data(settings_data, self._storage.global_settings, self._storage.project_settings)

    def save(self, settings_data: PartialSettingsData, to_global: bool):
        if not self._storage or not self._settings_notifications:
            raise ValueError("Settings not configured")

        self._settings_notifications.suppress_next_notification()
        
        # Save each setting to database
        for key, value in settings_data.model_dump(exclude_none=True).items():
            self._storage.save_setting(key, str(value), to_global)

# Singleton instance
@lru_cache()
def settings() -> Settings:
    return Settings()
