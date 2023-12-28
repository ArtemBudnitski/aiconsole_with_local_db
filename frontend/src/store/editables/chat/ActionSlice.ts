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

import { StateCreator } from 'zustand';

import { AICToolCall } from '@/types/editables/chatTypes';
import { getLastGroup, getLastMessage, getToolCall } from '@/utils/editables/chatUtils';
import { ChatAPI } from '../../../api/api/ChatAPI';
import { ChatStore, useChatStore } from './useChatStore';

import { v4 as uuidv4 } from 'uuid';

const TOOL_CALL_OUTPUT_LIMIT = 20000;

export type RunninngProcess = {
  requestId: string;
  type: 'execute' | 'run' | 'analyse';
  entityId: string;
  abortController: AbortController;
  cleanup: (process: RunninngProcess, aborted: boolean) => void;
};

export type ActionSlice = {
  doExecute: () => Promise<void>;
  doRun: (toolCallId: string) => Promise<void>;
  isAnalysisRunning: () => boolean;
  isExecutionRunning: () => boolean;
  isOngoing(requestId: string): boolean;
  finishProcess: (requestId: string, aborted: boolean) => void;
  stopWork: () => Promise<void>;
  runningProcesses: RunninngProcess[];
  runApiWithProcess: <T>(
    data: T,
    api: (param: T & { request_id: string; signal: AbortSignal }) => Promise<void>,
    type: 'execute' | 'run' | 'analyse',
    id: string,
    cleanup: (process: RunninngProcess, aborted: boolean) => void,
  ) => Promise<void>;
  analysis: {
    agent_id?: string;
    relevant_material_ids?: string[];

    next_step?: string;
    thinking_process?: string;
  };
  doAnalysis: () => Promise<void>;
};

export const createActionSlice: StateCreator<ChatStore, [], [], ActionSlice> = (set, get) => ({
  isOngoing: (requestId: string) => {
    return get().runningProcesses.some((process) => process.requestId === requestId);
  },
  isAnalysisRunning: () => {
    return get().runningProcesses.some((process) => process.type === 'analyse');
  },
  isExecutionRunning: () => {
    return get().runningProcesses.some((process) => process.type === 'execute' || process.type === 'run');
  },

  runApiWithProcess: async <T>(
    data: T,
    api: (param: T & { request_id: string; signal: AbortSignal }) => Promise<void>,
    type: 'execute' | 'run' | 'analyse',
    id: string,
    cleanup: (process: RunninngProcess, aborted: boolean) => void,
  ) => {
    const abortController = new AbortController();
    const requestId = uuidv4();

    set((state) => {
      return {
        runningProcesses: [
          ...state.runningProcesses,
          {
            requestId,
            entityId: id,
            type: type,
            abortController,
            cleanup,
          },
        ],
      };
    });

    return api({ ...data, request_id: requestId, signal: abortController.signal });

    //We can not remove the process from is running here, we need to do it in final websocket message or user cancelaton
  },

  runningProcesses: [],

  doRun: async (toolCallId: string) => {
    const chat = get().chat;

    if (!chat) {
      throw new Error('Chat is not initialized');
    }

    const toolCallLocation = getToolCall(chat, toolCallId);

    if (!toolCallLocation) {
      throw new Error('Message not found');
    }

    const toolCall = toolCallLocation.toolCall;

    const language = toolCall.language;
    const code = toolCall.code;
    const materials_ids = toolCallLocation.group.materials_ids;

    useChatStore.getState().editToolCall((toolCall: AICToolCall) => {
      toolCall.output = '';
      toolCall.is_code_executing = true;
    }, toolCallId);

    get().runApiWithProcess(
      {
        chatId: chat.id,
        tool_call_id: toolCallId,
        language,
        code,
        materials_ids,
      },
      ChatAPI.runCode,
      'run',
      toolCallId,
      (process) => {
        useChatStore.getState().editToolCall((toolCall) => {
          toolCall.is_code_executing = false;
          // Enforce limit on output length, and put info that it was truncated only if limit was reached, truncate so the last part remains (not the first)
          if (toolCall.output && toolCall.output?.length > TOOL_CALL_OUTPUT_LIMIT) {
            toolCall.output = `Output truncated to last ${TOOL_CALL_OUTPUT_LIMIT} characters:\n...\n${toolCall.output?.substring(
              toolCall.output.length - TOOL_CALL_OUTPUT_LIMIT,
            )}`;
          }
        }, process.entityId);

        useChatStore.getState().saveCurrentChatHistory();
      },
    );
  },

  finishProcess(requestId: string, aborted: boolean) {
    set((state) => {
      const finishedProcess = state.runningProcesses.filter((process) => process.requestId === requestId);

      for (const process of finishedProcess) {
        if (aborted) {
          process.abortController.abort();
        }
        process.cleanup(process, aborted);
      }

      return {
        runningProcesses: state.runningProcesses.filter((process) => process.requestId !== requestId),
      };
    });
  },

  /**
   * doExecute expects that the last message group is the one it should be filling in.
   */
  doExecute: async () => {
    const chat = get().chat;

    const lastGroupLocation = getLastGroup(chat);

    if (!lastGroupLocation || !chat) {
      throw new Error('No group or chat found');
    }

    const lastGroup = lastGroupLocation.group;

    //reset analysis
    useChatStore.setState(() => ({
      analysis: {
        agent_id: undefined,
        relevant_material_ids: undefined,
        next_step: undefined,
        thinking_process: undefined,
      },
    }));

    get().runApiWithProcess(
      {
        chat,
        relevant_materials_ids: lastGroup.materials_ids,
        agent_id: lastGroup.agent_id,
      },
      ChatAPI.execute,
      'execute',
      lastGroup.id,
      async () => {
        const chat = useChatStore.getState().chat;
        const messageLocation = getLastMessage(chat);

        //If the message is still empty, remove it

        if (messageLocation) {
          if (messageLocation.message.content === '' && messageLocation.message.tool_calls.length === 0) {
            useChatStore.getState().removeMessageFromGroup(messageLocation.message.id);
          } else {
            useChatStore.getState().editMessage((message) => {
              message.is_streaming = false;

              for (const toolCall of message.tool_calls) {
                toolCall.is_streaming = false;
              }
            }, messageLocation.message.id);
          }

          await useChatStore.getState().saveCurrentChatHistory();
        } else {
          console.warn(`Last Message not found`, chat);
        }
      },
    );
  },
  stopWork: async () => {
    for (const process of get().runningProcesses.slice()) {
      get().finishProcess(process.requestId, true);
    }
  },
  analysis: {
    agent_id: undefined,
    relevant_material_ids: undefined,
    next_step: undefined,
    thinking_process: undefined,
  },
  doAnalysis: async () => {
    try {
      const chat = get().chat;
      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      await get().runApiWithProcess(
        {
          chat: chat,
        },
        ChatAPI.analyse,
        'analyse',
        chat.id,
        () => {
          useChatStore.setState(() => ({
            analysis: {
              agent_id: undefined,
              relevant_material_ids: undefined,
              next_step: undefined,
              thinking_process: undefined,
            },
          }));
        },
      );
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        return;
      } else {
        get().stopWork();
        throw err;
      }
    }
  },
});
