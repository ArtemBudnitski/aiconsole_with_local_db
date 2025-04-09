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

from fastapi import APIRouter

from aiconsole.api.endpoints import (
    agents,
    chats,
    code,
    materials,
    projects,
    settings,
    tools,
    websockets,
)

app_router = APIRouter()

app_router.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app_router.include_router(chats.router, prefix="/api/chats", tags=["chats"])
app_router.include_router(code.router, prefix="/api/code", tags=["code"])
app_router.include_router(materials.router, prefix="/api/materials", tags=["materials"])
app_router.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app_router.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app_router.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])
