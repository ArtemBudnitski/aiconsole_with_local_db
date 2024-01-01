// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { ChatWSMessage, RequestProcessingFinishedWSMessage } from '@/types/editables/chatWebSocketTypes';
import {
  InitialProjectStatusWSMessage,
  ProjectClosedWSMessage,
  ProjectLoadingWSMessage,
  ProjectOpenedWSMessage,
} from '@/types/projects/projectsWebSocketTypes';
import { AssetsUpdatedWSMessage } from '@/types/editables/editablesWebSocketTypes';
import { SettingsWSMessage } from '../../types/settings/settingsWebSocketTypes';

export type ErrorWSMessage = {
  type: 'ErrorWSMessage';
  error: string;
};

export type NotificationWSMessage = {
  type: 'NotificationWSMessage';
  title: string;
  message: string;
};

export type DebugJSONWSMessage = {
  type: 'DebugJSONWSMessage';
  message: string;
  object: object;
};

export type IncomingWSMessage =
  | ErrorWSMessage
  | NotificationWSMessage
  | DebugJSONWSMessage
  | InitialProjectStatusWSMessage
  | ProjectOpenedWSMessage
  | ProjectClosedWSMessage
  | ProjectLoadingWSMessage
  | AssetsUpdatedWSMessage
  | SettingsWSMessage
  | RequestProcessingFinishedWSMessage
  | ChatWSMessage;
